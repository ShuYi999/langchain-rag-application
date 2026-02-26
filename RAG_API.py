"""
FastAPI RAG API - Production-Style Backend
Using LangChain + FAISS + Ollama (FREE!)

This API:
1. Loads documents once at startup (efficient!)
2. Provides a REST endpoint to ask questions
3. Returns answers based on your document knowledge base

Run with: uvicorn RAG_API:app --reload
Access docs at: http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import os

from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.tools import tool
import re

# Get Ollama host from environment (for Docker compatibility)
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")


# -----------------------------
# 1. Initialize FastAPI
# -----------------------------
app = FastAPI(
    title="RAG Knowledge Base API",
    description="Ask questions about company policies using RAG",
    version="1.0.0"
)


# -----------------------------
# 2. Load documents at startup from folder
# -----------------------------
def load_documents() -> List[Document]:
    """
    Load all .txt files from the documents/ folder.
    Each file becomes a Document with metadata.
    """
    docs = []
    folder_path = "documents/"
    
    print(f"📂 Loading documents from {folder_path}...")
    
    if not os.path.exists(folder_path):
        print(f"❌ Folder {folder_path} not found!")
        return docs
    
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            filepath = os.path.join(folder_path, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
                docs.append(
                    Document(
                        page_content=text,
                        metadata={"source": filename}
                    )
                )
            print(f"  ✓ Loaded: {filename}")
    
    print(f"✅ Loaded {len(docs)} documents")
    return docs


# -----------------------------
# 3. Build RAG components (embeddings + FAISS)
# -----------------------------
def create_vectorstore(docs: List[Document]):
    """
    Takes documents, chunks them, embeds them, and creates a FAISS vectorstore.
    This happens once at startup.
    """
    print("🔨 Creating vector store...")
    
    # Chunk documents (good practice even for small files)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(docs)
    print(f"  ✓ Split into {len(chunks)} chunks")
    
    # Embeddings model (using free Ollama)
    embeddings = OllamaEmbeddings(model="llama3.2:1b", base_url=OLLAMA_HOST)
    print(f"  ✓ Initialized embeddings model (host: {OLLAMA_HOST})")
    
    # Build vectorstore with FAISS
    vectorstore = FAISS.from_documents(chunks, embeddings)
    print(f"  ✓ FAISS vector store created")
    
    print("✅ Vector store ready!")
    return vectorstore


# -----------------------------
# 4. Startup Event: Load docs + Create retriever + LLM
#    This runs ONCE when the server starts
# -----------------------------
print("\n" + "="*60)
print("🚀 STARTING RAG API SERVER")
print("="*60)

# Load documents from folder
docs = load_documents()

if not docs:
    print("⚠️  WARNING: No documents loaded! Place .txt files in documents/ folder")

# Create vector store
vectorstore = create_vectorstore(docs)

# Create retriever (will fetch top 3 most relevant chunks)
retriever = vectorstore.as_retriever(k=3)

# Initialize LLM (using free Ollama)
llm = ChatOllama(
    model="llama3.2:1b",
    temperature=0,  # Deterministic answers
    base_url=OLLAMA_HOST
)
print(f"✅ LLM initialized (host: {OLLAMA_HOST})")

# Agent will be initialized lazily when needed
agent_executor = None  # Initialized on first use of /agent endpoint

# Create prompt template
prompt_template = ChatPromptTemplate.from_template("""
You are a helpful assistant.
Answer the question ONLY using the context below.
If the answer is not present in the context, say:
"I don't know based on the provided documents."

Context:
{context}

Question:
{question}

Answer:""")

print("="*60)
print("✅ RAG API SERVER READY!")
print("📖 API Docs: http://127.0.0.1:8000/docs")
print("="*60 + "\n")


# -----------------------------
# 5. Multi-Query Retrieval (Query Rewriting)
# -----------------------------
def generate_multi_queries(question: str, num_queries: int = 3) -> List[str]:
    """
    Generate multiple variations of the original question.
    This helps retrieve more diverse and relevant documents.
    """
    multi_query_prompt = ChatPromptTemplate.from_template("""
You are an AI assistant helping to improve search results.
Generate {num_queries} different versions of the given question to retrieve relevant documents.
Each version should approach the question from a different angle or use different wording.

