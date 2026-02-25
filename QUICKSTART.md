# 🚀 Quick Reference Guide

## Installation (One-Time Setup)

```powershell
# 1. Install dependencies
pip install -r requirements.txt -r requirements_frontend.txt

# 2. Install and setup Ollama
# Download from: https://ollama.ai
ollama pull llama3.2:1b

# 3. Add documents
mkdir documents
# Add .txt files to documents/ folder
```

## Running the Application

### Method 1: Quick Start Script (Easiest)
```powershell
.\start.ps1
```

### Method 2: Manual Start

**Terminal 1 - API:**
```powershell
uvicorn RAG_API:app --reload
```

**Terminal 2 - Frontend:**
```powershell
streamlit run RAG_Frontend.py
```

**Terminal 3 - Evaluation:**
```powershell
python RAG_Evaluation.py
```

### Method 3: Docker (Production)
```powershell
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Access Points

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:8501 |
| **API** | http://127.0.0.1:8000 |
| **API Docs** | http://127.0.0.1:8000/docs |

## API Examples

### Standard RAG Query
```powershell
curl -X POST "http://127.0.0.1:8000/ask" `
  -H "Content-Type: application/json" `
  -d '{"question": "What is the refund policy?", "use_multi_query": true}'
```

### Agent Query (with Calculator)
```powershell
curl -X POST "http://127.0.0.1:8000/agent" `
  -H "Content-Type: application/json" `
  -d '{"question": "Calculate 15% of 200"}'
```

### Health Check
```powershell
curl http://127.0.0.1:8000/health
```

## Key Features

### ✅ Multi-Query Retrieval
Automatically generates multiple query variations to find more relevant documents.

### ✅ Agent with Tools
- **Calculator**: Performs math calculations
- **Knowledge Base**: Searches your documents

### ✅ Evaluation with Ragas
Measures RAG quality with 4 key metrics:
- Faithfulness
- Answer Relevancy
- Context Relevancy
- Context Recall

## Troubleshooting

| Problem | Solution |
|---------|----------|
| API won't start | Check Ollama is running: `ollama serve` |
| No documents loaded | Add .txt files to `documents/` folder |
| Frontend can't connect | Ensure API is running on port 8000 |
| Evaluation fails | Install ragas: `pip install ragas` |

## File Structure

```
├── RAG_API.py              # Main API (FastAPI)
├── RAG_Frontend.py         # Web UI (Streamlit)
├── RAG_Evaluation.py       # Evaluation script (Ragas)
├── requirements.txt        # API dependencies
├── requirements_frontend.txt # Frontend dependencies
├── requirements_eval.txt   # Evaluation dependencies
├── docker-compose.yml      # Docker orchestration
├── start.ps1              # Quick start script
└── documents/             # Your .txt files here
```

## What You've Built

🎯 **Production-Ready Features:**
1. ✅ Advanced RAG with multi-query retrieval
2. ✅ Tool integration (calculator, knowledge base)
3. ✅ Interactive web interface
4. ✅ Automated evaluation pipeline
5. ✅ Docker containerization
6. ✅ API documentation
7. ✅ Health monitoring

🎓 **Resume Highlights:**
- Built production RAG system from scratch
- Implemented agent with tool integration
- Created full-stack ML application (API + Frontend)
- Established evaluation pipeline with Ragas
- Containerized and deployed with Docker
- Used LangChain, FAISS, Ollama, FastAPI, Streamlit

---

**Next Steps:**
- Deploy to cloud (AWS, GCP, Azure)
- Add more tools (web search, SQL, etc.)
- Implement user authentication
- Add conversation history
- Create Helm charts for Kubernetes
- Set up CI/CD pipeline

For detailed documentation, see: [README_DEPLOYMENT.md](README_DEPLOYMENT.md)
