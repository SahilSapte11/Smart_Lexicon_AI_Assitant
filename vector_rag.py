import os
from langchain_chroma import Chroma  # Updated import
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
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
vector_store = Chroma(
    persist_directory=chroma_db_path,
    embedding_function=gemini_embeddings
)

# Initialize Google Gemini Chat Model
gemini_chat = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro-latest",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.7
)

# Define the RAG prompt template
rag_prompt = ChatPromptTemplate.from_template(
    """You are a helpful assistant. Use the following context to answer the user's question.
    If you don't know the answer, just say that you don't know. Be concise and accurate.

    Context: {context}

    Question: {question}

    Answer:"""
)

# Define the RAG chain
rag_chain = (
    {"context": vector_store.as_retriever(), "question": RunnablePassthrough()}
    | rag_prompt
    | gemini_chat
    | StrOutputParser()
)

def query_rag(question):
    """
    Queries the RAG system with a user question and returns the generated response.
    """
    try:
        response = rag_chain.invoke(question)
        return response
    except Exception as e:
        return f"Error: {str(e)}"