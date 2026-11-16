# 🤖 HR Policies RAG Chatbot

This repository contains a **Retrieval-Augmented Generation (RAG) chatbot** designed to answer questions from HR policy documents using advanced AI technologies.

**Tech Stack:**

- **Vector Store:** Pinecone (serverless)  
- **Embeddings:** `all-MiniLM-L6-v2`  
- **LLM / Inference:** Groq LLaMA 3.1 / OpenAI / Ollama  
- **Backend:** FastAPI (Python Serverless on Vercel)  
- **Frontend:** Vite + Modern Web Chat UI (Vercel-native, No Streamlit)  

---

## 🛠 Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Shah-Abdul-Mazid/DevelopRag.git
cd DevelopRag
```

### 2. Repository Structure

```
DevelopRag/
├── backend/
│   ├── main.py             # FastAPI backend (dual routes /ask & /api/ask)
│   ├── backend.py          # Core RAG implementation
│   ├── rag_retriever_setup.py # Document indexing script
│   ├── requirements.txt    # Backend dependencies (serverless-friendly)
│   └── api/
│       └── index.py        # Serverless function entrypoint
├── frontend/               # Vite Web Chat UI (deployed to Vercel)
│   ├── index.html          # Chat interface with parameters & stats
│   ├── package.json        # Vite configuration
│   └── src/
│       ├── main.js         # API integration
│       └── style.css       # Responsive styling
├── HR Policies/            # PDF documents
├── vercel.json             # Vercel multi-service configuration
└── README.md
```

### 3. Install Dependencies

```bash
# Backend
pip install -r backend/requirements.txt

# Frontend
cd frontend && npm install && cd ..
```

### 4. Set Environment Variables

Create a `.env` in the `backend/` folder:

```
PINECONE_API_KEY=YOUR_PINECONE_API_KEY
GROQ_API_KEY=YOUR_GROQ_API_KEY
```

### 5. Run Locally

```bash
# Terminal 1: Backend
cd backend && python -m uvicorn main:app --reload

# Terminal 2: Frontend
cd frontend && npm run dev
```

The Streamlit app will open in your browser and connect to the backend.

---

## 📚 Usage

* Ask questions about HR policies directly in the chat interface.
* Adjust RAG parameters in the sidebar:

  * **Number of documents (top_k)** – how many relevant documents to retrieve
  * **Similarity threshold** – minimum similarity score for retrieved documents
  * **LLM fallback** – enable/disable fallback to general LLM if no documents are found
* Chat history is preserved throughout the session.

---

## 🖼 Example Usage

### 1. Chat Interface

![Chat Interface Screenshot](frontend_screenshot_placeholder.png)
*Web chat interface for interacting with the RAG chatbot.*

### 2. Sample Queries

| User Query                                                                                  | Example Response                                                                                                           |
| ------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| "When Red Cross Society in East Pakistan was transformed into the National Red Cross Society of Bangladesh?" | "The Red Cross Society in East Pakistan was transformed into the National Red Cross Society of Bangladesh on December 20, 1971." |
| "When Renamed as Bangladesh Red Cross Society by a GoB order?"                               | "The Bangladesh Red Crescent Society was renamed as Bangladesh Red Cross Society by a GoB (Government of Bangladesh) order on January 4, 1972." |
| "When Udayankur Seba Sangstha started its journey?"                                         | "Udayankur Seba Sangstha (USS) started its journey in 1997."                                                              |

### 3. Adjustable Parameters

* **Top K documents:** Retrieve more or fewer documents for context
* **Similarity threshold:** Filter documents based on relevance
* **LLM fallback:** Enable if no exact match is found in documents

---

## 🧩 Project Structure

* **backend/** – Backend (FastAPI), RAG retrieval, and notebooks
* **frontend/** – Vite web interface for Vercel deployment
* **hr_policies/** – Folder for HR policy PDF documents
* **README.md** – Project instructions

---

## 🚀 Deploying on Vercel (Frontend & Backend Services)

This repository includes a multi-service setup configured via `vercel.json` for full-stack deployment on Vercel:

- **Frontend:** Modern interactive chat UI built with Vite (`frontend/`)
- **Backend:** Serverless FastAPI service connecting to Pinecone (`backend/`)
- **Routing:** Handled automatically via `vercel.json` rewrites

### Vercel Environment Variables:
Configure the following in your **Vercel Project Settings > Environment Variables**:

| Variable | Description | Required? |
|---|---|---|
| `PINECONE_API_KEY` | Your Pinecone API key | Yes |
| `PINECONE_INDEX` | Index name (defaults to `hr-policies`) | Optional |
| `PINECONE_NAMESPACE` | Namespace (defaults to `hr-policies`) | Optional |
| `GROQ_API_KEY` | Free ultra-fast LLaMA 3.1 inference on cloud | Recommended |
| `OPENAI_API_KEY` | OpenAI API key for GPT-4o-mini | Optional |
| `HUGGINGFACE_API_KEY` | Hugging Face token for serverless embeddings | Optional |

### Deploy via Vercel CLI:
```bash
# 1. Install Vercel CLI if not already installed
npm install -g vercel

# 2. Deploy to Vercel
vercel
```

---

## ⚡ Notes

* Ensure your Pinecone API key is set correctly.
* Preprocessing PDFs is required on the first run to populate the vector store.
* For local runs, Ollama Llama2 can be used; for Vercel cloud deployment, Groq or OpenAI is recommended because Vercel Serverless runs in a stateless environment without a local Ollama daemon.

## 🎥 Demo Image
<img width="2558" height="1598" alt="image" src="https://github.com/user-attachments/assets/d9579520-4b18-44be-9717-e472df7732ed" />

