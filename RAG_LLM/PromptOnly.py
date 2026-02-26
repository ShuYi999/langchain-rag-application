from langchain_core.prompts import PromptTemplate
from langchain_community.chat_models import ChatOllama
from langchain_core.tools import tool

# ============ PART 1: EMAIL REWRITER ============

# 1. Define the prompt template
template = """
You are a professional email editor.
Rewrite the following email to sound:
- more polite
- more concise
- suitable for a work environment

Keep the meaning the same.

Email:
{email_text}
"""

prompt = PromptTemplate(
    input_variables=["email_text"],
    template=template,
)

# 2. Define the LLM (using local Ollama model - FREE!)
llm = ChatOllama(
    model="llama3.2:1b",
    temperature=0.5
)

# 3. Create a simple chain using LCEL (LangChain Expression Language)
email_chain = prompt | llm

# 4. Use the chain
user_email = """
hey, i can't make it to the meeting later. got some personal stuff.
can we move it to tomorrow afternoon?
"""

result = email_chain.invoke({"email_text": user_email})

print("=" * 50)
print("PART 1: EMAIL REWRITER")
print("=" * 50)
print("Rewritten email:\n")
print(result.content)


# ============ PART 2: CALCULATOR TOOL ============

# 1. Define a calculator tool
@tool
def calculator(expression: str) -> str:
    """Performs basic mathematical calculations. 
    Use this when you need to calculate numbers.
    Input should be a valid Python mathematical expression like '5 + 3' or '10 * 2'.
    
    Args:
        expression: A mathematical expression as a string
        
    Returns:
        The result of the calculation as a string
    """
    try:
        # Safely evaluate the mathematical expression
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

print("\n" + "=" * 50)
print("PART 2: CALCULATOR TOOL")
print("=" * 50)

# 2. Use the tool directly
print("\n--- Direct Tool Usage ---")
print(f"calculator('25 * 4') = {calculator.invoke('25 * 4')}")
print(f"calculator('150 - 73') = {calculator.invoke('150 - 73')}")
print(f"calculator('(100 + 50) / 3') = {calculator.invoke('(100 + 50) / 3')}")

# 3. Create a chain that uses LLM + Calculator
# The LLM will analyze the question and generate the calculation
math_prompt = PromptTemplate(
    input_variables=["question"],
    template="""You are a math helper. The user asks: {question}

Extract ONLY the mathematical expression that needs to be calculated.
Return ONLY the expression without any explanation.
For example:
- "What is 5 plus 3?" -> "5 + 3"
- "Calculate 10 times 20" -> "10 * 20"

Expression:"""
)

llm = ChatOllama(model="llama3.2:1b", temperature=0)

# Create a chain: user question -> LLM extracts math -> calculator solves it
math_chain = math_prompt | llm

# 4. Use the chain to extract math expressions
print("\n--- LLM + Calculator Chain ---")

question1 = "What is 25 multiplied by 4?"
print(f"\nQuestion: {question1}")
expression1 = math_chain.invoke({"question": question1}).content.strip()
print(f"LLM extracted: {expression1}")
result1 = calculator.invoke(expression1)
print(f"Calculator result: {result1}")

question2 = "If I have 150 dollars and spend 73, how much do I have left?"
print(f"\nQuestion: {question2}")
expression2 = math_chain.invoke({"question": question2}).content.strip()
print(f"LLM extracted: {expression2}")
result2 = calculator.invoke(expression2)
print(f"Calculator result: {result2}")

# 5. Show tool metadata
print("\n--- Tool Information ---")
print(f"Tool name: {calculator.name}")
print(f"Tool description: {calculator.description}")