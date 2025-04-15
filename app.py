import streamlit as st
from gemini_backend import get_gemini_response
from webscrapping import extract_content, format_with_gemini 
from vector_store_api import upload_pdf_to_chroma
from vector_rag import query_rag
from session_manager import (
    list_sessions, create_new_session,
    load_session, save_message
)

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# --- CONTEXT MAPPING ---
CONTEXTS = {
    "🤖 Personalized Chatbot": "chatbot",
    "📄 Document Upload": "doc",
    "🌐 URL Upload": "url",
    "📊 Data Analysis": "data"
}

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("🔍 Navigation")
    page = st.radio("Choose a feature:", list(CONTEXTS.keys()))
    context = CONTEXTS[page]

    # Session Selector
    st.markdown("### 💬 Chat Sessions")
    existing_sessions = list_sessions(context)
    session_options = [s["title"] + f" ({s['id'][:6]})" for s in existing_sessions]
    session_map = {s["title"] + f" ({s['id'][:6]})": s["id"] for s in existing_sessions}

    # Track previous session ID to detect switch
    previous_session_id = st.session_state.get(f"current_session_id_{context}", None)

    selected_option = st.selectbox("Select a session:", session_options) if session_options else None
    current_session_id = session_map[selected_option] if selected_option else None
    st.session_state[f"current_session_id_{context}"] = current_session_id

    # Detect session switch, clear state, force reload
    if current_session_id and previous_session_id and current_session_id != previous_session_id:
        st.session_state[f"chat_history_{context}"] = []
        st.rerun()

    # New Session Button
    if st.button("➕ New Session"):
        current_session_id = create_new_session(context)
        st.session_state[f"current_session_id_{context}"] = current_session_id
        st.session_state[f"chat_history_{context}"] = []
        st.rerun()

# --- SESSION DATA LOADING ---
if current_session_id:
    session_data = load_session(context, current_session_id)
    if session_data is None:
        st.error("Failed to load selected session.")
        st.stop()

    # Always replace session chat history on session change
    st.session_state[f"chat_history_{context}"] = session_data["messages"]
else:
    st.warning("Please create or select a session to continue.")
    st.stop()

# --- CHAT INTERFACE FUNCTION ---
def chat_interface(chat_context, pdf_mode=False):
    st.subheader("💬 Chat with AI")

    for chat in st.session_state[chat_context]:
        with st.chat_message(chat["role"]):
            st.markdown(chat["content"])

    user_input = st.chat_input("Type your question here...")

    if user_input:
        st.session_state[chat_context].append({"role": "user", "content": user_input})
        save_message(context, current_session_id, "user", user_input)

        if pdf_mode:
            bot_response = query_rag(user_input, chat_history=st.session_state[chat_context])

        else:
            bot_response = get_gemini_response(user_input, st.session_state[chat_context])


        st.session_state[chat_context].append({"role": "assistant", "content": bot_response})
        save_message(context, current_session_id, "assistant", bot_response)

        with st.chat_message("assistant"):
            st.markdown(bot_response)

# --- PERSONALIZED CHATBOT PAGE ---
def personalized_chatbot():
    st.title("🤖 Personalized Chatbot")
    st.write("Ask me anything! I'm here to help you.")
    chat_interface("chat_history_chatbot")

# --- DOCUMENT UPLOAD PAGE ---
def document_upload():
    st.title("📄 Document Upload")
    uploaded_file = st.file_uploader("Upload your document here", type=["pdf", "txt", "docx"])
    if uploaded_file:
        with st.spinner("Uploading and indexing your document..."):
            response_message = upload_pdf_to_chroma(uploaded_file)
        if "successfully" in response_message:
            st.success(response_message)
        else:
            st.error(response_message)
    chat_interface("chat_history_doc", pdf_mode=True)

