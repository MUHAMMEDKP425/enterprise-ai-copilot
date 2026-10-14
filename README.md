# 🤖 Enterprise AI Copilot

An AI-powered knowledge assistant that allows users to ask questions about company documents and receive answers based on the information retrieved from uploaded PDFs.

## 🚀 Features

- 📄 **PDF Document Upload** — Upload and manage company documents.
- 🧠 **AI-Powered Question Answering** — Ask questions in natural language using Retrieval-Augmented Generation (RAG).
- 🔍 **Semantic Search** — Find relevant document passages using embeddings and vector search.
- 📚 **Source References** — View source information associated with retrieved content.
- 🎯 **Document Filtering** — Search across all documents or select a specific document.
- 💬 **Persistent Chat History** — Save and reopen previous conversations.
- 🔄 **Follow-up Questions** — Use conversation history to understand follow-up questions.
- ⚡ **FastAPI Backend** — Provide API endpoints for document and chat operations.
- 🎨 **Streamlit Interface** — Interact with the assistant through a modern web interface.
- 🗄️ **Vector Database** — Store and retrieve document embeddings using Qdrant.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Frontend interface |
| FastAPI | Backend API |
| Qdrant | Vector database |
| Sentence Transformers | Text embeddings |
| PyMuPDF | PDF processing |
| OpenRouter | Language model API access |
| SQLite | Persistent chat history |
| Pydantic | Data validation |
| Uvicorn | Backend server |

## 🏗️ Project Structure

```text
enterprise-ai-copilot/
│
├── backend/
│   └── app/
│       ├── main.py
│       ├── rag_service.py
│       ├── document_service.py
│       ├── document_management.py
│       ├── pdf_reader.py
│       ├── qdrant_store.py
│       ├── chat_history.py
│       ├── store_embeddings.py
│       ├── search_qdrant.py
│       └── evaluate_rag.py
│
├── Data/
│   └── Documents/
│
├── frontend.py
├── requirements.txt
├── .gitignore
└── README.md
```

## 🧠 How It Works

This project uses **Retrieval-Augmented Generation (RAG)** to answer questions using uploaded documents.

1. **Upload:** The user uploads a PDF document.
2. **Process:** The application extracts text from the document.
3. **Embed:** The document content is converted into vector embeddings.
4. **Store:** The embeddings are stored in Qdrant.
5. **Retrieve:** When the user asks a question, the application searches for relevant document passages.
6. **Generate:** The retrieved information is provided to the language model to generate an answer.
7. **Display:** The answer and available source information are displayed in the interface.

The application is designed to use retrieved document content as the factual basis for answers. Response quality depends on the quality of the documents, retrieval, and model output.

## ⚙️ Installation and Setup

### Prerequisites

Before starting, make sure you have:

- Python installed
- Git installed
- An OpenRouter API key

### 1. Clone the Repository

```bash
git clone https://github.com/MUHAMMEDKP425/enterprise-ai-copilot.git
```

Navigate into the project directory:

```bash
cd enterprise-ai-copilot
```

### 2. Create a Virtual Environment

On Windows Command Prompt:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure the API Key

Create a `.env` file in the project root.

Add your OpenRouter API key:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

Replace `your_openrouter_api_key_here` with your own API key.

**Security note:** Never upload your `.env` file or API key to GitHub.

### 5. Start the Backend

From the project root, run:

```bash
uvicorn backend.app.main:app --reload
```

The backend should start at:

```text
http://127.0.0.1:8000
```

### 6. Start the Frontend

Open a second terminal in the project directory.

Activate the virtual environment if necessary, then run:

```bash
streamlit run frontend.py
```

Open the local URL displayed in the terminal to use the application.

## 🔐 Security

- Store API keys in environment variables.
- Never commit secrets to GitHub.
- Keep `.env` and `.venv/` excluded through `.gitignore`.
- Do not upload confidential company documents or personal information.
- Protect local chat history and database files.
- Review authentication and access controls before deploying the application for business use.

## 📌 Future Improvements

Potential future improvements include:

- Automated document-specific question suggestions
- Improved retrieval evaluation
- Support for additional document formats
- User authentication and access control
- Cloud deployment
- Enhanced document citation and page references

## 👨‍💻 Author

**Muhammed KP**

GitHub: [MUHAMMEDKP425](https://github.com/MUHAMMEDKP425)

Project Repository: [Enterprise AI Copilot](https://github.com/MUHAMMEDKP425/enterprise-ai-copilot)

## 📄 License

No license has been specified for this project yet.
