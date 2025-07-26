import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large",
    openai_api_key=api_key
)

db = Chroma(
    persist_directory="chroma_db",
    embedding_function=embeddings,
    collection_name="bangla_hsc26_db"
)

results = db.similarity_search("অনুপমের ভাগ্য দেবতা কে?", k=3)
for doc in results:
    print(doc.metadata, doc.page_content)