# **AI Assistant with RAG, Web Scraping, and Document Processing** 🤖📄🌐📊  

## **📌 Introduction**  
This is a **multi-functional AI-powered assistant** built using **Streamlit**. It integrates **Google Gemini AI, Web Scraping, PDF/Text processing, RAG (Retrieval-Augmented Generation) with ChromaDB, and Data Analysis** to provide **an interactive chatbot** for multiple use cases.  

## **✨ Features**
✅ **🤖 Personalized Chatbot** – AI-powered chatbot using Google Gemini API.  
✅ **📄 Document Upload (PDF/Text)** – Upload PDFs and chat with their content using RAG.  
✅ **🌐 URL Upload & Web Scraping** – Extract content from URLs and format it with Gemini AI.  
✅ **📊 Data Analysis** – Upload Excel/CSV files and analyze them with AI assistance.  
✅ **⚙️ Settings Panel** – Modify configurations as needed.  

## **🛠️ Tech Stack**
- **Frontend:** [Streamlit](https://streamlit.io/)  
- **AI Models:** Google Gemini API (for text generation & embeddings)  
- **Vector Store:** ChromaDB (stores embeddings for RAG)  
- **Document Processing:** PyMuPDF, python-docx  
- **Web Scraping:** BeautifulSoup, Requests  
- **Data Analysis:** Pandas, OpenPyxl  

---

## **🚀 Installation Guide**
### **1️⃣ Clone the Repository**
```sh
git clone https://github.com/yourusername/ai-assistant.git
cd ai-assistant
```

### **2️⃣ Create a Virtual Environment**
```sh
python -m venv venv
```

### **3️⃣ Activate the Virtual Environment**
- **Windows:**  
  ```sh
  venv\Scripts\activate
  ```
- **Mac/Linux:**  
  ```sh
  source venv/bin/activate
  ```

### **4️⃣ Install Dependencies**
```sh
pip install -r requirements.txt
```

### **5️⃣ Set Up Environment Variables**
Create a `.env` file in the root directory and add:
```sh
GEMINI_API_KEY=your_google_gemini_api_key
```

### **6️⃣ Run the Streamlit App**
```sh
streamlit run app.py
```

---

## **📌 Usage Guide**
### **▶️ Chatbot**
1. Navigate to the **🤖 Personalized Chatbot** section.  
2. Ask any question, and the AI will generate responses.  

### **▶️ Document Upload & Chat**
1. Go to **📄 Document Upload** and upload a **PDF/Text** file.  
2. The file is indexed using **ChromaDB**, and you can chat with its content.  

### **▶️ Web Scraping & Formatting**
1. Enter a **URL** and provide formatting requirements.  
2. The content is extracted, structured using **Gemini AI**, and displayed.  

### **▶️ Data Analysis**
1. Upload an **Excel/CSV** file for AI-assisted analysis.  

---

## **📜 File Structure**
```
/ai-assistant
│── app.py                      # Main Streamlit app
│── requirements.txt             # Python dependencies
│── README.md                    # Documentation
│── .env                         # Environment variables (not committed)
│── vector_store_api.py          # PDF processing & embedding
│── vector_rag.py                # Retrieval-Augmented Generation logic
│── webscrapping.py              # URL content extraction & formatting
│── gemini_backend.py            # AI response generation
```

---

## **🤝 Contribution**
1. **Fork the repository**  
2. **Create a feature branch:** `git checkout -b feature-name`  
3. **Commit changes:** `git commit -m "Added new feature"`  
4. **Push to GitHub:** `git push origin feature-name`  
5. **Open a pull request** 🚀  

---

## **📧 Contact**
💡 Have questions or suggestions? Reach out:  
📩 Email: **sahilspt011@gmail.com**  
🔗 GitHub: **https://github.com/SahilSapte11**  
