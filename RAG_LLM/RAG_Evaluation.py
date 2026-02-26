"""
RAG Evaluation with Ragas

This script evaluates the RAG system using Ragas metrics:
- Answer Faithfulness: Is the answer grounded in the retrieved context?
- Context Relevance: Are the retrieved chunks relevant to the question?
- Answer Relevance: Does the answer address the question?
- Context Recall: Does the context contain information needed to answer?

Install Ragas: pip install ragas

Run with: python RAG_Evaluation.py
"""

import os
from typing import List, Dict
from datasets import Dataset

# Ragas imports
try:
    from ragas import evaluate
    from ragas.metrics import (
        faithfulness,
        answer_relevancy,
        context_relevancy,
        context_recall
    )
    RAGAS_AVAILABLE = True
except ImportError:
    print("⚠️  Ragas not installed. Install with: pip install ragas")
    RAGAS_AVAILABLE = False

# LangChain imports
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document


# -----------------------------
# 1. Load and Setup RAG Components
# -----------------------------
def setup_rag_system():
    """Set up the RAG system for evaluation"""
    print("🔨 Setting up RAG system...")
    
    # Load documents
    docs = []
    folder_path = "documents/"
    
    if not os.path.exists(folder_path):
        print(f"❌ Folder {folder_path} not found!")
        return None, None, None
    
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            filepath = os.path.join(folder_path, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
                docs.append(Document(page_content=text, metadata={"source": filename}))
    
    print(f"  ✓ Loaded {len(docs)} documents")
    
    # Create chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
    chunks = splitter.split_documents(docs)
    print(f"  ✓ Split into {len(chunks)} chunks")
    
    # Create vector store
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    retriever = vectorstore.as_retriever(k=3)
    print(f"  ✓ Vector store created")
    
    # Create LLM
    llm = ChatOllama(model="llama3.2:1b", temperature=0)
    print(f"  ✓ LLM initialized")
    
    print("✅ RAG system ready!\n")
    return retriever, llm, chunks


def generate_answer(question: str, retriever, llm) -> Dict[str, any]:
    """Generate answer using RAG pipeline"""
    from langchain_core.prompts import ChatPromptTemplate
    
    # Retrieve documents
    retrieved_docs = retriever.invoke(question)
    
    # Build context
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])
    
    # Create prompt
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
    
    prompt = prompt_template.invoke({"context": context, "question": question})
    
    # Get answer
    result = llm.invoke(prompt)
    
    return {
        "answer": result.content,
        "contexts": [doc.page_content for doc in retrieved_docs],
        "question": question
    }


# -----------------------------
# 2. Create Test Dataset
# -----------------------------
def create_test_dataset() -> List[Dict[str, any]]:
    """
    Create a test dataset with questions and ground truth answers.
    In production, you'd have human-annotated ground truth answers.
    """
    test_cases = [
        {
            "question": "What is the refund policy?",
            "ground_truth": "Refunds are processed within 30 days of return."
        },
        {
            "question": "How long does shipping take?",
            "ground_truth": "Shipping takes 3-5 business days for standard delivery."
        },
        {
            "question": "What are the warranty terms?",
            "ground_truth": "The product comes with a 1-year limited warranty."
        },
        {
            "question": "Can I cancel my order?",
            "ground_truth": "Orders can be cancelled within 24 hours of placement."
        },
        {
            "question": "What payment methods are accepted?",
            "ground_truth": "We accept credit cards, PayPal, and bank transfers."
        }
    ]
    
    return test_cases


