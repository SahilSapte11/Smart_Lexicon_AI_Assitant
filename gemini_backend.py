import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load API key from .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=api_key)

# Initialize model
model = genai.GenerativeModel("models/gemini-1.5-pro-latest")

# Function to generate response
def get_gemini_response(user_query):
    try:
        response = model.generate_content(user_query)
        return response.text.strip()  # Clean and return response text
    except Exception as e:
        return f"Error: {e}"
