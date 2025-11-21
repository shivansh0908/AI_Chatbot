# build_index.py
import os
import shutil
from tqdm import tqdm
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

load_dotenv()

INDEX_DIR = "data/faiss_index"
SOURCE_MD = "data/combined_data.md"
BATCH = 400
CHUNK_SIZE = 1800
CHUNK_OVERLAP = 150

def load_markdown(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def build():
    if not os.path.exists(SOURCE_MD):
        raise FileNotFoundError(f"{SOURCE_MD} not found")

    text = load_markdown(SOURCE_MD)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        add_start_index=True
    )

    print("🪓 Splitting text into chunks...")
    docs = splitter.create_documents([text])
    print(f"✅ Created {len(docs)} chunks.")

    # wipe old index
    shutil.rmtree(INDEX_DIR, ignore_errors=True)
    os.makedirs(INDEX_DIR, exist_ok=True)

    print("🚀 Creating embeddings & FAISS index...")
    embedding_model = OpenAIEmbeddings(
        model=os.getenv("EMBEDDING_MODEL","text-embedding-3-small"),
        api_key=os.getenv("OPENAI_API_KEY")
    )

    vector_store = None
    for i in tqdm(range(0, len(docs), BATCH)):
        batch = docs[i:i+BATCH]
        if vector_store is None:
            vector_store = FAISS.from_documents(batch, embedding_model)
        else:
            vector_store.add_documents(batch)

    vector_store.save_local(INDEX_DIR)
    print("✅ FAISS index saved at", INDEX_DIR)

if __name__ == "__main__":
    build()
