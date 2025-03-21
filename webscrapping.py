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

def format_with_gemini(json_content, custom_requirement):
    """
    Sends the JSON content and custom requirement to the Gemini model for formatting.
    
    Args:
        json_content (dict): The JSON content to be formatted.
        custom_requirement (str): The user's custom requirement for formatting.
    
    Returns:
        str: The formatted output from the Gemini model.
    """
    try:
        # Create the prompt for Gemini
        prompt = f"""
        Here is the JSON content extracted from a webpage:
        {json.dumps(json_content, indent=4,ensure_ascii=False)}

        The user has provided the following custom requirement for formatting:
        {custom_requirement}

        Please format the JSON content according to the user's requirement.
        """
        
        # Send the prompt to the Gemini model
        response = model.generate_content(prompt)
        
        # Return the formatted output
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