Original question: {question}

Provide {num_queries} alternative questions, one per line, without numbering:""")
    
    prompt = multi_query_prompt.invoke({
        "question": question,
        "num_queries": num_queries
    })
    
    result = llm.invoke(prompt)
    
    # Parse the generated queries (split by newlines and filter empty)
    queries = [q.strip() for q in result.content.split('\n') if q.strip()]
    
    # Add original question as first query
    all_queries = [question] + queries[:num_queries-1]
    
    print(f"  🔄 Generated {len(all_queries)} query variations:")
    for i, q in enumerate(all_queries, 1):
        print(f"     {i}. {q}")
    
    return all_queries


def retrieve_with_multi_query(question: str) -> List[Document]:
    """
    Retrieve documents using multiple query variations.
    Combines results and removes duplicates.
    """
    # Generate multiple query variations
    queries = generate_multi_queries(question)
    
    # Retrieve documents for each query
    all_docs = []
    seen_contents = set()
    
    for query in queries:
        docs = retriever.invoke(query)
        for doc in docs:
            # Deduplicate based on content
            if doc.page_content not in seen_contents:
                all_docs.append(doc)
                seen_contents.add(doc.page_content)
    
    print(f"  📚 Retrieved {len(all_docs)} unique chunks")
    return all_docs


# -----------------------------
# 5b. Tool Integration (Calculator)
# -----------------------------
@tool
def calculator(expression: str) -> str:
    """
    Evaluates mathematical expressions. 
    Useful for: arithmetic, percentages, algebraic calculations.
    Input should be a valid Python mathematical expression.
    Example: "25 * 4 + 10" or "(100 - 20) / 2"
    """
    try:
        # Remove any text, keep only mathematical expression
        # Clean the expression for safety
        expression = expression.strip()
        
        # Only allow safe mathematical operations
        allowed_chars = set('0123456789+-*/().%** ')
        if not all(c in allowed_chars for c in expression):
            return "Error: Invalid characters in expression. Only use numbers and operators: + - * / ( ) ** %"
        
        # Evaluate the expression
        result = eval(expression, {"__builtins__": {}}, {})
        return f"Result: {result}"
    except Exception as e:
        return f"Error calculating: {str(e)}"


@tool  
def knowledge_base_search(query: str) -> str:
    """
    Searches the company knowledge base for information.
    Use this to answer questions about company policies, procedures, or documents.
    Input should be a clear question or search query.
    """
    try:
        # Use the existing retriever
        docs = retriever.invoke(query)
        if not docs:
            return "No relevant information found in the knowledge base."
        
        # Combine top results
        context = "\n\n".join([doc.page_content for doc in docs[:3]])
        sources = [doc.metadata.get("source", "unknown") for doc in docs]
        
        return f"Found information from: {', '.join(set(sources))}\n\nContent:\n{context}"
    except Exception as e:
        return f"Error searching knowledge base: {str(e)}"


# Create tools list
tools = [calculator, knowledge_base_search]


# -----------------------------
# 5c. Agent Setup (Tool-Using RAG)
# -----------------------------
def create_agent():
    """
    Create an agent that can use tools (calculator, knowledge base search).
    This allows the RAG system to dynamically choose whether to:
    - Search documents
    - Perform calculations
    - Or both
    """
    agent_prompt = ChatPromptTemplate.from_template("""
You are a helpful assistant with access to tools.

