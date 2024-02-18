import os
from pathlib import Path

from llama_index.core import (SimpleDirectoryReader, VectorStoreIndex,
                              ServiceContext, StorageContext, load_index_from_storage,
                              )

os.environ["OPENAI_API_KEY"] = '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'


class LlamaService:
    def __init__(self, document_path: str):
        self.storage = "./storage"
        self.data_path = document_path
        self.service_context = ServiceContext.from_defaults(chunk_size=1000)
        self.storage_path = Path(self.storage)

    def search_in_documents(self, search_query: str):
        self.storage_path.mkdir(parents=True, exist_ok=True)

        try:
            storage_context = StorageContext.from_defaults(persist_dir=self.storage)
            index = load_index_from_storage(storage_context)
        except Exception as e:
            print("Loading index failed, creating a new one:", e)
            documents = SimpleDirectoryReader(self.data_path).load_data()
            index = VectorStoreIndex.from_documents(documents, service_context=self.service_context)
            index.storage_context.persist(self.storage)

        query_engine = index.as_query_engine(similarity_top_k=5)
        response = query_engine.query(search_query)
        return response.response
