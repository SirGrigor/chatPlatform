import os
from pathlib import Path
from typing import Dict

from llama_index.agent.openai import OpenAIAgent
from llama_index.core import Settings
from llama_index.core import (SimpleDirectoryReader, VectorStoreIndex,
                              ServiceContext, StorageContext, load_index_from_storage,
                              )
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.llms.openai import OpenAI

from chatplatform.core.config import settings, logger
from chatplatform.db.models.course import Course
from chatplatform.schemas.course import CoursesGPTRequest
from chatplatform.services.course_service import CourseService
from chatplatform.services.document_service import DocumentService

os.environ["OPENAI_API_KEY"] = settings.OPENAPI_KEY
Settings.llm = OpenAI(temperature=0.7,
                      model="gpt-4-turbo-preview")


class LlamaService:
    def __init__(self, db):
        self.db = db
        self.storage = "./storage"
        self.data_path = os.getenv("DOCUMENT_STORAGE_PATH", "/app/documents")
        self.service_context = ServiceContext.from_defaults(chunk_size=1000)
        self.storage_path = Path(self.storage)
        self.query_engine_tools: Dict[str, QueryEngineTool] = {}
        self.agent = OpenAIAgent.from_tools([], llm=Settings.llm, service_context=self.service_context)

    async def index_document(self):
        self.storage_path.mkdir(parents=True, exist_ok=True)
        document_service = DocumentService(self.db)
        documents = await document_service.get_documents()

        for doc in documents:
            subcategory_path = Path(doc.filepath).parent
            subcategory_name = subcategory_path.name

            doc_storage_path = self.storage_path / subcategory_name
            doc_storage_path.mkdir(parents=True, exist_ok=True)

            try:
                storage_context = StorageContext.from_defaults(persist_dir=str(doc_storage_path))
                index = load_index_from_storage(storage_context)
            except Exception as e:
                print(f"Loading index for {subcategory_name} failed, creating a new one:", e)
                document = SimpleDirectoryReader(subcategory_path).load_data()
                index = VectorStoreIndex.from_documents(document, service_context=self.service_context)
                index.storage_context.persist(str(doc_storage_path))
                central_engine = index.as_query_engine(similarity_threshold=0.5)
                self.query_engine_tools = [
                    QueryEngineTool(
                        query_engine=central_engine,
                        metadata=ToolMetadata(
                            description=f"Assistance based on {subcategory_name} documents."
                        )
                    )
                ]

        return "Documents indexed successfully." + " " + " ".join([doc.filepath for doc in documents])

    async def ensure_tool_for_course(self, course_name: str):
        """Ensure that a query engine tool exists for the given course, creating it if necessary."""
        if course_name not in self.query_engine_tools:
            doc_storage_path = self.storage_path / course_name
            try:
                storage_context = StorageContext.from_defaults(persist_dir=str(doc_storage_path))
                index = load_index_from_storage(storage_context)
            except Exception as e:
                logger.error(f"Error loading or creating index for {course_name}: {e}")
                return None

            query_engine = index.as_query_engine(similarity_threshold=0.5)
            tool = QueryEngineTool(
                query_engine=query_engine,
                metadata=ToolMetadata(description=f"Assistance based on {course_name} documents.")
            )
            self.query_engine_tools[course_name] = tool
        return self.query_engine_tools[course_name]

    async def ask_gpt(self, initial_message: str, courses_request: CoursesGPTRequest):
        tools_for_request = []
        for course in courses_request.courses:
            course_name = course.title.replace(" ", "_")
            tool = await self.ensure_tool_for_course(course_name)
            if tool:
                tools_for_request.append(tool)

        if tools_for_request:
            self.agent.from_tools(tools_for_request)
            response = self.agent.chat(initial_message)
            self.agent.from_tools([])
            return response.response
        else:
            logger.error("No query engines loaded for the requested courses.")
            return "Error: Unable to process the request due to missing course data."
