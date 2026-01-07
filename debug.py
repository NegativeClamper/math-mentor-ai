import os
from dotenv import load_dotenv
import google.generativeai as genai
from agents import run_pipeline

# 1. Check Environment
print("--- DIAGNOSTIC START ---")
load_dotenv()
key = os.getenv("GOOGLE_API_KEY")

if not key:
    print("❌ CRITICAL: GOOGLE_API_KEY is missing from environment.")
    print("   Please create a .env file with your key.")
    exit()
else:
    print(f"✅ API Key found: {key[:5]}...{key[-3:]}")

# 2. Test Connection (Simple Ping)
print("\n--- TESTING GEMINI CONNECTION ---")
try:
    genai.configure(api_key=key)
    # Using the exact model from your previous successful list
    model = genai.GenerativeModel('gemini-2.0-flash') 
    response = model.generate_content("Say 'Hello' if you can hear me.")
    print(f"✅ Gemini Responded: {response.text.strip()}")
except Exception as e:
    print(f"❌ Connection Failed: {e}")
    exit()

# 3. Test Full Pipeline
print("\n--- TESTING AGENT PIPELINE ---")
test_problem = "Solve x + 5 = 10"
print(f"Input: {test_problem}")

try:
    result = run_pipeline(test_problem)
    print("\n✅ RAW RESULT FROM PIPELINE:")
    print(result)
    
    status = result.get("status")
    print(f"\nStatus Key: {status}")
    if status not in ["SUCCESS", "HITL"]:
        print("❌ ERROR: Status key is missing or invalid! This is why Streamlit shows nothing.")
    else:
        print("✅ Pipeline logic is valid. If this works, the issue is in app.py.")
        
except Exception as e:
    print(f"\n❌ PIPELINE CRASHED: {e}")
    import traceback
    traceback.print_exc()

print("\n--- DIAGNOSTIC END ---")