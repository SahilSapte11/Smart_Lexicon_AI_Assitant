import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import json
from dotenv import load_dotenv
import os

# Configure Gemini API
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)  # Replace with your Gemini API key
model = genai.GenerativeModel('models/gemini-1.5-pro-latest')

def extract_content(url):
    """
    Extracts the text content and metadata from a given URL and returns it as a JSON object.
    
    Args:
        url (str): The URL of the website to scrape.
    
    Returns:
        dict: A dictionary containing the title, metadata, and text content.
    """
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes (4xx, 5xx)
        
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract the title of the page
        title = soup.title.string if soup.title else "No Title Found"
        
        # Extract metadata (e.g., description, keywords)
        metadata = {}
        meta_tags = soup.find_all('meta')
        for tag in meta_tags:
            if 'name' in tag.attrs:
                metadata[tag.attrs['name']] = tag.attrs.get('content', '')
            elif 'property' in tag.attrs:
                metadata[tag.attrs['property']] = tag.attrs.get('content', '')
        
        # Extract all text content from the page
        for element in soup(['script', 'style', 'head', 'title', 'meta', 'link', 'footer', 'nav']):
            element.decompose()  # Remove unnecessary elements
        
        text_content = soup.get_text(separator='\n', strip=True)  # Get clean text content
        
        # Return the content as a dictionary
        return {
            'title': title,
            'metadata': metadata,
            'text_content': text_content
        }
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None

def format_with_gemini(json_content, custom_requirement, chat_history=None):
    """
    Formats the JSON content using Gemini based on custom requirement, optionally using chat history.

    Args:
        json_content (dict): The scraped content from the webpage.
        custom_requirement (str): The user's instruction.
        chat_history (list, optional): Previous chat messages to provide context.

    Returns:
        str: Gemini's formatted output in human language.
    """
    try:
        # Build base prompt
        prompt = f"""
Here is the JSON content extracted from a webpage:
{json.dumps(json_content, indent=4, ensure_ascii=False)}

The user has provided the following custom requirement:
"{custom_requirement}"
"""

        # Add context from chat history (e.g., previous assistant response)
        if chat_history:
            previous_answers = [
                msg["content"] for msg in reversed(chat_history)
                if msg["role"] == "assistant"
            ]
            if previous_answers:
                last_answer = previous_answers[0]
                prompt += f'\nFor context, here is the previous assistant response:\n"{last_answer}"\n'

        prompt += "\nPlease format or adjust the content accordingly."

        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        print(f"Error formatting with Gemini: {e}")
        return None


# Main script
if __name__ == "__main__":
    # Get user inputs
    url = input("Enter the URL to scrape: ")
    custom_requirement = input("Enter your custom requirement for formatting: ")
    
    # Extract content from the URL 
    content = extract_content(url)
    
    if content:
        # Format the content using Gemini
        formatted_output = format_with_gemini(content, custom_requirement)
        
        if formatted_output:
            print("\nFormatted Output:")
            print(formatted_output)
        else:
            print("Failed to format the content with Gemini.")
    else:
        print("Failed to scrape the content.")