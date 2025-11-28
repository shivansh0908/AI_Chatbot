AI Chatbot – Shiv Nadar University

A Retrieval-Augmented Generation (RAG) based AI chatbot designed for Shiv Nadar University to answer general academic queries, provide information efficiently, and demonstrate practical implementation of modern LLM technologies.

📘 Project Overview

This project implements an AI-powered chatbot capable of answering SNU-related questions using a combination of web scraping, text processing, vector search, and large language models. The chatbot uses a Retrieval-Augmented Generation (RAG) pipeline to retrieve the most relevant information from scraped university resources and generate accurate, context-aware answers.

The system consists of a FastAPI backend that handles the RAG pipeline and a simple HTML/CSS/JavaScript frontend for user interaction. It is lightweight, extendable, and designed to run locally or on a server.

🚀 Key Features

Retrieval-Augmented Generation (RAG):
Combines document retrieval with LLM-based response generation for reliable answers.

Custom Web Scraper:
Automatically fetches and converts academic content into clean, searchable text.

FAISS Vector Search:
Enables fast and efficient similarity search on embedded documents.

OpenAI LLM Integration:
Uses OpenAI embedding models and LLMs to generate high-quality responses.

Modular Architecture:
Clearly separated backend, frontend, and data processing pipelines.

Simple and Clean Frontend:
Users can chat with the bot through an intuitive web UI.

Environment-Based Configuration:
.env file ensures secure storage of API keys and model configurations.

📁 Project Structure
AI_Chatbot/
│
├── Backend/
│   ├── main.py                 # FastAPI backend server
│   ├── rag_pipeline.py         # Core RAG implementation
│   ├── vector_store.py         # FAISS vector database handler
│   ├── scrapper.py             # Web scraping tools
│   ├── markdown_cleaner.py     # Converts HTML → Markdown → Clean text
│   └── utils.py                # Helper functions
│
├── Frontend/
│   ├── index.html              # Chat interface
│   ├── script.js               # API communication logic
│   └── style.css               # UI styling
│
├── static/                     # Images, CSS, media assets
│
├── scrapperlinks.py            # List of URLs to scrape from
├── markdown_generator.py       # Generates markdown from scraped HTML
│
├── .env                        # API keys and configuration
├── requirements.txt            # Python dependencies
└── README.md

🔧 Setup & Installation
1. Clone the Repository
git clone https://github.com/shivansh0908/AI_Chatbot.git
cd AI_Chatbot

2. Create a Virtual Environment
python3 -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows

3. Install Dependencies
pip install -r requirements.txt

4. Add Environment Variables

Create a .env file in the project root:

OPENAI_API_KEY=your_openai_api_key_here
MODEL_NAME=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small

▶️ Running the Chatbot
Start the Backend Server
cd Backend
uvicorn main:app --reload


The server will start at:

http://127.0.0.1:8000

Open the Frontend

Open the file:

Frontend/index.html


Start chatting with the bot via the UI.

🧠 How the RAG System Works

Scraping
The scraper fetches academic content from URLs listed in scrapperlinks.py.

Markdown Processing
Raw HTML is converted to markdown, then cleaned into plain text.

Chunking & Embedding
The text is split into chunks and converted into embeddings using OpenAI’s embedding model.

Vector Indexing
FAISS stores embeddings for fast similarity searching.

Retrieval
When a user asks a question, the system retrieves the top relevant chunks.

LLM Response
Retrieved context + user question → sent to the LLM → final answer generated.

🧪 API Endpoints
POST /ask

Send a question to the RAG model.

GET /health

Check if the backend is running.

GET /get_context

Returns the retrieved context chunks (debugging/testing purpose).

📚 Technologies Used

FastAPI – Backend framework

OpenAI API – LLM and embeddings

FAISS – Vector database for similarity search

BeautifulSoup – Web scraping

LangChain – RAG pipeline utilities

HTML/CSS/JS – Frontend interface

📌 Future Enhancements

Add PDF and DOCX support

Create an admin dashboard

UI improvements and chat history

Deployment on Render / AWS / Railway

Add multi-language support

Expand dataset for broader questions

✨ Purpose of the Project

This chatbot is built as part of an AI project for Shiv Nadar University.
Its goal is to demonstrate real-world use of Retrieval-Augmented Generation and simplify how students access academic information.

👨‍💻 Author

Shivansh Banerjee
B.Tech Student — Shiv Nadar University
