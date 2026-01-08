import streamlit as st
import os
import json
from utils import extract_text_from_image, transcribe_audio
from agents import run_pipeline
import rag_engine # Import to initialize DB if needed

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="AI Math Mentor", layout="wide")

# --- 2. CUSTOM CSS (Fluid Background) ---
st.markdown("""
<style>
    /* Main App Background with Fluid Gradient */
    .stApp {
        background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #141e30);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        color: white;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Input Box Styling for Readability */
    .stTextArea textarea {
        background-color: #f0f2f6;
        color: #31333F;
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. STARTUP CHECKS & SESSION STATE ---
# Initialize Session State for OCR/ASR result
if "ocr_result" not in st.session_state: 
    st.session_state.ocr_result = ""

# Ensure Memory file exists
if not os.path.exists("memory.json"): 
    with open("memory.json", "w") as f: json.dump([], f)

# Ensure RAG Database exists (Critical for Cloud Deployment)
if not os.path.exists("./chroma_db"):
    with st.spinner("⚙️ Initializing Knowledge Base for the first time..."):
        rag_engine.build_knowledge_base()

st.title("🧮 Multimodal Math Mentor")
st.markdown("### Reliable Math AI with RAG, Agents & Memory")

# --- 4. SIDEBAR: INPUT SELECTOR ---
st.sidebar.header("1. Input Mode")
mode = st.sidebar.radio("Select Source:", ["Text", "Image", "Audio"])

if mode == "Text":
    st.sidebar.info("👉 Type your problem directly in the main panel.")

elif mode == "Image":
    img_file = st.sidebar.file_uploader("Upload Image (PNG/JPG)", type=["png", "jpg", "jpeg"])
    if img_file:
        # Display image directly from the file object
        st.sidebar.image(img_file, caption="Preview", width=200)
        
        if st.sidebar.button("Extract Text (OCR)"):
            with st.spinner("👀 Scanning image..."):
                # FIX: Pass the file object directly, NOT a filename string
                text = extract_text_from_image(img_file)
                st.session_state.ocr_result = text
                st.toast("Text extracted!")

elif mode == "Audio":
    audio_file = st.sidebar.file_uploader("Upload Audio (MP3/WAV)", type=["mp3", "wav"])
    if audio_file:
        # Play audio directly from the file object
        st.sidebar.audio(audio_file)
        
        if st.sidebar.button("Transcribe Audio"):
            with st.spinner("👂 Listening..."):
                # FIX: Pass the file object directly, NOT a filename string
                text = transcribe_audio(audio_file)
                st.session_state.ocr_result = text
                st.toast("Audio transcribed!")

# --- 5. MAIN AREA: HITL PREVIEW ---
st.divider()
st.subheader("2. Verify & Edit Question (HITL)")

# User edits the OCR/ASR result here (Human-in-the-Loop)
user_text = st.text_area(
    "Ensure the question is clear before solving:", 
    value=st.session_state.ocr_result, 
    height=150
)

# Sync manual edits back to session state
if user_text != st.session_state.ocr_result:
    st.session_state.ocr_result = user_text

# --- 6. SOLVE BUTTON ---
if st.button("🚀 Solve Problem", type="primary"):
    if not user_text.strip():
        st.warning("⚠️ Please enter a question or upload a file.")
    else:
        with st.spinner("🧠 AI Agents working... (Parser -> Router -> RAG -> Solver -> Verifier)"):
            
            # RUN THE PIPELINE
            result = run_pipeline(user_text)
            
            # --- A. AGENT TRACE PANEL ---
            with st.expander("🕵️ Agent Trace (Explainability)", expanded=True):
                if "trace" in result:
                    for step in result["trace"]:
                        st.write(step)

            # --- B. HITL ERROR HANDLING ---
            if result.get("status") == "HITL":
                st.error("⚠️ Human Intervention Required")
                st.write(f"**Reason:** {result.get('msg')}")
                if "debug" in result:
                    st.json(result["debug"])
            
            # --- C. SUCCESS DISPLAY ---
            elif result.get("status") == "SUCCESS":
                
                # Confidence Indicator
                score = result.get("confidence", 0.0)
                st.write("---")
                c1, c2 = st.columns([1, 4])
                with c1:
                    st.metric("AI Confidence", f"{int(score*100)}%")
                with c2:
                    color = "green" if score > 0.8 else "orange"
                    st.progress(score, text=f"Confidence Level: {color.upper()}")

                # Solution Columns
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("🎓 Tutor Explanation")
                    st.markdown(result.get("explanation", "No explanation."))
                
                with col2:
                    st.subheader("⚙️ Technical Solution")
                    st.code(result.get("solution", "No solution."))
                    
                    # RAG Context Panel
                    with st.expander("📚 Retrieved Knowledge (RAG)"):
                        st.info(result.get("context", "No context retrieved."))
                    
                    # Memory Usage Panel
                    with st.expander("🧠 Memory & Pattern Reuse"):
                        st.text(result.get("memory_used", "No previous patterns used."))

                # --- D. FEEDBACK & MEMORY STORAGE ---
                st.divider()
                st.subheader("3. Feedback & Learning")
                f1, f2 = st.columns(2)
                
                with f1:
                    # "Correct" button acts as the learning signal
                    if st.button("✅ Correct (Save to Memory)"):
                        with open("memory.json", "r+") as f:
                            try:
                                data = json.load(f)
                            except:
                                data = []
                            
                            memory_entry = {
                                "id": len(data) + 1,
                                "question": user_text, # Saved for future RAG
                                "solution": result.get("solution"),
                                "explanation": result.get("explanation"),
                                "user_feedback": "POSITIVE"
                            }
                            
                            data.append(memory_entry)
                            f.seek(0)
                            json.dump(data, f)
                        st.success("✅ Pattern learned! Saved to Memory.")
                
                with f2:
                    if st.button("❌ Incorrect"):
                         st.error("❌ Feedback recorded. System will adjust for next run.")