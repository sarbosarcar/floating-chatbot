import faiss
import numpy as np
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from preprocess import load_files, save_embeddings, split_text, crawl_and_load, load_from_json, load_md

def prepare_db(split_size=512, overlap=128):
    # docs = load_from_json()
    docs = load_md()
    chunks = split_text(docs, chunk_size=split_size, chunk_overlap=overlap)
    db = save_embeddings(chunks)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(docs, embeddings)
    vectorstore.save_local("index")
    print("Vector store saved successfully!")
    return vectorstore

def load_index(index_path: str, embeddings_model=HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")):
    try:
        return FAISS.load_local(index_path, embeddings_model, allow_dangerous_deserialization=True)
    except Exception as e:
        print("Error loading FAISS index:", e)
        exit()

def fetch_sources(query, db, top_k=1):
    results = db.similarity_search(query, top_k)
    context = "\n".join(
        f"{result.page_content}"
        for result in results
    )
    return context