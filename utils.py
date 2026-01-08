import os
import google.generativeai as genai
import tempfile
from PIL import Image

# Configure API Key securely
if "GOOGLE_API_KEY" in os.environ:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

def extract_text_from_image(image_file):
    """
    Uses Gemini 2.0 Flash Vision.
    Accepts the 'image_file' directly from st.file_uploader (BytesIO),
    skipping the need to save 'temp.png' to disk.
    """
    try:
        # Load directly from memory
        img = Image.open(image_file)
        
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content([
            "Transcribe the math problem in this image exactly into text/LaTeX. Do not solve it yet.", 
            img
        ])
        return response.text
    except Exception as e:
        return f"Error extracting text: {e}"

def transcribe_audio(audio_bytes):
    """
    Uses Gemini 2.0 Flash Audio.
    Writes audio to a safe temporary file (required for genai.upload_file),
    then uploads it to Gemini.
    """
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Create a temporary file in a directory we are ALLOWED to write to
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
            temp_audio.write(audio_bytes.read())
            temp_path = temp_audio.name

        try:
            # Upload to Gemini (it needs a file path)
            gemini_file = genai.upload_file(path=temp_path, mime_type="audio/mp3")
            
            response = model.generate_content([
                "Listen to this audio and transcribe the math question exactly.",
                gemini_file
            ])
            return response.text
            
        finally:
            # Clean up: delete the temp file from the server
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as e:
        return f"Error transcribing audio: {e}"