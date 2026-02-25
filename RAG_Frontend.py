"""
Streamlit Frontend for RAG Knowledge Base API

This provides a user-friendly web interface for:
- Asking questions to the RAG system
- Using agent mode with tools (calculator, knowledge base)
- Viewing sources and metadata
- Testing multi-query retrieval

Run with: streamlit run RAG_Frontend.py
Make sure RAG_API.py is running on http://127.0.0.1:8000
"""

import streamlit as st
import requests
import json
from typing import Dict, Any

# Configuration
API_URL = "http://127.0.0.1:8000"

# Page config
st.set_page_config(
    page_title="RAG Knowledge Base",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .question-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .answer-box {
        background-color: #e8f4f8;
        color: #1a1a1a;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #1f77b4;
        font-size: 1.1rem;
        line-height: 1.6;
    }
    .source-badge {
        background-color: #1f77b4;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        margin: 0.25rem;
        display: inline-block;
    }
    </style>
    """, unsafe_allow_html=True)


def check_api_health() -> Dict[str, Any]:
    """Check if the API is running and healthy"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            return {"status": "healthy", "data": response.json()}
        else:
            return {"status": "unhealthy", "error": f"Status code: {response.status_code}"}
    except requests.exceptions.ConnectionError:
        return {"status": "unreachable", "error": "Cannot connect to API. Is it running?"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def ask_rag(question: str, use_multi_query: bool = True) -> Dict[str, Any]:
    """Send question to RAG endpoint"""
    try:
        response = requests.post(
            f"{API_URL}/ask",
            json={"question": question, "use_multi_query": use_multi_query},
            timeout=30
        )
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": f"Status code: {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def ask_agent(question: str) -> Dict[str, Any]:
    """Send question to agent endpoint"""
    try:
        response = requests.post(
            f"{API_URL}/agent",
            json={"question": question},
            timeout=30
        )
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": f"Status code: {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ===== MAIN APP =====

# Header
st.markdown('<p class="main-header">🤖 RAG Knowledge Base Assistant</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # API Health Check
    st.subheader("API Status")
    health = check_api_health()
    
    if health["status"] == "healthy":
        st.success("✅ API is running")
        with st.expander("API Details"):
            st.json(health["data"])
    elif health["status"] == "unreachable":
        st.error("❌ API is not running")
        st.info("Start the API with:\n```\nuvicorn RAG_API:app --reload\n```")
    else:
        st.warning(f"⚠️ API status: {health['status']}")
        st.text(health.get("error", "Unknown error"))
    
    st.divider()
    
    # Mode selection
    st.subheader("Query Mode")
    mode = st.radio(
        "Choose how to process your question:",
        ["Standard RAG", "Agent with Tools"],
        help="Standard RAG: Direct document retrieval\nAgent: Can use calculator and knowledge base"
    )
    
    # Multi-query option (only for Standard RAG)
    if mode == "Standard RAG":
        use_multi_query = st.checkbox(
            "Enable Multi-Query Retrieval",
            value=True,
            help="Generate multiple query variations for better retrieval"
        )
    
    st.divider()
    
    # Example questions
    st.subheader("💡 Example Questions")
    
    if mode == "Standard RAG":
        examples = [
            "What is the refund policy?",
            "Tell me about shipping times",
            "What are the warranty terms?",
        ]
    else:
        examples = [
            "Calculate 15% tip on $85",
            "What's 20% of 250?",
            "If 3 items cost $49.99 each, what's the total?",
        ]
    
    for example in examples:
        if st.button(example, key=f"example_{example}", use_container_width=True):
            st.session_state.example_question = example

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Ask a Question")
    
    # Check if example was clicked
    default_question = st.session_state.get("example_question", "")
    if default_question:
        question = st.text_area(
            "Your question:",
            value=default_question,
            height=100,
            placeholder="Type your question here..."
        )
        # Clear the example after using it
        st.session_state.example_question = ""
    else:
        question = st.text_area(
            "Your question:",
            height=100,
            placeholder="Type your question here..."
        )
    
    # Submit button
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
    
    with col_btn1:
        submit_button = st.button("🚀 Ask Question", type="primary", use_container_width=True)
    
    with col_btn2:
        clear_button = st.button("🗑️ Clear", use_container_width=True)
    
    if clear_button:
        st.session_state.clear()
        st.rerun()
    
    # Process question
    if submit_button and question.strip():
        if health["status"] != "healthy":
            st.error("❌ Cannot submit question. API is not healthy.")
        else:
            with st.spinner("🔍 Processing your question..."):
                # Choose endpoint based on mode
                if mode == "Standard RAG":
                    result = ask_rag(question, use_multi_query)
                else:
                    result = ask_agent(question)
                
                # Store in session state
                st.session_state.last_result = result
                st.session_state.last_question = question
                st.session_state.last_mode = mode
    
    # Display results
    if "last_result" in st.session_state and st.session_state.last_result:
        result = st.session_state.last_result
        
        st.divider()
        st.subheader("📝 Answer")
        
        if result.get("success"):
            data = result["data"]
            
            # Display answer
            st.markdown(f'<div class="answer-box">{data.get("answer", "No answer")}</div>', 
                       unsafe_allow_html=True)
            
            # Display metadata
            st.subheader("📊 Metadata")
            
            if st.session_state.last_mode == "Standard RAG":
                col_meta1, col_meta2 = st.columns(2)
                
                with col_meta1:
                    st.metric("Chunks Used", data.get("num_chunks_used", 0))
                
                with col_meta2:
                    st.metric("Sources", len(data.get("sources", [])))
                
                # Display sources
                if data.get("sources"):
                    st.subheader("📚 Sources")
                    cols = st.columns(min(len(data["sources"]), 3))
                    for idx, source in enumerate(data["sources"]):
                        with cols[idx % 3]:
                            st.markdown(
                                f'<span class="source-badge">{source}</span>', 
                                unsafe_allow_html=True
                            )
            else:
                # Agent mode
                st.info(f"🤖 Mode: {data.get('mode', 'agent')}")
                with st.expander("Available Tools"):
                    for tool in data.get("tools_available", []):
                        st.write(f"- {tool}")
        else:
            st.error(f"❌ Error: {result.get('error', 'Unknown error')}")

with col2:
    st.header("📖 How It Works")
    
    if mode == "Standard RAG":
        st.markdown("""
        **Standard RAG Process:**
        
        1. 📝 Your question is received
        2. 🔄 Multiple query variations generated
        3. 🔍 Searches document database
        4. 📚 Retrieves relevant chunks
        5. 🤖 LLM generates answer using context
        6. ✅ Returns answer with sources
        """)
    else:
        st.markdown("""
        **Agent with Tools:**
        
        1. 📝 Your question is received
        2. 🤔 Agent analyzes what's needed
        3. 🔧 Chooses appropriate tool(s):
           - Calculator for math
           - Knowledge base for docs
        4. 🔄 Can use multiple tools
        5. 🤖 Synthesizes final answer
        6. ✅ Returns comprehensive result
        """)
    
    st.divider()
    
    st.header("🎯 Features")
    st.markdown("""
    - ✅ Multi-query retrieval
    - ✅ Calculator tool
    - ✅ Knowledge base search
    - ✅ Source tracking
    - ✅ Real-time processing
    """)
    
    st.divider()
    
    # Statistics
    if "last_result" in st.session_state:
        st.header("📈 Session Stats")
        
        # Simple stats counter
        if "query_count" not in st.session_state:
            st.session_state.query_count = 0
        
        if submit_button and question.strip():
            st.session_state.query_count += 1
        
        st.metric("Questions Asked", st.session_state.query_count)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>Built with ❤️ using FastAPI, LangChain, FAISS, Ollama & Streamlit</p>
    <p>API Docs: <a href='http://127.0.0.1:8000/docs' target='_blank'>http://127.0.0.1:8000/docs</a></p>
</div>
""", unsafe_allow_html=True)
