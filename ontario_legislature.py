import typer
from typing import Optional, List
import streamlit as st
from phi.assistant import Assistant
from phi.storage.assistant.postgres import PgAssistantStorage
from phi.knowledge.pdf import PDFUrlKnowledgeBase
from phi.vectordb.pgvector import PgVector2
import os
from dotenv import load_dotenv
import base64

# Load environment variables
load_dotenv()

def set_background_image(image_url):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url({image_url});
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Call function to set the background image
# Replace 'your_image_url' with the URL of your image or path to your local image
set_background_image('https://www.ola.org/sites/default/files/legacy/ImageGallery7.jpg')

# Set up database connection
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

# Initialize Knowledge Base and Storage
vector_db = PgVector2(collection="Ontario", db_url=db_url)
storage = PgAssistantStorage(table_name="pdf_assistant", db_url=db_url)

def initialize_assistant(pdf_urls):
    """Initialize the Assistant with the given PDF URLs."""
    knowledge_base = PDFUrlKnowledgeBase(urls=pdf_urls, vector_db=vector_db)
    knowledge_base.load()
    assistant = Assistant(
        knowledge_base=knowledge_base,
        storage=storage,
        show_tool_calls=False,
        search_knowledge=True,
        read_chat_history=True,
    )
    return assistant

# Streamlit Interface
st.title("Ontario Legislative Assembly Chatbot")
st.markdown(
    """
    Welcome to the **Ontario Legislative Assembly Chatbot**. 
    Use this tool to query legislative documents quickly and efficiently.
    """
)
# Input Section
#st.header("Upload and Process PDF")
pdf_url = st.text_input("Enter the URL:")
if st.button("Process PDF"):
    if pdf_url.strip():
        try:
            st.session_state["assistant"] = initialize_assistant([pdf_url])
            st.success("PDF processed successfully. You can now ask questions!")
        except Exception as e:
            st.error(f"Error processing PDF: {e}")
    else:
        st.error("Please enter a valid PDF URL.")

# Chat Section
if "assistant" in st.session_state:
    st.header("Ask Questions about the PDF")
    user_input = st.text_input("Your question:")
    if st.button("Ask"):
        if user_input.strip():
            try:
                assistant = st.session_state["assistant"]
                response = ''.join(assistant.chat(user_input))
                st.markdown(f"**Assistant:** {response}")
            except Exception as e:
                st.error(f"Error generating response: {e}")
        else:
            st.error("Please enter a question.")

# Footer Section
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; margin-top: 20px;">
        <p style="font-size: 14px; color: #777;">
        Developed by <strong>Shehbaz Patel</strong> | © 2024 All Rights Reserved
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)