# -----------------------------
# 3. Run Evaluation
# -----------------------------
def evaluate_rag_system():
    """Main evaluation function"""
    
    if not RAGAS_AVAILABLE:
        print("❌ Cannot run evaluation without Ragas")
        print("Install with: pip install ragas")
        return
    
    print("="*60)
    print("🔬 RAG SYSTEM EVALUATION WITH RAGAS")
    print("="*60 + "\n")
    
    # Setup RAG
    retriever, llm, chunks = setup_rag_system()
    
    if retriever is None:
        print("❌ Failed to set up RAG system")
        return
    
    # Create test dataset
    print("📝 Creating test dataset...")
    test_cases = create_test_dataset()
    print(f"  ✓ Created {len(test_cases)} test cases\n")
    
    # Generate answers for all test cases
    print("🤖 Generating answers for test cases...")
    evaluation_data = []
    
    for idx, test_case in enumerate(test_cases, 1):
        print(f"  Processing {idx}/{len(test_cases)}: {test_case['question'][:50]}...")
        
        result = generate_answer(test_case["question"], retriever, llm)
        
        evaluation_data.append({
            "question": result["question"],
            "answer": result["answer"],
            "contexts": result["contexts"],
            "ground_truth": test_case["ground_truth"]
        })
    
    print("  ✓ All answers generated\n")
    
    # Convert to Ragas dataset format
    print("📊 Preparing evaluation dataset...")
    dataset = Dataset.from_list(evaluation_data)
    
    # Define metrics to evaluate
    metrics = [
        faithfulness,          # Is answer faithful to context?
        answer_relevancy,      # Is answer relevant to question?
        context_relevancy,     # Are contexts relevant to question?
        context_recall         # Does context have info to answer?
    ]
    
    # Run evaluation
    print("\n🔬 Running Ragas evaluation...")
    print("  (This may take a few minutes...)\n")
    
    try:
        results = evaluate(
            dataset,
            metrics=metrics,
            llm=llm,
            embeddings=OllamaEmbeddings(model="nomic-embed-text")
        )
        
        # Display results
        print("="*60)
        print("📊 EVALUATION RESULTS")
        print("="*60)
        print("\n📈 Overall Metrics:")
        print(f"  • Faithfulness:       {results['faithfulness']:.3f}")
        print(f"  • Answer Relevancy:   {results['answer_relevancy']:.3f}")
        print(f"  • Context Relevancy:  {results['context_relevancy']:.3f}")
        print(f"  • Context Recall:     {results['context_recall']:.3f}")
        
        # Interpretation guide
        print("\n📖 Interpretation Guide:")
        print("  0.0 - 0.4: Poor - Needs significant improvement")
        print("  0.4 - 0.6: Fair - Room for improvement")
        print("  0.6 - 0.8: Good - Decent performance")
        print("  0.8 - 1.0: Excellent - High quality")
        
        # Detailed results
        print("\n📋 Detailed Results:")
        results_df = results.to_pandas()
        print(results_df.to_string(index=False))
        
        # Save results
        results_df.to_csv("evaluation_results.csv", index=False)
        print("\n💾 Results saved to: evaluation_results.csv")
        
        print("\n" + "="*60)
        print("✅ EVALUATION COMPLETE!")
        print("="*60)
        
        return results
        
    except Exception as e:
        print(f"\n❌ Evaluation failed: {str(e)}")
        print("\nTroubleshooting:")
        print("  1. Ensure Ollama is running: ollama serve")
        print("  2. Ensure llama3.2:1b model is available: ollama pull llama3.2:1b")
        print("  3. Check that documents/ folder has .txt files")
        return None


# -----------------------------
# 4. Manual Evaluation Helper
# -----------------------------
def manual_evaluation_template():
    """
    Template for manual evaluation.
    Use this to create human-evaluated ground truth.
    """
    print("\n📝 MANUAL EVALUATION TEMPLATE")
    print("="*60)
    print("""
For each question, evaluate:

1. Answer Faithfulness (0-5):
   - Is the answer supported by the retrieved context?
   - Are there hallucinations?

2. Context Relevance (0-5):
   - Are the retrieved chunks relevant to the question?
   - Is there too much irrelevant information?

3. Answer Relevance (0-5):
   - Does the answer address the question?
   - Is it complete and accurate?

4. Context Recall (0-5):
   - Does the context contain all necessary information?
   - Is anything important missing?

Save your evaluations in a CSV file with columns:
question, answer, faithfulness, context_relevance, answer_relevance, context_recall, notes
    """)


# -----------------------------
# 5. Main Execution
# -----------------------------
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Evaluate RAG system with Ragas")
    parser.add_argument(
        "--manual-template",
        action="store_true",
        help="Show manual evaluation template"
    )
    
    args = parser.parse_args()
    
    if args.manual_template:
        manual_evaluation_template()
    else:
        # Run automatic evaluation
        evaluate_rag_system()
