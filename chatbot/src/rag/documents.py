import markdown
from pathlib import Path
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from config.settings import settings


class MarkdownDocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
        )

    def load_documents(self) -> List[Document]:
        documents = []
        documents_path = Path(settings.documents_path)

        if not documents_path.exists():
            print(f"Documents directory not found: {documents_path}")
            return documents

        for md_file in documents_path.glob("**/*.md"):
            try:
                with open(md_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Convert markdown to plain text for better chunking
                html = markdown.markdown(content)
                # Simple HTML tag removal for plain text
                import re

                text = re.sub(r"<[^>]+>", "", html)

                doc = Document(
                    page_content=text,
                    metadata={
                        "source": str(md_file),
                        "filename": md_file.name,
                        "type": "markdown",
                    },
                )
                documents.append(doc)

            except Exception as e:
                print(f"Error loading {md_file}: {e}")

        return documents

    def split_documents(self, documents: List[Document]) -> List[Document]:
        return self.text_splitter.split_documents(documents)

    def process_documents(self) -> List[Document]:
        raw_documents = self.load_documents()
        if not raw_documents:
            return []

        chunks = self.split_documents(raw_documents)
        print(f"Processed {len(raw_documents)} documents into {len(chunks)} chunks")
        return chunks
