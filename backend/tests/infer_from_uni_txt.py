import os
import json
from groq import Groq
from pathlib import Path
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Load API key from config.json (two directories up)
logger.info("🔑 Loading API key from config.json...")
config_path = Path(__file__).parent.parent.parent / 'config.json'
try:
    with open(config_path) as f:
        config = json.load(f)
        GROQ_API_KEY = config.get('groq_apikey')
        if not GROQ_API_KEY:
            logger.error("❌ GROQ_API_KEY not found in config.json")
            raise ValueError("GROQ_API_KEY missing")
        logger.info("✅ Successfully loaded GROQ_API_KEY")
except Exception as e:
    logger.error(f"❌ Error loading config.json: {str(e)}")
    raise

# Read the text file
logger.info("📄 Loading conversation text file...")
text_file_path = Path(__file__).parent / 'victor_tonsils_uni.txt'
try:
    with open(text_file_path, 'r') as f:
        conversation_text = f.read()
        logger.info("✅ Successfully loaded conversation text")
        logger.debug(f"Text content: {conversation_text[:100]}...")  # Log first 100 chars
except Exception as e:
    logger.error(f"❌ Error reading text file: {str(e)}")
    raise

# Initialize Groq client
logger.info("🤖 Initializing Groq client...")
client = Groq(
    api_key=GROQ_API_KEY,
)
logger.info("✅ Groq client initialized")

logger.info("📡 Making API call for medical analysis...")
try:
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a helpful medical assistant. Generate a summary and relevant follow-up questions based on the patient's consultation. This conversation is provided in a way where the patient and doctor text cannot be distinguished. Looking at this text consider the best questions to ask the patient in order to rule out any serious conditions, and gain the most information on what the condition could be. Please do this acting as a world class medical professional, and provide the best possible questions to ask the patient. Do this acting as if the fate of the patient's life depends on the questions you ask."
            },
            {
                "role": "user",
                "content": conversation_text
            }
        ],
        model="llama-3.2-90b-vision-preview",
    )
    logger.info("✅ Second API call successful")
    logger.info("🏥 Medical Analysis Results:")
    logger.info("-" * 50)
    logger.info(chat_completion.choices[0].message.content)
    logger.info("-" * 50)
except Exception as e:
    logger.error(f"❌ Error in API call: {str(e)}")
    raise

logger.info("✨ Script execution completed successfully")