Answer the following question as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}
""")
    
    agent = create_react_agent(llm, tools, agent_prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=5,
        handle_parsing_errors=True
    )
    
    return agent_executor


# -----------------------------
# 6. RAG Function (core logic with multi-query)
# -----------------------------
def rag_answer(question: str, use_multi_query: bool = True) -> dict:
    """
    The RAG pipeline:
    1. Retrieve relevant document chunks (with optional multi-query)
    2. Build prompt with context
    3. Get answer from LLM
    4. Return answer with sources
    """
    # Step 1: Retrieve relevant chunks
    if use_multi_query:
        retrieved_docs = retrieve_with_multi_query(question)
    else:
        retrieved_docs = retriever.invoke(question)
    
    # Step 2: Combine into context
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])
    
    # Step 3: Build prompt
    prompt = prompt_template.invoke({
        "context": context,
        "question": question
    })
    
    # Step 4: Get answer from LLM
    result = llm.invoke(prompt)
    
    # Step 5: Prepare response with sources
    sources = [doc.metadata.get("source", "unknown") for doc in retrieved_docs]
    
    return {
        "answer": result.content,
        "sources": list(set(sources)),  # Unique sources
        "num_chunks_used": len(retrieved_docs)
    }


def agent_answer(question: str) -> dict:
    """
    Use the agent to answer questions.
    The agent can dynamically choose to:
    - Search the knowledge base
    - Use the calculator
    - Or combine multiple tools
    """
    global agent_executor
    
    # Lazy initialization of agent
    if agent_executor is None:
        print("🔨 Initializing agent on first use...")
        agent_executor = create_agent()
        print("✅ Agent initialized")
    
    try:
        result = agent_executor.invoke({"input": question})
        
        return {
            "answer": result.get("output", "No answer generated"),
            "mode": "agent",
            "tools_available": [tool.name for tool in tools]
        }
    except Exception as e:
        return {
            "answer": f"Error using agent: {str(e)}",
            "mode": "agent",
            "tools_available": [tool.name for tool in tools]
        }


# -----------------------------
# 7. API Request/Response Models
# -----------------------------
class QuestionRequest(BaseModel):
    """Request body for asking a question"""
    question: str
    use_multi_query: bool = True  # Enable multi-query retrieval by default
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is the refund policy?",
                "use_multi_query": True
            }
        }


class AnswerResponse(BaseModel):
    """Response with answer and metadata"""
    answer: str
    sources: List[str]
    num_chunks_used: int


class AgentResponse(BaseModel):
    """Response from agent with tools"""
    answer: str
    mode: str
    tools_available: List[str]


# -----------------------------
# 8. API Endpoints
# -----------------------------
@app.get("/")
def root():
    """Root endpoint - basic info"""
    return {
        "message": "RAG Knowledge Base API with Tools",
        "docs": "/docs",
        "endpoints": {
            "ask": "POST /ask - Ask a question (standard RAG with multi-query)",
            "agent": "POST /agent - Ask a question (agent with tools: calculator, knowledge base)",
            "health": "GET /health - Check API status"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "documents_loaded": len(docs),
        "model": "llama3.2:1b",
        "vector_store": "FAISS"
    }


@app.post("/ask", response_model=AnswerResponse)
def ask_question(request: QuestionRequest):
    """
    Main RAG endpoint - ask a question and get an answer
    
    The question is:
    1. Optionally rewritten into multiple query variations (multi-query retrieval)
    2. Converted to vector(s) and used to search for relevant document chunks
    3. Chunks are sent to LLM as context
    4. LLM generates an answer based on the context
    """
    print(f"\n📥 Question received: {request.question}")
    print(f"🔄 Multi-query mode: {request.use_multi_query}")
    
    answer_data = rag_answer(request.question, use_multi_query=request.use_multi_query)
    
    print(f"📤 Answer: {answer_data['answer'][:100]}...")
    print(f"📚 Sources: {answer_data['sources']}")
    
    return answer_data


@app.post("/agent", response_model=AgentResponse)
def ask_agent(request: QuestionRequest):
    """
    Agent endpoint - uses tools to answer questions
    
    The agent can:
    - Search the knowledge base for documents
    - Perform mathematical calculations
    - Combine multiple tools to solve complex queries
    
    Example questions:
    - "What is 25% of the refund amount mentioned in the policy?"
    - "Calculate the total if I buy 3 items at $49.99 each"
    - "What's the shipping time and how much would 5 orders cost at $10 each?"
    """
    print(f"\n🤖 Agent question received: {request.question}")
    
    answer_data = agent_answer(request.question)
    
    print(f"📤 Agent answer: {answer_data['answer'][:100]}...")
    
    return answer_data


# -----------------------------
# 9. Run Instructions
# -----------------------------
if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Starting server...")
    print("📖 Access API docs at: http://127.0.0.1:8000/docs")
    print("🔗 Or test at: http://127.0.0.1:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
