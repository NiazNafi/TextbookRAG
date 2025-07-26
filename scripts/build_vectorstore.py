import json
import os
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()
JSON_FILE = "data/processed/HSC26-Bangla1st-Paper-with-answers.json"
CHROMA_DIR = "chroma_db"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100




def load_json(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        return json.load(f)

def create_documents(json_data):
    
    #Convert JSON entries into LangChain Documents.
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""]
    )

    docs = []
    for entry in json_data:
        section = entry.get("section", "unknown")
        content = entry.get("content", "")
        metadata = {"section": section}

        split_docs = splitter.create_documents([content], metadatas=[metadata])
        docs.extend(split_docs)

    print(f"Created {len(docs)} chunks from {len(json_data)} sections.")
    return docs

def build_chroma_vectorstore(docs, persist_dir):
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large",  # multilingual, high quality
        openai_api_key=api_key
    )

    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=persist_dir,
        collection_name="bangla_hsc26_db"
    )

    print(f"Vectorstore built and saved at {persist_dir}")
    return vectorstore

def main():
    data = load_json(JSON_FILE)

    docs = create_documents(data)

    # Preview first few chunks
    print("\n=== Preview of chunks ===")
    for i, d in enumerate(docs[:5]):
        print(f"\n--- Chunk {i+1} ---")
        print("Metadata:", d.metadata)
        print("Content:\n", d.page_content[:300], "...\n")
        
    build_chroma_vectorstore(docs, CHROMA_DIR)

if __name__ == "__main__":
    main()
