import os
from dotenv import load_dotenv
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import streamlit as st
from io import BytesIO

# Load environment variables from .env file
load_dotenv()

# Get the Telegram API token from the .env file
TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
CLOUDMERSIVE_API_KEY = os.getenv("CLOUDMERSIVE_API_KEY")

# Initialize the Telegram Bot
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome! Send me a PDF or Word document to convert.")

def handle_document(update: Update, context: CallbackContext):
    # Get the document from the message
    file_id = update.message.document.file_id
    file_info = context.bot.get_file(file_id)
    
    # Download the file
    file = file_info.download_as_bytearray()
    
    # Get file extension
    file_extension = update.message.document.file_name.split('.')[-1]
    
    if file_extension == "pdf":
        # Convert PDF to Word
        converted_file = convert_pdf_to_word(file)
        update.message.reply_document(document=converted_file, filename="converted_word.docx", caption="Converted to Word!")
    
    elif file_extension in ["docx", "doc"]:
        # Convert Word to PDF
        converted_file = convert_word_to_pdf(file)
        update.message.reply_document(document=converted_file, filename="converted_pdf.pdf", caption="Converted to PDF!")

def convert_pdf_to_word(pdf_data):
    # Cloudmersive PDF to Word API
    url = 'https://api.cloudmersive.com/convert/pdf/to/word'
    headers = {'Apikey': CLOUDMERSIVE_API_KEY}
    
    files = {'file': ('file.pdf', io.BytesIO(pdf_data))}
    response = requests.post(url, headers=headers, files=files)
    
    if response.status_code == 200:
        # Return the converted Word file
        return io.BytesIO(response.content)
    else:
        return "Error in conversion"

def convert_word_to_pdf(word_data):
    # Cloudmersive Word to PDF API
    url = 'https://api.cloudmersive.com/convert/convert/to/pdf'
    headers = {'Apikey': CLOUDMERSIVE_API_KEY}
    
    files = {'file': ('file.docx', io.BytesIO(word_data))}
    response = requests.post(url, headers=headers, files=files)
    
    if response.status_code == 200:
        # Return the converted PDF file
        return io.BytesIO(response.content)
    else:
        return "Error in conversion"

# Set up the Streamlit interface
def streamlit_interface():
    st.title('Telegram Bot Document Converter')

    st.write("""
    This app allows you to send files to the Telegram Bot.
    The bot will convert your PDF to Word or Word to PDF.
    """)

    st.markdown("To interact with the bot, click [here](https://t.me/your_bot_name)")

    # Start the Telegram Bot in a separate thread
    updater = Updater(TELEGRAM_API_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.document, handle_document))
    
    updater.start_polling()

# Run the Streamlit app
if __name__ == "__main__":
    streamlit_interface()
