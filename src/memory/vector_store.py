from typing import List, Dict, Any, Optional
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class LocalVectorStore:
    """Local vector storage for RAG with ChromaDB"""

    def __init__(
        self,
        persist_directory: str = "./data/vector_db",
        collection_name: str = "agentaru_knowledge",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        # Initialize embeddings
        try:
            self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
            logger.info(f"Initialized embeddings: {embedding_model}")
        except Exception as e:
            logger.error(f"Failed to initialize embeddings: {e}")
            raise

        # Initialize Chroma
        try:
            self.vectorstore = Chroma(
                collection_name=collection_name,
                embedding_function=self.embeddings,
                persist_directory=str(self.persist_directory),
            )
            logger.info(f"Initialized ChromaDB: {collection_name}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise

    def add_documents(
        self,
        texts: List[str],
        metadatas: List[Dict[str, Any]] = None,
        ids: List[str] = None,
    ):
        """Add documents to vector store"""
        try:
            result = self.vectorstore.add_texts(texts=texts, metadatas=metadatas, ids=ids)
            logger.info(f"Added {len(texts)} documents to vector store")
            return result
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            return None

    def similarity_search(
        self, query: str, k: int = 5, filter: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        try:
            results = self.vectorstore.similarity_search_with_score(
                query=query, k=k, filter=filter
            )

            return [
                {"content": doc.page_content, "metadata": doc.metadata, "score": score}
                for doc, score in results
            ]
        except Exception as e:
            logger.error(f"Failed to search documents: {e}")
            return []

    def as_retriever(self, **kwargs):
        """Get LangChain retriever interface"""
        return self.vectorstore.as_retriever(**kwargs)

    def delete_collection(self):
        """Delete the collection"""
        try:
            self.vectorstore.delete_collection()
            logger.info("Deleted vector store collection")
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
