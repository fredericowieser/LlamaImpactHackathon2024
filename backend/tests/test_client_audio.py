import asyncio
import websockets
import json
import logging
from pathlib import Path
from datetime import datetime
from mutagen import mp3  # For getting audio duration
import math

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Constants for audio streaming
CHUNK_SIZE = 8192  # 8KB chunks

async def handle_server_messages(websocket):
    """Handle incoming messages from the server."""
    try:
        while True:
            try:
                response = await websocket.recv()
                response_data = json.loads(response)
                
                message_type = response_data.get('type', '')
                logger.info(f"\n📥 Received {message_type}:")
                logger.info("-" * 50)
                
                if message_type == 'transcript_update':
                    text = response_data.get('text', '')
                    logger.info("📝 Transcript:")
                    logger.info(text[:200] + "..." if len(text) > 200 else text)
                
                elif message_type == 'summary_update':
                    summary = response_data.get('summary', '')
                    logger.info("📋 Summary:")
                    logger.info(summary)
                
                elif message_type == 'questions_update':
                    questions = response_data.get('questions', [])
                    logger.info("❓ Questions:")
                    for i, question in enumerate(questions, 1):
                        logger.info(f"{i}. {question}")
                
                logger.info("-" * 50)
                
            except websockets.exceptions.ConnectionClosed:
                logger.info("Connection closed by server")
                break
            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to decode JSON: {str(e)}")
            except Exception as e:
                logger.error(f"❌ Error handling message: {str(e)}")
                continue

    except Exception as e:
        logger.error(f"❌ Error in message handler: {str(e)}")

async def test_websocket_with_audio():
    uri = "ws://localhost:8000/ws"
    logger.info(f"🔌 Attempting to connect to {uri}")

    try:
        # Read audio file and get duration
        file_path = Path(__file__).parent / 'Victor.mp3'
        audio = mp3.MP3(file_path)
        duration_seconds = audio.info.length
        logger.info(f"🎵 Audio duration: {duration_seconds:.2f} seconds")

        with open(file_path, 'rb') as f:
            audio_data = f.read()
            logger.info(f"✅ Audio file loaded successfully ({len(audio_data)} bytes)")

        # Calculate streaming parameters
        total_chunks = math.ceil(len(audio_data) / CHUNK_SIZE)
        delay_per_chunk = duration_seconds / total_chunks
        bytes_per_second = len(audio_data) / duration_seconds
        
        logger.info(f"📊 Streaming parameters:")
        logger.info(f"   - Total chunks: {total_chunks}")
        logger.info(f"   - Delay per chunk: {delay_per_chunk:.3f} seconds")
        logger.info(f"   - Bytes per second: {bytes_per_second:.2f}")

    except Exception as e:
        logger.error(f"❌ Error preparing audio file: {str(e)}")
        return

    try:
        async with websockets.connect(uri) as websocket:
            logger.info("✅ Connected to WebSocket server")
            
            # Start message handler task
            message_handler = asyncio.create_task(handle_server_messages(websocket))
            
            # Stream audio data in chunks at real-time rate
            position = 0
            start_time = asyncio.get_event_loop().time()
            
            while position < len(audio_data):
                chunk = audio_data[position:position + CHUNK_SIZE]
                await websocket.send(chunk)
                
                current_chunk = position // CHUNK_SIZE + 1
                elapsed_time = asyncio.get_event_loop().time() - start_time
                logger.info(f"📤 Sent chunk {current_chunk}/{total_chunks} "
                          f"({len(chunk)} bytes) - "
                          f"Time: {elapsed_time:.2f}s/{duration_seconds:.2f}s")
                
                position += CHUNK_SIZE
                
                # Calculate and apply delay for real-time streaming
                target_time = start_time + (position / bytes_per_second)
                current_time = asyncio.get_event_loop().time()
                delay = max(0, target_time - current_time)
                await asyncio.sleep(delay)
            
            # Send end-of-stream marker
            await websocket.send(json.dumps({"type": "end"}))
            logger.info("📤 Sent end-of-stream marker")
            
            # Wait for a few seconds to receive final updates
            try:
                await asyncio.sleep(5)  # Wait for final processing
            except asyncio.CancelledError:
                pass
            
            # Cancel message handler
            message_handler.cancel()
            try:
                await message_handler
            except asyncio.CancelledError:
                pass

    except websockets.exceptions.ConnectionRefused:
        logger.error("❌ Failed to connect. Is the server running?")
    except Exception as e:
        logger.error(f"❌ An error occurred: {str(e)}")
    finally:
        logger.info("👋 Test client finished")

if __name__ == "__main__":
    logger.info("\n" + "=" * 50)
    logger.info("🚀 Starting WebSocket audio test client...")
    logger.info("=" * 50 + "\n")
    
    asyncio.run(test_websocket_with_audio())