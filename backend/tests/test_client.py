# test_client_with_file.py

import asyncio
import websockets
import json
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

async def test_websocket_with_file():
    uri = "ws://localhost:8000/ws"
    logger.info(f"🔌 Attempting to connect to {uri}")

    # Read test file
    try:
        file_path = Path(__file__).parent / 'victor_tonsils_uni.txt'
        with open(file_path, 'r') as f:
            test_content = f.read()
            logger.info("✅ Test file loaded successfully")
    except Exception as e:
        logger.error(f"❌ Error reading test file: {str(e)}")
        return

    try:
        async with websockets.connect(uri) as websocket:
            logger.info("✅ Connected to WebSocket server")
            
            logger.info("📤 Sending test file content")
            await websocket.send(test_content)
            
            # Wait for response
            response = await websocket.recv()
            response_data = json.loads(response)
            
            logger.info("📥 Received response:")
            logger.info("-" * 50)
            logger.info(f"Transcript: {response_data.get('transcript', 'No transcript')[:200]}...")
            logger.info("Questions generated:")
            for q in response_data.get('questions', []):
                logger.info(f"❓ {q}")
            logger.info("-" * 50)

    except websockets.exceptions.ConnectionRefused:
        logger.error("❌ Failed to connect. Is the server running?")
    except Exception as e:
        logger.error(f"❌ An error occurred: {str(e)}")

if __name__ == "__main__":
    logger.info("🚀 Starting WebSocket test client...")
    asyncio.run(test_websocket_with_file())