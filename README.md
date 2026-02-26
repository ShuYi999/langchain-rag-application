# 🤖 LangChain RAG Projects

A collection of **Retrieval Augmented Generation (RAG)** systems demonstrating different capabilities with LLMs and VLMs.

## 📁 Project Structure

```
LangChain/
├── RAG_LLM/           # Standard RAG with Text-Only LLM
├── RAG_VLM/           # Multimodal RAG with Vision Language Model
├── venv/              # Shared Python virtual environment
├── documents/         # Original sample documents
└── README.md          # This file
```

## 🚀 Projects

### 1. RAG_LLM - Text-Based RAG System

**Location:** `RAG_LLM/`

A production-ready RAG system for text documents using:
- **Model:** llama3.2:1b (Language Model)
- **Vector DB:** FAISS
- **Features:**
  - ✅ Text document Q&A
  - ✅ Multi-query retrieval
  - ✅ Agent with tools (calculator + knowledge base)
  - ✅ FastAPI backend
  - ✅ Streamlit frontend
  - ✅ Docker deployment
  - ✅ Evaluation with Ragas metrics

**Use Cases:**
- Document Q&A systems
- Knowledge base search
- Policy/procedure lookup
- FAQ systems

**Quick Start:**
```powershell
cd RAG_LLM
.\start.ps1
```

**Documentation:**
- [README_DEPLOYMENT.md](RAG_LLM/README_DEPLOYMENT.md) - Full documentation
- [QUICKSTART.md](RAG_LLM/QUICKSTART.md) - 5-minute guide

---

### 2. RAG_VLM - Multimodal RAG with Vision

**Location:** `RAG_VLM/`

Advanced RAG system with **vision capabilities** using:
- **Model:** llava:7b (Vision Language Model) + llama3.2:1b
- **Vector DB:** FAISS
- **Features:**
  - ✅ Text document Q&A (like RAG_LLM)
  - ✅ **Image analysis** (NEW!)
  - ✅ **Multimodal queries** (text + image) (NEW!)
  - ✅ FastAPI backend with image upload
  - ✅ Streamlit frontend with image support

**Use Cases:**
- Product inspection + policy check
- Visual quality control
- Image-based customer support
- Document processing with images
- OCR + knowledge base integration

**Quick Start:**
```powershell
cd RAG_VLM
.\start.ps1
```

**Documentation:**
- [README.md](RAG_VLM/README.md) - Full documentation
- [QUICKSTART.md](RAG_VLM/QUICKSTART.md) - 5-minute guide

---

## 🆚 Comparison

| Feature | RAG_LLM | RAG_VLM |
|---------|---------|---------|
| **Input Types** | Text only | Text + Images |
| **Main Model** | llama3.2:1b (1GB) | llava:7b (4GB) |
| **RAM Required** | 2-4 GB | 6-8 GB |
| **Speed** | Fast (2-5s) | Slower (10-30s) |
| **Use Cases** | Text Q&A | Visual analysis + text |
| **Complexity** | Simple | Advanced |
| **Best For** | Learning RAG basics | Multimodal applications |

## 🛠️ Prerequisites

### Both Projects Need:
- **Python 3.11+**
- **Ollama** - https://ollama.ai
- **Virtual environment** (shared `venv/`)

### Models Required:

**For RAG_LLM:**
```powershell
ollama pull llama3.2:1b    # ~1 GB
```

**For RAG_VLM (additional):**
```powershell
ollama pull llava:7b       # ~4 GB
```

## 📚 Learning Path

### Beginner → Advanced

1. **Start with RAG_LLM**
   - Learn RAG fundamentals
   - Understand embeddings, vector stores
   - Master text-based retrieval

2. **Upgrade to RAG_VLM**
   - Add vision capabilities
   - Understand multimodal processing
   - Build advanced use cases

## 🔧 Setup

### 1. Install Ollama & Models

```powershell
# Install Ollama from https://ollama.ai

# Pull models
ollama pull llama3.2:1b    # For both projects
ollama pull llava:7b       # For RAG_VLM only
```

### 2. Create Virtual Environment (if not exists)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Choose Your Project

**Option A: Text-Only RAG**
```powershell
cd RAG_LLM
pip install -r requirements.txt -r requirements_frontend.txt
.\start.ps1
```

**Option B: Multimodal RAG**
```powershell
cd RAG_VLM
pip install -r requirements.txt -r requirements_frontend.txt
.\start.ps1
```

## 📖 Documentation

Each project has its own complete documentation:

- **RAG_LLM:**
  - [README_DEPLOYMENT.md](RAG_LLM/README_DEPLOYMENT.md)
  - [QUICKSTART.md](RAG_LLM/QUICKSTART.md)

- **RAG_VLM:**
  - [README.md](RAG_VLM/README.md)
  - [QUICKSTART.md](RAG_VLM/QUICKSTART.md)

## 🎯 What You'll Learn

### Core RAG Concepts
- Embeddings and vector representations
- Vector databases (FAISS)
- Similarity search
- Retrieval-augmented generation
- Multi-query retrieval techniques

### LLM Integration
- Using Ollama for local LLMs
- Prompt engineering
- Context management
- Tool integration (agents)

### Vision Capabilities (RAG_VLM)
- Vision Language Models (VLMs)
- Multimodal embeddings
- Image understanding
- Combining visual + textual context

### Production Practices
- FastAPI backend development
- Streamlit UI creation
- Docker containerization
- Health checks and monitoring
- Evaluation metrics (Ragas)

## 🚀 Quick Commands

### RAG_LLM
```powershell
cd RAG_LLM
.\start.ps1                                    # Interactive menu
uvicorn RAG_API:app --reload                   # API only
streamlit run RAG_Frontend.py                  # Frontend only
docker-compose up -d                           # Docker deployment
```

### RAG_VLM
```powershell
cd RAG_VLM
.\start.ps1                                    # Interactive menu
python -m uvicorn RAG_VLM_API:app --reload    # API only
streamlit run RAG_VLM_Frontend.py             # Frontend only
```

## 💡 Tips

1. **Start simple**: Begin with RAG_LLM to understand basics
2. **Shared venv**: Both projects use the same virtual environment
3. **Documents**: Add your own .txt files to `documents/` in each project
4. **Images**: For RAG_VLM, add test images to `RAG_VLM/images/`
5. **Memory**: RAG_VLM needs more RAM due to vision model

## 🐛 Troubleshooting

**"Model not found"**
```powershell
ollama list                    # Check installed models
ollama pull llama3.2:1b        # Install missing model
ollama pull llava:7b           # For VLM
```

**"Cannot connect to Ollama"**
- Make sure Ollama is running
- Check: http://localhost:11434

**"Out of memory"**
- RAG_LLM: Close other apps (needs ~4GB)
- RAG_VLM: Needs ~8GB, consider upgrading RAM

## 📊 Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | FastAPI, Python 3.11+ |
| **Frontend** | Streamlit |
| **LLM/VLM** | Ollama (llama3.2, llava) |
| **Framework** | LangChain |
| **Vector DB** | FAISS |
| **Containerization** | Docker, Docker Compose |
| **Evaluation** | Ragas |

## 🎓 Use This for...

- **Learning**: Understand RAG and multimodal AI
- **Portfolio**: Showcase ML/AI skills
- **Prototyping**: Quick MVP for RAG applications
- **Research**: Experiment with different models
- **Production**: Deploy with Docker

## 📝 License

Free to use for learning and personal projects.

---

**GitHub:** [Your Repository](https://github.com/ShuYi999/langchain-rag-application)

Built with ❤️ using LangChain, Ollama, and FAISS | 100% Free & Local
