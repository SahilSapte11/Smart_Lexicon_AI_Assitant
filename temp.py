import streamlit as st
from gemini_backend import get_gemini_response  # Import Gemini integration
from webscrapping import extract_content, format_with_gemini 
# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("🔍 Navigation")
    page = st.radio(
        "Choose a feature:",
        ["🤖 Personalized Chatbot", "📄 Document Upload", "🌐 URL Upload", "📊 Data Analysis", "⚙️ Settings"]
    )

# --- CHAT HISTORY STATE ---
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "chat_history_doc" not in st.session_state:
    st.session_state["chat_history_doc"] = []
if "chat_history_url" not in st.session_state:
    st.session_state["chat_history_url"] = []
if "chat_history_data" not in st.session_state:
    st.session_state["chat_history_data"] = []

# --- CHAT INTERFACE FUNCTION ---
def chat_interface(chat_context):
    st.subheader("💬 Chat with AI")
    
    # Display chat history
    for chat in st.session_state[chat_context]:
        with st.chat_message(chat["role"]):
            st.markdown(chat["content"])

    # User input
    user_input = st.chat_input("Type your question here...")

    if user_input:
        # Store user query
        st.session_state[chat_context].append({"role": "user", "content": user_input})

        # Generate response using Gemini
        bot_response = get_gemini_response(user_input)

        # Store bot response
        st.session_state[chat_context].append({"role": "assistant", "content": bot_response})

        # Display bot response
        with st.chat_message("assistant"):
            st.markdown(bot_response)


# --- PERSONALIZED CHATBOT PAGE ---
def personalized_chatbot():
    st.title("🤖 Personalized Chatbot")
    st.write("Ask me anything! I'm here to help you.")
    chat_interface("chat_history")

# --- DOCUMENT UPLOAD PAGE ---
def document_upload():
    st.title("📄 Document Upload")
    uploaded_file = st.file_uploader("Upload your document here", type=["pdf", "txt", "docx"])
    if uploaded_file:
        st.success("Document uploaded successfully! 🟢")

    # Embedded chat feature
    chat_interface("chat_history_doc")

# --- URL UPLOAD PAGE ---
def url_upload():
    st.title("🌐 URL Upload")
    
    # URL Input Field
    url_input = st.text_input("Enter URL here:")
    custom_requirement = st.text_area("Describe your scraping requirements:")
    
    if st.button("Scrape and Format"):
        if url_input and custom_requirement:
            with st.spinner("Scraping content..."):
                content = extract_content(url_input)

            if content:
                st.success("Content scraped successfully! ✅")
                with st.expander("🔍 Extracted Content (Raw)"):
                    st.json(content)

                with st.spinner("Formatting content with Gemini..."):
                    formatted_output = format_with_gemini(content, custom_requirement)

                if formatted_output:
                    st.success("Content formatted successfully! ✅")
                    st.text_area("Formatted Output:", value=formatted_output, height=300)
                else:
                    st.error("Failed to format the content with Gemini.")
            else:
                st.error("Failed to scrape the content. Please check the URL.")
        else:
            st.warning("Please provide both the URL and custom requirement.")

    chat_interface("chat_history_url")


# --- DATA ANALYSIS PAGE ---
def data_analysis():
    st.title("📊 Data Analysis")
    
    # Excel File Upload Field
    uploaded_excel = st.file_uploader("Upload your Excel file here", type=["xlsx", "csv"])
    if uploaded_excel:
        st.success("Excel file uploaded successfully! 🟢")

    # Embedded chat feature
    chat_interface("chat_history_data")

# --- SETTINGS PAGE ---
def settings():
    st.title("⚙️ Settings")
    st.write("Configure your app settings here.")

# --- PAGE ROUTING ---
if page == "🤖 Personalized Chatbot":
    personalized_chatbot()
elif page == "📄 Document Upload":
    document_upload()
elif page == "🌐 URL Upload":
    url_upload()
elif page == "📊 Data Analysis":
    data_analysis()
elif page == "⚙️ Settings":
    settings()
