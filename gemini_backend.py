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
def get_gemini_response(user_query, chat_history=None):
    try:
        prompt = ""

        if chat_history:
            # Get the last 3 assistant messages (most recent first)
            assistant_msgs = [
                msg["content"] for msg in chat_history
                if msg["role"] == "assistant"
            ][-3:]  # Take last 3

            if assistant_msgs:
                prompt += "Here are some previous assistant responses for context:\n"
                for i, msg in enumerate(assistant_msgs, 1):
                    prompt += f"{i}. {msg}\n"

        # Add the user's message
        prompt += f"\nNow the user says:\n\"{user_query}\"\n"
        prompt += "Please generate an appropriate and context-aware response."

        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        return f"Error: {e}"

