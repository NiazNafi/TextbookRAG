from collections import Counter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os

PERSIST_DIR = "chroma_db"
EMBED_MODEL = "text-embedding-3-large"
LLM_MODEL = "gpt-4o"
SELF_CONSISTENCY_RUNS = 3

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

embeddings = OpenAIEmbeddings(model=EMBED_MODEL)
vectorstore = Chroma(
    persist_directory=PERSIST_DIR,
    embedding_function=embeddings,
    collection_name="bangla_hsc26_db"
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 20})
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

llm = ChatOpenAI(model=LLM_MODEL,
                 openai_api_key=api_key,
                 temperature=0.2)

# Custom QA prompt
custom_prompt_template = """
আপনি শুধুমাত্র প্রদত্ত কন্টেক্সট (জ্ঞানভাণ্ডার/knowledge) ব্যবহার করে উত্তর দিবেন।
যদি প্রশ্নের উত্তর কন্টেক্সটে না থাকে, তবে বলুন: "আমার এ সম্পর্কে ধারনা নেই"

কন্টেক্সট:
{context}

প্রশ্ন:
{question}

"""

QA_PROMPT = PromptTemplate(
    template=custom_prompt_template,
    input_variables=["context", "question"]
)

qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    memory=memory,
    combine_docs_chain_kwargs={"prompt": QA_PROMPT},
    verbose=True
)

# Self Consistency Function
def self_consistent_answer(question):
    answers = []
    for _ in range(SELF_CONSISTENCY_RUNS):
        result = qa_chain.invoke({"question": question})
        answers.append(result["answer"])
    return Counter(answers).most_common(1)[0][0]

if __name__ == "__main__":
    print("RAG Chatbot (type 'exit' to quit)\n")
    while True:
        q = input("You: ")
        if q.lower().strip() in ["exit", "quit"]:
            break
        answer = self_consistent_answer(q)
        print("Bot:", answer)
