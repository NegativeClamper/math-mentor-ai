import os
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def extract_text_from_image(image_path):
    """
    Uses Gemini 1.5 Flash to see the math problem.
    This works MUCH better than standard OCR for math formulas.
    """
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        img = Image.open(image_path)
        
        # We ask Gemini to just extract the text
        response = model.generate_content([
            "Transcribe the math problem in this image exactly into text/LaTeX. Do not solve it yet.", 
            img
        ])
        return response.text
    except Exception as e:
        return f"Error extracting text: {e}"

def transcribe_audio(audio_path):
    """
    Uses Gemini 1.5 Flash to listen to the audio file.
    """
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Upload the file to Gemini temporarily
        audio_file = genai.upload_file(path=audio_path)
        
        # Prompt it to listen
        response = model.generate_content([
            "Listen to this audio and transcribe the math question exactly.",
            audio_file
        ])
        
        # Clean up: delete the file from cloud storage to save space
        audio_file.delete()
        
        return response.text
    except Exception as e:
        return f"Error transcribing audio: {e}"