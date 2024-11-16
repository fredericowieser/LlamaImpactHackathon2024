# main.py

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
        while True:
            # Get data from frontend
            data = await websocket.receive_text()
            logger.info(f"📥 Received message: {data[:50]}...")  # Log first 50 chars
            


            # Create mock response
            response = {
                "transcript": f"Mock transcript for: {data[:20]}...",
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
    
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )