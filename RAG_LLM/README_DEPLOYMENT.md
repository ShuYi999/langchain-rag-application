# 🚀 Production RAG System with Multi-Query Retrieval & Tools

A production-ready Retrieval Augmented Generation (RAG) system featuring multi-query retrieval, tool integration, comprehensive evaluation, and containerized deployment.

## ✨ Features

### Core RAG Capabilities
- ✅ **Multi-Query Retrieval**: Generates multiple query variations for better document retrieval
- ✅ **FAISS Vector Store**: Efficient similarity search with embeddings
- ✅ **Free LLM**: Uses Ollama (llama3.2:1b) - completely free and local

### Tool Integration
- 🧮 **Calculator Tool**: Performs mathematical calculations
- 📚 **Knowledge Base Search**: Retrieves information from documents
- 🤖 **Agent Mode**: Intelligently chooses and combines tools

### Evaluation & Monitoring
- 📊 **Ragas Metrics**: Automated evaluation of RAG quality
  - Faithfulness: Answer grounded in context
  - Context Relevance: Retrieved chunks are relevant
  - Answer Relevance: Answer addresses the question
  - Context Recall: Context has needed information

### User Interface
- 🎨 **Streamlit Frontend**: Beautiful, interactive web UI
- 📖 **FastAPI Docs**: Auto-generated API documentation
- 💡 **Example Questions**: Built-in examples for testing

### Production Ready
- 🐳 **Dockerized**: Full Docker + Docker Compose setup
- 🏥 **Health Checks**: Built-in endpoint monitoring
- 🔄 **Auto-restart**: Resilient container configuration
- 📝 **Logging**: Comprehensive request/response logging

---

## 📋 Prerequisites

### Required
- **Python 3.11+**
- **Ollama** (for running LLM locally)
  - Download: https://ollama.ai
  - Install model: `ollama pull llama3.2:1b`
- **Docker & Docker Compose** (for deployment)

### Optional
- Git (for version control)
- Postman/Thunder Client (for API testing)

---

## 🛠️ Installation

### 1. Clone or Download the Project

```bash
cd "c:\Users\limsy\Documents\Private\Coding\Machine Learning\LangChain"
```

### 2. Create Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

#### For API Development:
```powershell
pip install -r requirements.txt
```

#### For Frontend:
```powershell
pip install -r requirements_frontend.txt
```

#### For Evaluation:
```powershell
pip install -r requirements_eval.txt
```

#### Or Install Everything:
```powershell
pip install -r requirements.txt -r requirements_frontend.txt -r requirements_eval.txt
```

### 4. Prepare Documents

Create a `documents/` folder and add `.txt` files:

```powershell
mkdir documents
# Add your .txt files to the documents/ folder
```

**Example document** (`documents/policy.txt`):
```
Refund Policy
=============
We offer full refunds within 30 days of purchase.
No questions asked!

Shipping Information
===================
Standard shipping: 3-5 business days
Express shipping: 1-2 business days
```

### 5. Start Ollama

```powershell
ollama serve
```

In another terminal, ensure model is available:
```powershell
ollama pull llama3.2:1b
```

---

## 🚀 Running the Application

### Option 1: Local Development (Recommended for Testing)

#### Start the API:
```powershell
uvicorn RAG_API:app --reload
```
- API: http://127.0.0.1:8000
- Docs: http://127.0.0.1:8000/docs

#### Start the Frontend (new terminal):
```powershell
streamlit run RAG_Frontend.py
```
- Frontend: http://localhost:8501

### Option 2: Docker Deployment (Production)

#### Build and Start:
```powershell
docker-compose up -d
```

#### View Logs:
```powershell
docker-compose logs -f
```

#### Stop Services:
```powershell
docker-compose down
```

#### Access:
- API: http://localhost:8000/docs
- Frontend: http://localhost:8501

---

## 📖 Usage Examples

### Using the API (curl)

#### Standard RAG Query:
```powershell
curl -X POST "http://127.0.0.1:8000/ask" `
  -H "Content-Type: application/json" `
  -d '{"question": "What is the refund policy?", "use_multi_query": true}'
```

#### Agent Query (with Tools):
```powershell
curl -X POST "http://127.0.0.1:8000/agent" `
  -H "Content-Type: application/json" `
  -d '{"question": "Calculate 15% of 200 and tell me if its covered by refund policy"}'
```

#### Health Check:
```powershell
curl http://127.0.0.1:8000/health
```

### Using the Frontend

1. Open http://localhost:8501
2. Choose mode: "Standard RAG" or "Agent with Tools"
3. Type your question
4. View answer, sources, and metadata
5. Try example questions from sidebar

### Using Python Requests

```python
import requests

# Standard RAG
response = requests.post(
    "http://127.0.0.1:8000/ask",
    json={"question": "What is the shipping time?", "use_multi_query": True}
)
print(response.json())

# Agent with Tools
response = requests.post(
    "http://127.0.0.1:8000/agent",
    json={"question": "What's 20% tip on $85?"}
)
print(response.json())
```

---

## 🔬 Evaluation

Run the evaluation script to measure RAG performance:

```powershell
python RAG_Evaluation.py
```

This will:
1. Load your RAG system
2. Run test questions
3. Measure Ragas metrics:
   - Faithfulness
   - Answer Relevancy
   - Context Relevancy
   - Context Recall
4. Save results to `evaluation_results.csv`

### Interpreting Results

| Score | Quality | Action |
|-------|---------|--------|
| 0.0-0.4 | Poor | Needs significant improvement |
| 0.4-0.6 | Fair | Room for improvement |
| 0.6-0.8 | Good | Decent performance |
| 0.8-1.0 | Excellent | High quality |

---

## 🎯 API Endpoints

### `GET /`
Root endpoint with API information

### `GET /health`
Health check - returns API status and configuration

### `POST /ask`
Standard RAG query with multi-query retrieval

**Request:**
```json
{
  "question": "What is the refund policy?",
  "use_multi_query": true
}
```

**Response:**
```json
{
  "answer": "Refunds are processed within 30 days...",
  "sources": ["policy.txt"],
  "num_chunks_used": 3
}
```

### `POST /agent`
Agent query with tool access

**Request:**
```json
{
  "question": "Calculate 15% of 200"
}
```

**Response:**
```json
{
  "answer": "Result: 30.0",
  "mode": "agent",
  "tools_available": ["calculator", "knowledge_base_search"]
}
```

---

## 🏗️ Architecture

```
┌─────────────────────┐
│   Streamlit UI      │
│   (Port 8501)       │
└──────────┬──────────┘
           │ HTTP
           ▼
┌─────────────────────┐
│   FastAPI Backend   │
│   (Port 8000)       │
│                     │
│  ┌───────────────┐  │
│  │ Multi-Query   │  │
│  │ Retrieval     │  │
│  └───────────────┘  │
│                     │
│  ┌───────────────┐  │
│  │ Agent + Tools │  │
│  │ - Calculator  │  │
│  │ - KB Search   │  │
│  └───────────────┘  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   FAISS Vector DB   │
│   (In-memory)       │
└─────────────────────┘
           │
           ▼
┌─────────────────────┐
│   Ollama LLM        │
│   (llama3.2:1b)     │
│   (Port 11434)      │
└─────────────────────┘
```

---

## 📂 Project Structure

```
LangChain/
├── RAG_API.py                  # FastAPI backend with RAG logic
├── RAG_Frontend.py             # Streamlit web interface
├── RAG_Evaluation.py           # Ragas evaluation script
├── requirements.txt            # API dependencies
├── requirements_frontend.txt   # Frontend dependencies
├── requirements_eval.txt       # Evaluation dependencies
├── Dockerfile                  # Docker image for API
├── Dockerfile.frontend         # Docker image for frontend
├── docker-compose.yml          # Multi-container orchestration
├── .dockerignore              # Docker ignore patterns
├── README_DEPLOYMENT.md        # This file
└── documents/                  # Your knowledge base (.txt files)
    ├── policy.txt
    └── faq.txt
```

---

## 🔧 Configuration

### Changing the LLM Model

In `RAG_API.py`, modify:
```python
llm = ChatOllama(
    model="llama3.2:1b",  # Change to: "llama2", "mistral", etc.
    temperature=0
)
```

### Adjusting Retrieval Settings

```python
retriever = vectorstore.as_retriever(
    k=3  # Number of chunks to retrieve (increase for more context)
)
```