# --- URL UPLOAD PAGE ---
def url_upload():
    st.title("🌐 URL Upload")

    # --- Always-visible input fields ---
    st.markdown("### 🔗 Enter URL and Your Requirement")
    url_input = st.text_input("Enter URL here:", key="url_input")
    custom_requirement = st.text_area("Describe your scraping requirements:", key="custom_requirement")

    if st.button("🚀 Scrape and Format"):
        if url_input and custom_requirement:
            with st.spinner("Scraping content..."):
                scraped_content = extract_content(url_input)

            # Save to session for tab rendering
            st.session_state.scraped_content = scraped_content

            # Save user instruction to chat history
            user_msg = f"Scrape the content from this URL:\n{url_input}\n\nRequirement:\n{custom_requirement}"
            st.session_state["chat_history_url"].append({"role": "user", "content": user_msg})
            save_message("url", st.session_state["current_session_id_url"], "user", user_msg)

            if scraped_content:
                success_msg = f"✅ Successfully scraped content from: {url_input}\n**Title:** {scraped_content.get('title', 'No Title')}"
                st.session_state["chat_history_url"].append({"role": "assistant", "content": success_msg})
                save_message("url", st.session_state["current_session_id_url"], "assistant", success_msg)

                # Immediately format with Gemini
                with st.spinner("Formatting with Gemini..."):
                    formatted_output = format_with_gemini(scraped_content, custom_requirement)

                if formatted_output:
                    st.session_state.formatted_output = formatted_output
                    st.session_state["chat_history_url"].append({"role": "assistant", "content": formatted_output})
                    save_message("url", st.session_state["current_session_id_url"], "assistant", formatted_output)
                    st.success("Formatted successfully!")
                else:
                    err_msg = "❌ Failed to format content with Gemini."
                    st.session_state["chat_history_url"].append({"role": "assistant", "content": err_msg})
                    save_message("url", st.session_state["current_session_id_url"], "assistant", err_msg)
                    st.error(err_msg)
            else:
                err_msg = f"❌ Failed to scrape content from: {url_input}"
                st.session_state["chat_history_url"].append({"role": "assistant", "content": err_msg})
                save_message("url", st.session_state["current_session_id_url"], "assistant", err_msg)
                st.error(err_msg)
        else:
            st.warning("Please provide both the URL and the scraping requirement.")

    # --- Tabbed layout for chat + viewer ---
    tab1, tab2 = st.tabs(["💬 Chat Interface", "📄 Content Viewer"])

    with tab1:
        st.subheader("Chat with the Scraped Content")

        # Show chat history
        for chat in st.session_state["chat_history_url"]:
            with st.chat_message(chat["role"]):
                st.markdown(chat["content"])

        # Follow-up chat input
        user_input = st.chat_input("Ask about the scraped content...")
        if user_input and st.session_state.get("scraped_content"):
            st.session_state["chat_history_url"].append({"role": "user", "content": user_input})
            save_message("url", st.session_state["current_session_id_url"], "user", user_input)

            with st.spinner("Thinking..."):
                followup_response = format_with_gemini(
    st.session_state.scraped_content,
    user_input,
    chat_history=st.session_state["chat_history_url"]
)

            if followup_response:
                st.session_state["chat_history_url"].append({"role": "assistant", "content": followup_response})
                save_message("url", st.session_state["current_session_id_url"], "assistant", followup_response)
                with st.chat_message("assistant"):
                    st.markdown(followup_response)
            else:
                err_msg = "❌ Gemini failed to respond."
                st.session_state["chat_history_url"].append({"role": "assistant", "content": err_msg})
                save_message("url", st.session_state["current_session_id_url"], "assistant", err_msg)
                st.error(err_msg)

    with tab2:
        st.subheader("📄 Scraped Content Viewer")

        if st.session_state.get("scraped_content"):
            content = st.session_state.scraped_content
            col1, col2 = st.columns(2)

            with col1:
                st.write("### Basic Info")
                st.json({
                    "URL": url_input,
                    "Title": content.get("title"),
                    "Metadata Count": len(content.get("metadata", []))
                })

                st.write("### Metadata")
                st.json(content.get("metadata", {}))

            with col2:
                st.write("### Text Content")
                st.text_area("Full Text Content", value=content.get("text_content", ""), height=400)

            if st.session_state.get("formatted_output"):
                st.divider()
                st.write("### Last Formatted Output")
                st.markdown(st.session_state.formatted_output)
        else:
            st.info("No content scraped yet. Enter a URL to begin.")



# --- DATA ANALYSIS PAGE ---
def data_analysis():
    st.title("📊 Data Analysis")
    uploaded_excel = st.file_uploader("Upload your Excel file here", type=["xlsx", "csv"])
    if uploaded_excel:
        st.success("Excel file uploaded successfully! 🟢")
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
