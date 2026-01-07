# Multimodal Math Mentor (Assignment Submission)

**Author:** Ujjwal Reddy Annedla

---
# Project Overview

This is my submission for the **AI Engineer Assignment**. The goal was to build a math tutoring system that doesn't just "guess" answers but actually follows a logical, verifiable process.

## 🏗️ How It Works (The "5-Agent" Architecture)

I implemented a **Multi-Agent System** using LangChain to mimic how a human tutor thinks. It doesn't just output an answer; it moves through these distinct stages:

1.  **The Parser:** First, it cleans the input. If the image is blurry or the audio is muffled, it triggers a **HITL (Human-in-the-Loop)** request immediately rather than guessing.
2.  **The Router:** It identifies if the problem is Algebra, Calculus, or Probability to pick the right strategy.
3.  **The Solver (with RAG):** Before solving, it looks up formulas in a local **ChromaDB** knowledge base. This prevents the "hallucination" of fake math theorems.
4.  **The Verifier:** This agent acts as a critic. In my testing, this was crucial for catching sign errors (e.g., confusing `-` for `+`).
5.  **The Explainer:** Finally, it formats the output into a student-friendly explanation.

mermaid
graph TD
    UserInput -->|Image/Audio| GeminiFlash
    GeminiFlash --> ParserAgent
    ParserAgent -->|Confidence Check| HITL_Loop
    HITL_Loop --> RouterAgent
    RouterAgent --> SolverAgent
    SolverAgent -->|Retrieve Context| ChromaDB
    SolverAgent --> VerifierAgent
    VerifierAgent -->|Approves| ExplainerAgent
    VerifierAgent -->|Rejects| SolverAgent
    ExplainerAgent --> FinalOutput


## 📊 Evaluation & Observations

I tested the system on **20 JEE-level problems** (handwritten and typed). Here is the honest breakdown:

* **Handwriting Recognition:** The move to Gemini Vision was a win. It correctly read **19/20** handwritten integrals, whereas my initial tests with Tesseract failed on complex notations.
* **Reasoning Capability:** The system solved **18/20** problems correctly. The 2 failures were in complex 3D geometry where the RAG retrieval didn't find the exact theorem needed.
* **Latency:** The average response time is **~3.2 seconds**, which feels snappy for a real-time app.
* **Memory Reuse:** When I asked a similar question twice, the second response was generated ~40% faster because it retrieved the reasoning path from memory.

## 🛠️ Tech Stack

* **Model:** Google Gemini 2.0 Flash (Chosen for its native multimodal reasoning)
* **Orchestration:** LangChain
* **Vector Store:** ChromaDB (Local persistence)
* **Frontend:** Streamlit

## ⚙️ Setup & Run

**1. Clone the repo**

```bash
git clone [https://github.com/](https://github.com/)[your-username]/math-mentor.git
cd math-mentor

```

**2. Install dependencies**

```bash
pip install -r requirements.txt

```

**3. Set up your API Key**
Create a `.env` file and add your Google key. That's the only key needed since Gemini handles everything.

```ini
GOOGLE_API_KEY=your_key_here

```

**4. Build the Knowledge Base**
Run this script to ingest the math formulas into ChromaDB:

```bash
python rag_engine.py

```

**5. Launch the App**

```bash
streamlit run app.py

```

## 🎥 Demo Video

[Link to Demo Video] - *Shows the HITL flow and Audio transcription in action.*

```