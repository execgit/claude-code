from typing import Dict, Any
from .embeddings import EmbeddingService
from .documents import MarkdownDocumentProcessor
from config.settings import settings

class RAGRetriever:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.document_processor = MarkdownDocumentProcessor()
        
    def initialize_knowledge_base(self) -> None:
        print("Initializing knowledge base...")
        
        # Clear existing collection
        self.embedding_service.clear_collection()
        
        # Process and embed documents
        documents = self.document_processor.process_documents()
        if documents:
            self.embedding_service.embed_documents(documents)
        else:
            print("No documents found to process")
    
    def retrieve_context(self, query: str) -> str:
        if self.embedding_service.get_collection_count() == 0:
            return "No knowledge base available."
        
        results = self.embedding_service.search(query, k=settings.top_k_results)
        
        if not results:
            return "No relevant information found."
        
        # Combine retrieved chunks into context
        context_parts = []
        for i, result in enumerate(results):
            source = result['metadata'].get('filename', 'Unknown')
            content = result['content']
            context_parts.append(f"[Source: {source}]\n{content}")
        
        return "\n\n---\n\n".join(context_parts)
    
    def get_knowledge_base_info(self) -> Dict[str, Any]:
        return {
            "document_count": self.embedding_service.get_collection_count(),
            "documents_path": settings.documents_path,
            "embedding_model": settings.embedding_model
        }