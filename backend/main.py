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
from backend.summary import summariser
from backend.questions import gen_new_questions, gen_remove_questions, gen_questions_combiner

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
    logger.info("-" * 50)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("🔌 New WebSocket connection established")

    # Load the prompts from backend/prompts/*.txt
    logger.info("📝 Loading prompts...")
    prompts_path = Path(__file__).parent / 'backend' / 'prompts'
    best_results_path = prompts_path / 'best_results.txt'
    with best_results_path.open('r') as f:
        best_results_txt = f.read()
    new_questions_path = prompts_path / 'new_questions.txt'
    with new_questions_path.open('r') as f:
        new_questions_txt = f.read()
    rm_questions_path = prompts_path / 'rm_questions.txt'
    with rm_questions_path.open('r') as f:
        rm_questions_txt = f.read()
    summarise_path = prompts_path / 'summarise.txt'
    with summarise_path.open('r') as f:
        summarise_txt = f.read()
    question_combiner_path = prompts_path / 'question_combiner.txt'
    with question_combiner_path.open('r') as f:
        question_combiner_txt = f.read()
    logger.info("✅ Prompts loaded successfully")

    # Load API key from config.json (two directories up)
    config_path = Path(__file__).parent.parent / 'config.json'
    with open(config_path) as f:
        config = json.load(f)
        GROQ_API_KEY = config.get('groq_apikey')

    # Initialize Groq client
    client = Groq(
        api_key=GROQ_API_KEY,
    )
    
    try:
        # Initialize parameters
        history = []
        history_text = ""
        questions = []
        doc_notes = ""
        summary = ""
        while True:
            # Get audio data from frontend
            # Receive audio data and DOCTORS NOTES from the frontend
            data = await websocket.receive_text()
            history.append(data)
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
            summary = summariser(
                client=client,
                history=data,
                role=best_results_txt,
                summary_prompt=summarise_txt,
                doc_notes=doc_notes,
                old_summary=summary,
            )
            logger.info("📝 Summary generated:")
            logger.info(f"   {summary}")

            # Using the full history generate new questions to ask the patient
            # to get the most information about their condition.
            logger.info("🔍 Generating follow-up questions...")
            new_questions = gen_new_questions(
                client=client,
                history=data,
                role=new_questions_txt,
                new_qs_prompt=new_questions_txt,
                previous_questions=questions,
                doc_notes=doc_notes,
            )
            logger.info("🔍 New questions generated:")
            logger.info(f"   ❓ {new_questions}")

            # Generate what questions should be removed from the questions JSON
            # as they have already been asked/answered.
            rm_questions = ""
            if questions:
                logger.info("🔍 Generating questions to remove...")
                rm_questions = gen_remove_questions(
                    client=client,
                    history=data,
                    role=rm_questions_txt,
                    new_qs_prompt=rm_questions_txt,
                    previous_questions=questions,
                    doc_notes=doc_notes,
                )
                logger.info("🔍 Questions to remove:")
                logger.info(f"   ❓ {rm_questions}")

                # Remove the questions that have already been asked/answered
                # and add the new questions to the questions JSON.
                logger.info("🔍 Removing questions that have already been asked...")
                questions = gen_questions_combiner(
                    client=client,
                    role=rm_questions_txt,
                    comb_qs_prompt=question_combiner_txt,
                    previous_questions=questions,
                    new_questions=new_questions,
                    rm_questions=rm_questions,
                )
                logger.info("🔍 Updated questions:")
                logger.info(f"   ❓ {questions}")
            else:
                questions = new_questions
                logger.info("🔍 Updated questions:")
                logger.info(f"   ❓ {questions}")


            # Create mock response
            response = {
                "summary": summary,
                "questions": [
                    "How are you feeling today?",
                    "Any new symptoms?",
                    "Rate your pain 1-10"
                ]
            }

            # TESTING ONLY

            
            # Log and send response
            logger.info("🤖 Sending response with questions:")
            
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
    
    # Start the server
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )