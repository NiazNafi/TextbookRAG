# Textbook RAG

A Retrieval-Augmented Generation (RAG) system for HSC26 Bangla 1st paper book as knowledge base. Implemented self-consistency prompting.


---

## Setup Guide

1. **Clone the repository**

   ```powershell
   git clone https://github.com/NiazNafi/TextbookRAG.git
   cd TextbookRAG
   ```

2. **Create and activate virtual environment**

   ```powershell
   python -m venv rag_env311
   .\rag_env311\Scripts\activate
   ```

3. **Install dependencies**

   ```powershell
   pip install -r requirements.txt
   ```

4. **Prepare data**

   - Place your PDF files in the `data/raw/` directory.
   - Use `pdftopng.py` to convert PDFs to PNGs.
   - Keep your google-api-key in .env file
   - Use `batch_ocr_to_md.py` to extract text from images and save as Markdown.

5. **Build vector store**

   ```powershell
   python scripts/build_vectorstore.py
   ```

6. **Run search or chat**
   ```powershell
   python scripts/search_query.py
   python scripts/rag_chat.py
   ```

---

## Used Tools, Libraries, Packages

- **OCR & PDF Processing:**
  - `pdf2image`, `gemini_api`
- **Text Processing:**
  - `nltk`, `re`, `markdown`
- **Embeddings & Vector Store:**
  - `text-embedding-3-large`, `chromadb`
- **Other:**
  - `openai` , `langchain`
## Databased created for this project
-Available in `https://drive.google.com/drive/folders/10UJnfqMyF4D5k-83f952vVqf_YDgO_H7?usp=sharing`
---

## Sample Queries and Outputs

**Bangla Example:**  
Query:

```
"অনুপম কে?"
```

Output:

```
"অনুপম "অপরিচিতা" গল্পের একটি চরিত্র। তিনি উচ্চ শিক্ষিত হলেও তার নিজস্বতা বলতে কিছু নেই এবং পরিবারতন্ত্রের কাছে অসহায় ও ব্যক্তিত্বহীন একটি চরিত্র হিসেবে উপস্থাপিত।"
```

**English Example:**  
Query:

```
"Do you know who anupam is?"
```

Output:

```
"Yes, Anupam is a character in the story "Aparichita." He is portrayed as an educated but personality-lacking individual who is heavily dependent on his mother and uncle. Despite his education, Anupam lacks independence and is unable to stand up against injustice, as seen when he remains silent during the dowry-related humiliation at his wedding. "
```

<!-- ---

<!-- ## API Documentation

<!-- 
- `POST /query`
  - **Input:** `{ "query": "Your question here" }`
  - **Output:** `{ "answer": "Relevant answer from textbook" }


## Evaluation
<!-- 
- **Metrics:** Precision, Recall, F1-score, MRR
- **Method:** Manual annotation of retrieved answers vs. ground truth --> 



## Evaluation
<!-- 
- **Metrics:** Precision, Recall, F1-score, MRR
- **Method:** Manual annotation of retrieved answers vs. ground truth -->
-->
---

## Project Questions & Answers

### 1. What method or library did you use to extract the text, and why? Did you face any formatting challenges with the PDF content?

- **Method:** Used `pdf2image` to convert PDF pages to images, then used gemini for extracting text and developing markup language for tables and headings.
- **Reason:** The encoding of pdf was not in unicode format. Using traditional libraries would not give proper text formats. I thought of using  pytesseract to ocr for extracting text. But I wanted to see gemini-flash-2.0-exp capability to do the task of annotating the red and blue highlighted linees and give the markup which is essential to get a proper formatting for tables and charts and further filtering sections.
- **Challenges:**
  - Did not give proper result for red and blue highlight. So omitted that part in post-processing.
  - Manual post-processing and cleaning were sometimes required.

### 2. What chunking strategy did you choose? Why do you think it works well for semantic retrieval?

- **Strategy:** `Recursive Character Chunking` with section heading as metadata for filtering (split by double newlines or Markdown headings).
- **Reason:** I chose to split the processed data into different sections so that proper metadata can be incorporated with the chunks. And I wanted to keep the window open for q and a for creative question patterns, and for this I used recursivecharactersplitter from Langchain to chunk upto 1000 character from each section.

### 3. What embedding model did you use? Why did you choose it? How does it capture the meaning of the text?

- **Model:** `text-embedding-3-large`
- **Reason:** Supports both Bangla and English, efficient.

### 4. How are you comparing the query with your stored chunks? Why did you choose this similarity method and storage setup?

- **Method:** Cosine similarity between query embedding and chunk embeddings.
- **Storage:** Used `chromadb` for efficient vector storage and retrieval.
- **Reason:** Cosine similarity is standard for measuring semantic closeness in embedding space. ChromaDB is lightweight and easy to use for local vector search.

### 5. How do you ensure that the question and the document chunks are compared meaningfully? What would happen if the query is vague or missing context?

- **Ensuring meaningful comparison:**
  - Both queries and chunks are embedded using the same model.
  - Chunking preserves context within each paragraph.
- **If query is vague:**
  - The system may return less relevant or generic chunks.
  - Adding query expansion or clarifying questions could improve results.

### 6. Do the results seem relevant? If not, what might improve them?

- **Relevance:** Generally good for well-formed queries.
- **Possible improvements:**
  - Better OCR post-processing to reduce noise.
  - Experiment with different chunk sizes or overlap.
  - Use a more advanced or domain-specific embedding model.
  - Increase the size and diversity of the document corpus.

---
