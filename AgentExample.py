from langchain_core.prompts import PromptTemplate
from langchain_community.chat_models import ChatOllama
from langchain_core.tools import tool

# ============ DEFINE TOOLS ============

@tool
def calculator(expression: str) -> str:
    """Performs mathematical calculations.
    Use this when you need to solve math problems or calculate numbers.
    Input should be a valid Python math expression like '5 + 3' or '100 - 75'.
    
    Examples:
    - "5 + 3" returns "8"
    - "100 * 2" returns "200"
    """
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return f"Calculation result: {result}"
    except Exception as e:
        return f"Error calculating: {str(e)}"


@tool
def email_rewriter(email_text: str) -> str:
    """Rewrites emails to be more professional and polite.
    Use this when you need to improve the tone or professionalism of an email.
    Input should be the email text that needs to be rewritten.
    """
    # Create a mini-chain for email rewriting
    template = """You are a professional email editor.
Rewrite the following email to be more polite, concise, and professional.

Email:
{email_text}

Professional version:"""
    
    prompt = PromptTemplate(
        input_variables=["email_text"],
        template=template
    )
    
    llm = ChatOllama(model="llama3.2:1b", temperature=0.5)
    chain = prompt | llm
    result = chain.invoke({"email_text": email_text})
    return result.content


# ============ SIMPLE AGENT IMPLEMENTATION ============

class SimpleAgent:
    """A simplified agent that can choose which tool to use.
    
    This demonstrates the KEY DIFFERENCE between chains and agents:
    - CHAIN: Fixed pipeline (always does the same steps)
    - AGENT: Dynamic routing (decides which tool to use based on input)
    """
    
    def __init__(self, llm, tools):
        self.llm = llm
        self.tools = {tool.name: tool for tool in tools}
        
    def run(self, user_input: str):
        """Run the agent with user input."""
        print(f"\n{'='*60}")
        print(f"USER INPUT: {user_input}")
        print(f"{'='*60}\n")
        
        # Step 1: Agent decides which tool to use
        print("STEP 1: Agent analyzes input and chooses tool...")
        decision_prompt = self._create_decision_prompt(user_input)
        decision = self.llm.invoke(decision_prompt).content.strip().lower()
        
        print(f"Agent decision: {decision}\n")
        
        # Step 2: Parse the decision and use the appropriate tool
        if "calculator" in decision:
            # Extract the math expression
            print("STEP 2: Extracting math expression...")
            math_prompt = f"Extract only the mathematical expression from: '{user_input}'. Return just the expression with numbers and operators like '5 + 3'."
            expression = self.llm.invoke(math_prompt).content.strip()
            print(f"→ Tool selected: CALCULATOR")
            print(f"→ Expression: {expression}\n")
            
            print("STEP 3: Executing calculator tool...")
            result = self.tools["calculator"].invoke(expression)
            
        elif "email_rewriter" in decision or "email" in decision or "rewrite" in decision:
            print("STEP 2: Using email rewriter tool...")
            print(f"→ Tool selected: EMAIL_REWRITER\n")
            
            print("STEP 3: Executing email rewriter tool...")
            result = self.tools["email_rewriter"].invoke(user_input)
            
        else:
            # No tool needed, just answer directly
            print("STEP 2: No tool needed")
            print(f"→ Tool selected: NONE (direct LLM answer)\n")
            
            print("STEP 3: Getting direct answer from LLM...")
            result = self.llm.invoke(user_input).content
        
        print(f"\nFINAL RESULT:\n{result}")
        print(f"\n{'='*60}\n")
        return result
    
    def _create_decision_prompt(self, user_input: str):
        """Create a prompt for the agent to decide which tool to use."""
        tools_description = "\n".join([
            f"- {name}: {tool.description}" 
            for name, tool in self.tools.items()
        ])
        
        prompt = f"""You are an AI assistant with access to these tools:

{tools_description}

User request: "{user_input}"

Which tool should you use? Analyze the request carefully.
- If it involves math/calculations, respond with: calculator
- If it involves rewriting/improving email text, respond with: email_rewriter
- If neither applies, respond with: none

Respond with ONLY the tool name.

Decision:"""
        
        return prompt


# ============ CREATE AND TEST THE AGENT ============

print("""
╔══════════════════════════════════════════════════════════════╗
║         AGENT EXAMPLE - Dynamic Tool Selection              ║
╚══════════════════════════════════════════════════════════════╝

In this file, the agent can CHOOSE which tool to use based on the input.
Compare this to PromptOnly.py which uses CHAINS (fixed pipelines).

""")

# Create tools list
tools = [calculator, email_rewriter]

# Create LLM
llm = ChatOllama(model="llama3.2:1b", temperature=0)

# Create agent
agent = SimpleAgent(llm, tools)

# Test 1: Math question (should use calculator)
print("\n🧪 TEST 1: Math Question")
agent.run("What is 156 plus 89?")

# Test 2: Email question (should use email_rewriter)
print("\n🧪 TEST 2: Email Rewriting")
agent.run("hey boss, cant make it today. feeling sick. ttyl")

# Test 3: Another math question
print("\n🧪 TEST 3: Math Question (multiplication)")
agent.run("Calculate the result of 50 multiplied by 12")

# Test 4: General question (might not use any tool)
print("\n🧪 TEST 4: General Question (no tool needed)")
agent.run("What is LangChain?")


print("\n" + "="*60)
print("KEY DIFFERENCES: CHAIN vs AGENT")
print("="*60)
print("""
┌─────────────────────────────────────────────────────────────┐
│ CHAIN (see PromptOnly.py)                                   │
├─────────────────────────────────────────────────────────────┤
│ • Fixed pipeline: Input → Prompt → LLM → Output            │
│ • Always follows the same path                              │
│ • Fast and predictable                                      │
│ • Good for: Specific, well-defined tasks                    │
│                                                             │
│ Example:                                                    │
│   email_chain = prompt | llm                                │
│   # Always does: format prompt → send to LLM               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ AGENT (this file)                                           │
├─────────────────────────────────────────────────────────────┤
│ • Dynamic routing: LLM decides what to do                   │
│ • Can choose between multiple tools                         │
│ • Can use tools multiple times or not at all                │
│ • Good for: Complex, multi-step, varied tasks               │
│                                                             │
│ Example:                                                    │
│   agent = SimpleAgent(llm, [calculator, email_rewriter])    │
│   # Agent thinks → chooses tool → executes → returns        │
└─────────────────────────────────────────────────────────────┘

WHEN TO USE EACH:
─────────────────
Chain:  You know exactly what steps are needed
        Example: "Always rewrite emails"

Agent:  User input varies and requires different actions
        Example: "Help with emails, math, or questions"
""")
