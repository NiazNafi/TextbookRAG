from collections import Counter
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

PERSIST_DIR = "chroma_db"
EMBED_MODEL = "text-embedding-3-large"
LLM_MODEL = "gpt-4o"
SELF_CONSISTENCY_RUNS = 3


load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Custom prompt
custom_prompt_template = """
আপনাকে শুধুমাত্র প্রদত্ত কন্টেক্সট (জ্ঞানভাণ্ডার) ব্যবহার করে উত্তর দিতে হবে।
যদি প্রশ্নের সরাসরি উত্তর নিচের কন্টেক্সটে না থাকে, তবে শুধু লিখুন:
"আমার এ সম্পর্কে ধারনা নেই"

কন্টেক্সট:
{context}

প্রশ্ন:
{question}

উত্তর বাংলায় দিন:
"""
QA_PROMPT = PromptTemplate(
    template=custom_prompt_template,
    input_variables=["context", "question"]
)

embeddings = OpenAIEmbeddings(model=EMBED_MODEL)
vectorstore = Chroma(
    persist_directory=PERSIST_DIR,
    embedding_function=embeddings,
    collection_name="bangla_hsc26_db"
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 20})
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
llm = ChatOpenAI(model=LLM_MODEL, openai_api_key=api_key, temperature=0.2)

qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    memory=memory,
    combine_docs_chain_kwargs={"prompt": QA_PROMPT},
    verbose=False
)

def self_consistent_answer(question: str) -> str:

    docs = retriever.get_relevant_documents(question)
    if not docs:
        return "আমার এ সম্পর্কে ধারনা নেই"

    answers = []
    for _ in range(SELF_CONSISTENCY_RUNS):
        result = qa_chain.invoke({"question": question})
        answers.append(result["answer"])

    final = Counter(answers).most_common(1)[0][0]
    if "আমার এ সম্পর্কে ধারনা নেই" in final:
        return "আমার এ সম্পর্কে ধারনা নেই"
    return final

app = FastAPI()

class QueryRequest(BaseModel):
    question: str

@app.post("/ask")
def ask(req: QueryRequest):
    answer = self_consistent_answer(req.question)
    return {"answer": answer}
