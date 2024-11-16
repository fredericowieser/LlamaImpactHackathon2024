# main.py

import os
import json
from groq import Groq
from pathlib import Path
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
import json
import time
from datetime import datetime

# Set up logging with a more visible format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI()

# Basic CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Test logging at startup
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Starting Healthcare Assistant API...")
    logger.info("📝 Test Questions Ready:")
    test_questions = [
        "How are you feeling today?",
        "Any new symptoms?",
        "Rate your pain 1-10"
    ]
    for q in test_questions:
        logger.info(f"   ❓ {q}")
    logger.info("-" * 50)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("🔌 New WebSocket connection established")
    
    try:
        # Convert initial audio to text
        history = []
        # Generate initial questions
        questions = []
        while True:
            # Get audio data from frontend
            data = await websocket.receive_text()
            logger.info(f"📥 Received audio chunk from frontend")
            print(data)
            
            # Convert theis audio data to text
            logger.info("🔊 Converting audio to text...")

            # Pass this new test chunk with the previous history to the joiner
            # this will try and give us the correct transcript.
            logger.info("🔍 Sending audio to joiner for full transcription...")

            # Using the full history generate a summary of the conversation
            # trying to stick to new doctor notes best practices and only
            # include the most important information.
            logger.info("📝 Generating conversation summary...")
            summary = s

            # Using the full history generate new questions to ask the patient
            # to get the most information about their condition.
            logger.info("🔍 Generating follow-up questions...")

            # Generate what questions should be removed from the questions JSON
            # as they have already been asked/answered.
            logger.info("🔍 Generating questions to remove...")

            # Remove the questions that have already been asked/answered
            logger.info("🔍 Removing questions that have already been asked...")

            # Create mock response
            response = {
                "summary": summary,
                "questions": [
                    "How are you feeling today?",
                    "Any new symptoms?",
                    "Rate your pain 1-10"
                ]
            }
            
            # Log and send response
            logger.info("🤖 Sending response with questions:")
            for q in response["questions"]:
                logger.info(f"   ❓ {q}")
            
            await websocket.send_json(response)
            logger.info("📤 Response sent successfully")
            logger.info("-" * 50)

    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
    finally:
        logger.info("👋 WebSocket connection closed")

@app.get("/")
async def root():
    logger.info("✨ Health check endpoint accessed")
    return {"status": "healthy", "message": "Healthcare Assistant API is running"}

if __name__ == "__main__":
    # Add some visible test logs before starting server
    logger.info("="*50)
    logger.info("🔍 Testing logging system...")
    logger.info("✅ Logging system working")
    logger.info("="*50)

    # Load API key from config.json (two directories up)
    config_path = Path(__file__).parent.parent / 'config.json'
    print(config_path)
    with open(config_path) as f:
        config = json.load(f)
        GROQ_API_KEY = config.get('groq_apikey')

    # Initialize Groq client
    client = Groq(
        api_key=GROQ_API_KEY,
    )
    
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )