"""
Wrapper for langchain vector store
"""
from typing import List, Dict

#from langchain.docstore.document import Document
from langchain.vectorstores import VectorStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from uuid import uuid4
from langchain_core.documents import Document

class VectorStoreWrapper:
    """
    A Wrapper for LangchainVectorStore to handle GPT-Researcher Document Type
    """
    def __init__(self, vector_store : Chroma):
        self.vector_store = vector_store

    def load(self, documents):
        """
        Load the documents into vector_store
        Translate to langchain doc type, split to chunks then load
        """
        langchain_documents = self._create_langchain_documents(documents)
        self.vector_store.add_documents(documents = list(langchain_documents.values()), ids=list(langchain_documents.keys()))
    
    def _create_langchain_documents(self, data: List[Dict[str, str]]) -> dict:
        """Convert GPT Researcher Document to Langchain Document"""
        return {
            item["url"] + '_' + str(uuid4()): Document(page_content=item["raw_content"], metadata={"source": item["url"]}) for item in data
        }
        # return [Document(page_content=item["raw_content"], metadata={"source": item["url"]}) for item in data]

    def _split_documents(self, documents: List[Document], chunk_size: int = 1000, chunk_overlap: int = 100) -> List[Document]:
        """
        Split documents into smaller chunks
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        #return text_splitter.split_documents(documents)
        return text_splitter.create_documents(documents)

    async def asimilarity_search(self, query, k, filter):
        """Return query by vector store"""
        results = await self.vector_store.asimilarity_search(query=query, k=k, filter=filter)
        return results

    def _get_retriever(self, similarity_threshold):
        """Return query by vector store"""
        return self.vector_store.as_retriever(search_type="similarity_score_threshold", search_kwargs={"k" : 10, "score_threshold": similarity_threshold})