### Multi-Query Settings

```python
def generate_multi_queries(question: str, num_queries: int = 3):
    # Change num_queries to generate more/fewer variations
```

---

## 🐛 Troubleshooting

### API Won't Start
- ✅ Check Ollama is running: `ollama serve`
- ✅ Check model exists: `ollama list`
- ✅ Check port 8000 is free: `netstat -ano | findstr :8000`

### No Documents Loaded
- ✅ Create `documents/` folder
- ✅ Add `.txt` files to the folder
- ✅ Check file encoding (UTF-8 recommended)

### Frontend Can't Connect
- ✅ Ensure API is running on port 8000
- ✅ Check API health: http://127.0.0.1:8000/health
- ✅ Restart both services

### Docker Issues
- ✅ Ensure Docker Desktop is running
- ✅ Check Ollama is accessible: `ollama list`
- ✅ Check container logs: `docker-compose logs`

### Evaluation Fails
- ✅ Install ragas: `pip install ragas`
- ✅ Ensure documents exist in `documents/` folder
- ✅ Check Ollama is running

---

## 🚀 Deployment Checklist

- [ ] Documents folder populated with `.txt` files
- [ ] Ollama installed and model pulled
- [ ] Dependencies installed (`requirements.txt`)
- [ ] API runs locally (`uvicorn RAG_API:app`)
- [ ] Frontend runs locally (`streamlit run RAG_Frontend.py`)
- [ ] Evaluation completed successfully
- [ ] Docker images build (`docker-compose build`)
- [ ] Docker containers run (`docker-compose up -d`)
- [ ] Health checks pass
- [ ] API docs accessible at `/docs`
- [ ] Frontend accessible and functional

---

## 📝 Resume-Ready Features

Highlight these on your resume/portfolio:

✅ **Advanced RAG Implementation**
- Multi-query retrieval for improved accuracy
- FAISS vector store for efficient similarity search
- Free, local LLM deployment with Ollama

✅ **Agent & Tool Integration**
- Calculator and knowledge base tools
- Dynamic tool selection based on query
- ReAct pattern agent implementation

✅ **Production Architecture**
- RESTful API with FastAPI
- Interactive UI with Streamlit
- Containerized with Docker
- Health monitoring and logging

✅ **Quality Assurance**
- Automated evaluation with Ragas
- Multiple quality metrics (faithfulness, relevance, recall)
- Documented performance benchmarks

✅ **Full-Stack ML System**
- Backend API development
- Frontend UI development
- Model evaluation pipeline
- Deployment infrastructure

---

## 🎓 Next Steps

### Enhancements to Consider:
1. **Add More Tools**
   - Web search (SerpAPI, DuckDuckGo)
   - SQL database query
   - Weather API
   - Custom business logic tools

2. **Improve Retrieval**
   - Hybrid search (keyword + semantic)
   - Reranking with cross-encoders
   - Query expansion techniques
   - Parent document retrieval

3. **Production Features**
   - User authentication (JWT tokens)
   - Rate limiting
   - Caching (Redis)
   - Async processing (Celery)
   - Database for conversation history

4. **Monitoring & Observability**
   - LangSmith for tracing
   - Prometheus metrics
   - Grafana dashboards
   - Error tracking (Sentry)

5. **Cloud Deployment**
   - AWS ECS/Fargate
   - Google Cloud Run
   - Azure Container Apps
   - Kubernetes (Helm charts)

---

## 📚 Resources

- **LangChain Docs**: https://python.langchain.com/
- **Ollama**: https://ollama.ai/
- **FAISS**: https://github.com/facebookresearch/faiss
- **Ragas**: https://docs.ragas.io/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Streamlit**: https://streamlit.io/

---

## 📄 License

This project is for educational purposes. Modify and use as needed for your learning journey!

---

## 🤝 Contributing

This is a learning project! Feel free to:
- Add new features
- Improve documentation
- Fix bugs
- Share improvements

---

## 💬 Support

Having issues? Here's how to get help:

1. Check the **Troubleshooting** section above
2. Review the API docs at `/docs`
3. Check Ollama status: `ollama list`
4. Verify Docker containers: `docker-compose ps`
5. Check logs: `docker-compose logs -f`

---

Built with ❤️ for AI learning
