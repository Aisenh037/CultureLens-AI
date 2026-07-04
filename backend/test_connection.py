import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load settings from the local .env file
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
model_name = os.getenv("GEMINI_MODEL", "models/gemini-3.5-flash")

print("==================================================")
print("       CultureLens AI - API Connection Test       ")
print("==================================================")
print(f"Loaded API Key: {api_key[:12] if api_key else 'None'}...")
print(f"Loaded Model:   {model_name}")
print("Connecting to Google Gemini API...")

if not api_key:
    print("[ERROR] GEMINI_API_KEY is not defined in backend/.env!")
    exit(1)

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    
    # Send a simple query to verify model communication
    response = model.generate_content("Say 'CultureLens API is fully active!' in a short sentence.")
    
    print("\n[SUCCESS] Model responded successfully!")
    print(f"Response text: \"{response.text.strip()}\"\n")
    print("Your environment configuration is verified and working!")
except Exception as e:
    print("\n[CONNECTION FAILURE] Could not connect or retrieve response from the Gemini API.")
    print(f"Error Details: {str(e)}\n")
    print("Please verify that your key is valid and you have remaining quota on your free tier.")
