import json
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from rag_engine import retrieve_context

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash", 
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

def search_memory(query):
    """Retrieves similar past problems."""
    try:
        if os.path.exists("memory.json"):
            with open("memory.json", "r") as f:
                memories = json.load(f)
            relevant = [m for m in memories if any(w in m['question'] for w in query.split() if len(w) > 4)]
            if relevant:
                return f"Similar Problem: {relevant[-1]['question']}\nExplanation: {relevant[-1]['explanation']}"
    except:
        pass
    return "No similar past problems found."

class MathAgents:
    def parser_agent(self, text):
        # ... (Same prompt as before) ...
        prompt = PromptTemplate(
            input_variables=["input"],
            template="""
            You are a Math Parser. Input: {input}
            Task: Clean text, identify topic. If no question, assume 'Solve'.
            Output strictly valid JSON: {{"problem_text": "...", "topic": "...", "needs_clarification": bool}}
            """
        )
        try:
            response = (prompt | llm).invoke({"input": text})
            return json.loads(response.content.replace("```json", "").replace("```", "").strip())
        except:
            return {"problem_text": text, "topic": "Unknown", "needs_clarification": False}

    def router_agent(self, topic):
        allowed = ["algebra", "calculus", "probability", "linear algebra", "geometry", "statistics"]
        return "PROCEED" if any(t in topic.lower() for t in allowed) else "FLAG"

    def solver_agent(self, problem, context, memory):
        prompt = PromptTemplate(
            input_variables=["problem", "context", "memory"],
            template="Role: Math Mentor. Context: {context}. Memory: {memory}. Problem: {problem}. Solve step-by-step."
        )
        return (prompt | llm).invoke({"problem": problem, "context": context, "memory": memory}).content

    def verifier_agent(self, problem, solution):
        prompt = PromptTemplate(
            input_variables=["problem", "solution"],
            template="Verify solution. Output 'VERIFIED' or 'REJECTED: reason'.\nProblem: {problem}\nSolution: {solution}"
        )
        return (prompt | llm).invoke({"problem": problem, "solution": solution}).content

    def explainer_agent(self, solution):
        prompt = PromptTemplate(
            input_variables=["solution"],
            template="Explain simply:\n{solution}"
        )
        return (prompt | llm).invoke({"solution": solution}).content

def run_pipeline(raw_text):
    agents = MathAgents()
    trace = [] # <--- NEW: Log agent actions for the UI
    
    # 1. PARSE
    parsed = agents.parser_agent(raw_text)
    if not parsed: parsed = {"problem_text": raw_text, "topic": "Unknown", "needs_clarification": False}
    
    trace.append(f"✅ Parser: Identified topic '{parsed.get('topic')}'")
    
    if parsed.get("needs_clarification"):
        return {"status": "HITL", "msg": "Ambiguous Input", "trace": trace}
    
    # 2. ROUTE
    route = agents.router_agent(parsed.get("topic", ""))
    trace.append(f"✅ Router: Action '{route}'")
    
    # 3. MEMORY
    problem_text = parsed.get("problem_text", raw_text)
    memory_context = search_memory(problem_text)
    if "No similar" not in memory_context:
        trace.append("🧠 Memory: Found similar past problem.")
    else:
        trace.append("🧠 Memory: No relevant history found.")

    # 4. SOLVE
    context = retrieve_context(problem_text)
    trace.append(f"📚 RAG: Retrieved {len(context.split())} chars of context.")
    
    solution = agents.solver_agent(problem_text, context, memory_context)
    trace.append("⚙️ Solver: Generated solution.")
    
    # 5. VERIFY
    check = agents.verifier_agent(problem_text, solution)
    confidence = 0.0
    if "VERIFIED" in check:
        trace.append("✅ Verifier: Solution approved.")
        confidence = 0.95 # High confidence
    else:
        trace.append(f"⚠️ Verifier: Flagged issue - {check}")
        confidence = 0.60 # Lower confidence, might trigger HITL warning
        # We don't stop strictly here to let user see the attempt, but we flag it.
    
    # 6. EXPLAIN
    final = agents.explainer_agent(solution)
    trace.append("🎓 Explainer: Formatted output.")

    return {
        "status": "SUCCESS", 
        "solution": solution, 
        "explanation": final, 
        "context": context,
        "trace": trace,           # <--- For UI Trace Panel
        "confidence": confidence  # <--- For UI Confidence Indicator
    }