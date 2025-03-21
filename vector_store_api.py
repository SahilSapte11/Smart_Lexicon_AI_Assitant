import os
import tempfile
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Google Gemini Embeddings
gemini_embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

# Initialize ChromaDB vector store
chroma_db_path = "chroma_db"
if not os.path.exists(chroma_db_path):
    os.makedirs(chroma_db_path)

def upload_pdf_to_chroma(uploaded_file):
    """
    Processes the uploaded PDF file, splits the text, generates embeddings,
    and stores them in ChromaDB.
    """
    try:
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name

        # Extract text from the PDF
        pdf_reader = PdfReader(tmp_file_path)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        # Clean up the temporary file
        os.unlink(tmp_file_path)

        # Split the text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text)

        # Generate embeddings and store in ChromaDB
        vector_store = Chroma.from_texts(
            texts=chunks,
            embedding=gemini_embeddings,
            persist_directory=chroma_db_path
        )
        vector_store.persist()

        return "PDF successfully uploaded and indexed in ChromaDB!"

    except Exception as e:
        return f"Error: {str(e)}"