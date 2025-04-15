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

def query_rag(question, chat_history=None):
    """
    Queries the RAG system with a user question and optional chat history for context.

    Args:
        question (str): The user's question.
        chat_history (list, optional): Chat history to extract previous assistant responses.

    Returns:
        str: The RAG-generated response.
    """
    try:
        # Build enriched question with chat history if available
        enriched_prompt = ""

        if chat_history:
            assistant_msgs = [
                msg["content"] for msg in chat_history
                if msg["role"] == "assistant"
            ][-3:]  # Last 3 assistant replies

            if assistant_msgs:
                enriched_prompt += "Previous assistant responses for context:\n"
                for i, msg in enumerate(assistant_msgs, 1):
                    enriched_prompt += f"{i}. {msg}\n"

        # Add the new user question
        enriched_prompt += f"\nUser's current question:\n{question}"

        response = rag_chain.invoke(enriched_prompt)
        return response.strip()

    except Exception as e:
        return f"Error: {str(e)}"
