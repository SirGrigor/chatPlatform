import os
from pathlib import Path
from typing import Dict, Optional

from celery import Celery, shared_task
from llama_index.core import Settings, ServiceContext, StorageContext, load_index_from_storage, SimpleDirectoryReader, \
    VectorStoreIndex, PromptHelper
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.llms.openai import OpenAI

from chatplatform.core.config import settings, logger
from chatplatform.db.models.document import Document

os.environ["OPENAI_API_KEY"] = settings.OPENAPI_KEY
Settings.llm = OpenAI(temperature=0.7, model="gpt-4-turbo-preview")
app = Celery('tasks', broker=settings.CELERY_BROKER_URL)


@shared_task
def index_document_task(document_id, db):
    document = db.query(Document).get(document_id)
    if document:
        indexer = DocumentIndexer(db)
        indexer.index_document(document)
    else:
        logger.error(f"Document with ID {document_id} not found.")


class DocumentIndexer:
    def __init__(self, db_session):
        self.db = db_session
        self.storage_path = Path(os.getenv("STORAGE_PATH", "./storage"))
        self.prompt_helper = PromptHelper(4096, 256, 0.5)
        self.service_context = ServiceContext.from_defaults(chunk_size=1000, prompt_helper=self.prompt_helper)
        self.query_engine_tools: Dict[str, QueryEngineTool] = {}

    def index_document(self, doc: Document) -> None:
        logger.info(f"Starting to index document: {doc.filename}")

        # Extract course_name from the document's current system path
        document_path = Path(doc.filepath)
        course_name = document_path.parts[-2]  # Assuming course_name is the second last part of the path

        doc_storage_path = self.storage_path / course_name / "files"
        doc_storage_path.mkdir(parents=True, exist_ok=True)

        try:
            storage_context = StorageContext.from_defaults(persist_dir=str(doc_storage_path))
            index = load_index_from_storage(storage_context)
            document = SimpleDirectoryReader(document_path.parent).load_data()
            index.refresh_ref_docs(document, update_kwargs={"delete_kwargs": {"delete_from_docstore": True}})
        except Exception as e:
            logger.error(f"Failed to load index for {course_name}, creating a new one: {e}")
            document = SimpleDirectoryReader(document_path.parent).load_data()
            splitter = SentenceSplitter(chunk_size=256)
            index = VectorStoreIndex.from_documents(document, service_context=self.service_context,
                                                    transformations=[splitter])
            index.storage_context.persist(str(doc_storage_path))

    async def ensure_tool_for_course(self, course_name: str) -> Optional[QueryEngineTool]:
        if course_name not in self.query_engine_tools:
            doc_storage_path = self.storage_path / course_name / "files"
            try:
                storage_context = StorageContext.from_defaults(persist_dir=str(doc_storage_path))
                index = load_index_from_storage(storage_context)
            except Exception as e:
                logger.error(f"Error loading or creating index for {course_name}: {e}")
                return None
            rerank = SentenceTransformerRerank(
                model="cross-encoder/ms-marco-MiniLM-L-2-v2", top_n=10
            )
            query_engine = index.as_query_engine(similarity_top_k=10, node_postprocessors=[rerank])
            tool = QueryEngineTool(
                query_engine=query_engine,
                metadata=ToolMetadata(name=course_name, description=f"Assistance based on {course_name} documents.")
            )
            self.query_engine_tools[course_name] = tool
        return self.query_engine_tools.get(course_name)
