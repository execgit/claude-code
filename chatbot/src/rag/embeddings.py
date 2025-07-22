import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
from langchain_core.documents import Document
from config.settings import settings


class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer(settings.embedding_model)
        self.client = chromadb.PersistentClient(path=settings.vector_db_path)
        self.collection = self.client.get_or_create_collection(
            name="documents", metadata={"hnsw:space": "cosine"}
        )

    def embed_documents(self, documents: List[Document]) -> None:
        if not documents:
            print("No documents to embed")
            return

        # Prepare data for ChromaDB
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        ids = [f"doc_{i}" for i in range(len(documents))]

        # Generate embeddings
        embeddings = self.model.encode(texts, show_progress_bar=True)

        # Store in ChromaDB
        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=texts,
            metadatas=metadatas,
            ids=ids,
        )

        print(f"Embedded and stored {len(documents)} document chunks")

    def search(self, query: str, k: int = None) -> List[Dict[str, Any]]:
        if k is None:
            k = settings.top_k_results

        query_embedding = self.model.encode([query])

        results = self.collection.query(
            query_embeddings=query_embedding.tolist(), n_results=k
        )

        # Format results
        formatted_results = []
        for i in range(len(results["documents"][0])):
            formatted_results.append(
                {
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                }
            )

        return formatted_results

    def get_collection_count(self) -> int:
        return self.collection.count()

    def clear_collection(self) -> None:
        self.client.delete_collection("documents")
        self.collection = self.client.get_or_create_collection(
            name="documents", metadata={"hnsw:space": "cosine"}
        )
