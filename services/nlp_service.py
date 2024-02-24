import os
from pathlib import Path

from llama_index.core import (SimpleDirectoryReader, VectorStoreIndex,
                              ServiceContext, StorageContext, load_index_from_storage,
                              )
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings
from core.config import settings
from llama_index.agent.openai import OpenAIAgent
os.environ["OPENAI_API_KEY"] = settings.OPENAPI_KEY
Settings.llm = OpenAI(temperature=0.7,
                      model="gpt-4-turbo-preview")


class LlamaService:
    def __init__(self, document_path: str):
        self.storage = "./storage"
        self.data_path = os.getenv("DOCUMENT_STORAGE_PATH", document_path)
        self.service_context = ServiceContext.from_defaults(chunk_size=1000)
        self.storage_path = Path(self.storage)
        self.agent = OpenAIAgent.from_tools(llm=Settings.llm, service_context=self.service_context)

    async def search_in_documents(self, search_query: str):
        self.storage_path.mkdir(parents=True, exist_ok=True)

        try:
            storage_context = StorageContext.from_defaults(persist_dir=self.storage)
            index = load_index_from_storage(storage_context)
        except Exception as e:
            print("Loading index failed, creating a new one:", e)
            documents = SimpleDirectoryReader(self.data_path).load_data()
            index = VectorStoreIndex.from_documents(documents, service_context=self.service_context)
            index.storage_context.persist(self.storage)

        return self.agent.chat(search_query).response
