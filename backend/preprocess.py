import json
from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader, JSONLoader, DirectoryLoader, UnstructuredMarkdownLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import os
import dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_community.document_loaders.firecrawl import FireCrawlLoader

dotenv.load_dotenv()
FIRECRAWL_API_KEY = os.environ.get("FIRECRAWL_API_KEY")

def crawl_and_load():
    loader = FireCrawlLoader(
        api_key=FIRECRAWL_API_KEY, url="https://srijanju.in", mode="crawl"
    )
    data = loader.load()
    return data

def load_from_json():
    loader = JSONLoader(
        file_path="./data2/web_data.json",
        jq_schema=".[] | {content: .markdown, metadata: .metadata}",
        text_content=False
    )
    docs = loader.load()
    return docs

def load_md():
    loader = DirectoryLoader('./data2', glob="*.md", loader_cls=UnstructuredMarkdownLoader, show_progress=True)
    docs = loader.load()
    return docs

def load_files():
    loader = DirectoryLoader('./data', glob="*", show_progress=True)
    pdf_loader = PyPDFLoader('./data/sample.pdf')
    pdf_docs = pdf_loader.load()
    loader.documents.extend(pdf_docs)
    docs = loader.load()
    return docs

def save_embeddings(chunks, name="faiss_index"):
    if not chunks:
        raise ValueError("Chunks not provided!")
    hf = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = FAISS.from_documents(chunks, hf)
    db.save_local(name)
    print(f"Saved {len(chunks)} chunks to FAISS and stored locally")
    return db

def split_text(documents, chunk_size=300, chunk_overlap=50, length_function=len, add_start_index=True):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap, length_function=length_function, add_start_index=add_start_index)
    chunks = text_splitter.split_documents(documents)
    return chunks