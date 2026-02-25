# -----------------------------
# RAG (Retrieval Augmented Generation) Example
# Using LangChain + FAISS + Ollama (FREE!)
# -----------------------------

"""
What is RAG?
- RAG = Retrieval Augmented Generation
- Instead of the LLM relying only on its training data, it retrieves relevant 
  information from YOUR documents first, then generates an answer based on that.

This solves:
- Hallucinations (making up facts)
- Outdated information
- Domain-specific knowledge the LLM wasn't trained on
"""

# -----------------------------
# 1. Imports
# -----------------------------
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document


# -----------------------------
# 2. Create some sample documents
#    (Pretend these came from PDFs, websites, or databases)
# -----------------------------
print("="*70)
print("STEP 1: Creating Sample Documents")
print("="*70)

documents = [
    Document(page_content="Refunds can be requested within 30 days of purchase."),
    Document(page_content="Shipping usually takes 3–5 business days for local deliveries."),
    Document(page_content="Customers must provide the receipt for any refund request."),
    Document(page_content="Warranty coverage lasts for 2 years from the purchase date."),
    Document(page_content="Damaged items must be reported within 48 hours of delivery.")
]

print(f"Created {len(documents)} documents")
for i, doc in enumerate(documents, 1):
    print(f"  {i}. {doc.page_content}")


# -----------------------------
# 3. Chunking (Breaking documents into smaller pieces)
#    Why? Long documents need to be split for:
#    - Better embedding quality
#    - Retrieve only relevant parts
#    - Stay within context limits
# -----------------------------
print("\n" + "="*70)
print("STEP 2: Chunking Documents")
print("="*70)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,      # Maximum characters per chunk
    chunk_overlap=50     # Overlap to maintain context between chunks
)

docs = text_splitter.split_documents(documents)
print(f"Split into {len(docs)} chunks (in this case, docs were small so no change)")


# -----------------------------
# 4. Create embeddings + FAISS vector store
#    What are embeddings? Numerical representations of text
#    What is FAISS? A vector database for similarity search
# -----------------------------
print("\n" + "="*70)
print("STEP 3: Creating Embeddings & Vector Store")
print("="*70)
print("Converting text to numerical vectors for similarity search...")

embeddings = OllamaEmbeddings(model="llama3.2:1b")

print("Building FAISS vector store...")
vectorstore = FAISS.from_documents(
    docs,
    embedding=embeddings
)

# Create retriever (will fetch top-k most similar documents)
retriever = vectorstore.as_retriever(
    k=3  # Retrieve top 3 most relevant chunks
)

print(f"✓ Vector store created with {len(docs)} document chunks")
print(f"✓ Retriever configured to fetch top 3 relevant documents")


# -----------------------------
# 5. Build the RAG prompt
#    This instructs the LLM to use ONLY the retrieved context
# -----------------------------
print("\n" + "="*70)
print("STEP 4: Creating RAG Prompt Template")
print("="*70)

prompt_template = ChatPromptTemplate.from_template("""
You are a helpful assistant. 
Answer ONLY using the context below.
If the answer is not in the context, say: "I don't know based on the provided documents."

Context:
{context}

Question:
{question}

Answer:""")

print("✓ Prompt template created")


# -----------------------------
# 6. Define the LLM (using free Ollama)
# -----------------------------
print("\n" + "="*70)
print("STEP 5: Initializing LLM")
print("="*70)

llm = ChatOllama(
    model="llama3.2:1b",
    temperature=0  # 0 = deterministic, focused answers
)

print("✓ Using Ollama llama3.2:1b (free local model)")


# -----------------------------
# 7. RAG execution function
#    This is where the magic happens!
# -----------------------------
def rag_answer(question, verbose=True):
    """
    The RAG pipeline:
    1. Retrieve relevant documents based on the question
    2. Format them as context
    3. Send context + question to LLM
    4. Return the answer
    """
    if verbose:
        print(f"\n→ Retrieving relevant documents for: '{question}'")
    
    # Step 1: Retrieve top-k most similar documents
    retrieved_docs = retriever.invoke(question)
    
    if verbose:
        print(f"→ Found {len(retrieved_docs)} relevant chunks:")
        for i, doc in enumerate(retrieved_docs, 1):
            print(f"    {i}. {doc.page_content}")
    
    # Step 2: Merge them into a single context string
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])
    
    # Step 3: Format the prompt with context + question
    prompt = prompt_template.invoke({
        "context": context,
        "question": question
    })
    
    if verbose:
        print(f"→ Sending to LLM with context...")
    
    # Step 4: Call the LLM
    result = llm.invoke(prompt)
    
    return result.content


# -----------------------------
# 8. Test RAG with questions
# -----------------------------
print("\n" + "="*70)
print("STEP 6: Testing RAG System")
print("="*70)

# Question 1: Should find relevant info
print("\n" + "─"*70)
print("Q1: What is the refund policy?")
print("─"*70)
answer1 = rag_answer("What is the refund policy?")
print(f"\nA1: {answer1}")

# Question 2: Should find relevant info
print("\n" + "─"*70)
print("Q2: How long is the warranty?")
print("─"*70)
answer2 = rag_answer("How long is the warranty?")
print(f"\nA2: {answer2}")

# Question 3: NOT in documents (should say "I don't know")
print("\n" + "─"*70)
print("Q3: What is the return address?")
print("─"*70)
answer3 = rag_answer("What is the return address?")
print(f"\nA3: {answer3}")

# Question 4: Shipping question
print("\n" + "─"*70)
print("Q4: How long does shipping take?")
print("─"*70)
answer4 = rag_answer("How long does shipping take?")
print(f"\nA4: {answer4}")


# -----------------------------
# 9. Summary
# -----------------------------
print("\n" + "="*70)
print("RAG PIPELINE SUMMARY")
print("="*70)
print("""
┌──────────────────────────────────────────────────────────────────┐
│ RAG Flow:                                                         │
│                                                                   │
│  User Question                                                    │
│       ↓                                                           │
│  1. Vectorize question → search FAISS for similar documents       │
│       ↓                                                           │
│  2. Retrieve top K relevant document chunks                       │
│       ↓                                                           │
│  3. Create prompt: Context (retrieved docs) + Question            │
│       ↓                                                           │
│  4. Send to LLM → Generate answer based on context                │
│       ↓                                                           │
│  Answer                                                           │
└──────────────────────────────────────────────────────────────────┘

Key Components:
1. Documents - Your knowledge base
2. Text Splitter - Breaks long docs into chunks
3. Embeddings - Converts text to vectors
4. Vector Store (FAISS) - Stores vectors for fast similarity search
5. Retriever - Fetches relevant chunks
6. Prompt Template - Formats context + question
7. LLM - Generates final answer

Benefits of RAG:
✓ LLM answers from YOUR documents (not just training data)
✓ Reduces hallucinations
✓ Easy to update knowledge (just add documents)
✓ Works with small models (context helps them)
✓ Cites sources (you know where answers come from)
""")
