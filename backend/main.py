import os
import json
from groq import Groq
from pathlib import Path
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from typing import List, Dict, Any
import numpy as np
from dataclasses import dataclass, field
from io import BytesIO
from pydub import AudioSegment
import time
import uvicorn
import logging
from datetime import datetime
from backend.summary import summariser
from backend.questions import gen_new_questions, gen_remove_questions
from backend.transcription import transcibe_conv_slice, join_transcriptions

# Update the audio path constant to match transcription.py
AUDIO_PATH = "./audio/"

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

@dataclass
class ConversationHistory:
    """Maintains a history of the conversation."""
    transcript: str = ""
    summary: str = ""
    questions: List[str] = field(default_factory=list)
    doc_notes: str = ""
    last_processed_time: float = field(default_factory=time.time)
    buffer_transcripts: List[str] = field(default_factory=list)  # Store individual transcripts

    def update_transcript(self, new_text: str) -> None:
        """Update transcript and mark time of last update."""
        logger.info("🔄 Updating conversation transcript")
        logger.info(f"New transcription text: {new_text}")
        
        # Add new transcription to buffer
        if new_text:
            self.buffer_transcripts.append(new_text)
            
        # If we have at least 2 transcripts, try to join them
        if len(self.buffer_transcripts) >= 2:
            logger.info("Attempting to join transcripts...")
            # Join the first two transcripts
            if not self.transcript:
                self.transcript = self.buffer_transcripts[0]
                logger.info(f"Initial transcript: {self.transcript}")
            
            # Join with the next transcript
            combined = join_transcriptions(self.transcript, self.buffer_transcripts[1])
            if combined:
                self.transcript = combined
                # Remove the processed transcript from buffer
                self.buffer_transcripts.pop(0)
                logger.info(f"Updated full transcript: {self.transcript}")
            
        self.last_processed_time = time.time()

class AudioProcessor:
    """Handles audio processing and maintains conversation state."""
    def __init__(self, chunk_duration: int = 10, overlap_duration: int = 5):
        self.chunk_duration = chunk_duration
        self.overlap_duration = overlap_duration
        self.buffer = BytesIO()
        self.start_time = time.time()
        self.chunk_count = 0
        self.accumulated_data = BytesIO()
        self.last_transcription_time = 0
        logger.info(f"✅ AudioProcessor initialized with chunk_duration={chunk_duration}s, overlap_duration={overlap_duration}s")
        
    async def process_chunk(self, audio_data: bytes, conversation: ConversationHistory) -> str:
        """Process a chunk of audio data and update conversation history."""
        try:
            current_time = time.time()
            # Accumulate the binary data
            self.accumulated_data.write(audio_data)
            current_size = self.accumulated_data.getbuffer().nbytes
            
            logger.info(f"📊 Current buffer size: {current_size/1024:.2f}KB")
            
            # Only process if we have enough data AND enough time has passed
            if (current_size >= 32000 and 
                current_time - self.last_transcription_time >= self.overlap_duration):
                
                logger.info(f"🎵 Processing chunk {self.chunk_count}")
                self.last_transcription_time = current_time
                
                try:
                    # Save the audio chunk
                    self.accumulated_data.seek(0)
                    chunk_filename = os.path.join(AUDIO_PATH, f"conversation_chunk_{self.chunk_count}.mp3")
                    with open(chunk_filename, 'wb') as f:
                        f.write(self.accumulated_data.getvalue())
                    logger.info(f"💾 Saved chunk to: {chunk_filename}")
                    
                    # Transcribe the chunk
                    transcribed_text = transcibe_conv_slice(
                        chunk_filename,
                        0,
                        self.chunk_duration
                    )
                    
                    if transcribed_text:
                        logger.info(f"✅ Transcription successful: {transcribed_text}")
                    else:
                        logger.warning("⚠️ No text transcribed from chunk")
                    
                    # Cleanup
                    os.remove(chunk_filename)
                    self.chunk_count += 1
                    
                    # Reset buffer but keep overlap
                    overlap_size = min(16000, current_size)
                    self.accumulated_data.seek(-overlap_size, 2)
                    overlap_data = self.accumulated_data.read()
                    self.accumulated_data = BytesIO()
                    self.accumulated_data.write(overlap_data)
                    
                    return transcribed_text
                    
                except Exception as e:
                    logger.error(f"❌ Error processing chunk: {str(e)}")
                    return ""
            
            return ""
            
        except Exception as e:
            logger.error(f"❌ Error in process_chunk: {str(e)}")
            return ""

class ConversationManager:
    def __init__(self, websocket: WebSocket, client: Groq, prompts: Dict[str, str]):
        self.websocket = websocket
        self.client = client
        self.prompts = prompts
        self.conversation = ConversationHistory()
        self.audio_processor = AudioProcessor()
        self.last_update_time = 0
        self.update_interval = 10  # Seconds between updates to client
        logger.info("✅ ConversationManager initialized")
        
    async def process_audio(self, audio_data: bytes) -> None:
        """Process incoming audio and trigger necessary updates."""
        try:
            transcribed_text = await self.audio_processor.process_chunk(audio_data, self.conversation)
            
            if transcribed_text:
                self.conversation.update_transcript(transcribed_text)
                
                # Only send updates every update_interval seconds
                current_time = time.time()
                if current_time - self.last_update_time >= self.update_interval:
                    self.last_update_time = current_time
                    await self._send_updates()
            
        except Exception as e:
            logger.error(f"❌ Error in process_audio: {str(e)}")

    async def _send_updates(self) -> None:
        """Send all necessary updates to client."""
        try:
            # Only send updates if we have a transcript
            if self.conversation.transcript:
                logger.info("🔄 Sending updates to client...")
                
                await self._send_transcript()
                await self._update_summary()
                await self._update_questions()
                
                logger.info("✅ All updates sent")
            
        except Exception as e:
            logger.error(f"❌ Error in _send_updates: {str(e)}")

    async def _send_transcript(self) -> None:
        """Send current transcript to client."""
        try:
            await self.websocket.send_json({
                "type": "transcript_update",
                "text": self.conversation.transcript
            })
            logger.info("📤 Sent transcript update to client")
        except Exception as e:
            logger.error(f"❌ Error sending transcript: {str(e)}")

    async def _update_summary(self) -> None:
        """Generate and send updated summary."""
        try:
            logger.info("📋 Generating new summary...")
            summary = summariser(
                client=self.client,
                history=self.conversation.transcript,
                role=self.prompts['best_results'],
                summary_prompt=self.prompts['summarise'],
                doc_notes=self.conversation.doc_notes,
                old_summary=self.conversation.summary
            )
            
            logger.info("Generated summary:")
            logger.info("-" * 50)
            logger.info(summary)
            logger.info("-" * 50)
            
            self.conversation.summary = summary
            
            await self.websocket.send_json({
                "type": "summary_update",
                "summary": summary
            })
            logger.info("📤 Sent summary update to client")
            
        except Exception as e:
            logger.error(f"❌ Error in summary generation: {str(e)}")

    async def _update_questions(self) -> None:
        """Generate and send updated questions."""
        try:
            logger.info("❓ Generating new questions...")
            new_questions = gen_new_questions(
                client=self.client,
                history=self.conversation.transcript,
                role=self.prompts['new_questions'],
                new_qs_prompt=self.prompts['new_questions'],
                previous_questions=self.conversation.questions,
                doc_notes=self.conversation.doc_notes
            )
            
            logger.info("New questions generated:")
            logger.info("-" * 50)
            # for i, q in enumerate(new_questions, 1):
            #     logger.info(f"{i}. {q}")
            logger.info("-" * 50)
            
            if self.conversation.questions:
                logger.info("🔍 Checking for questions to remove...")
                removed_questions = gen_remove_questions(
                    client=self.client,
                    history=self.conversation.transcript,
                    role=self.prompts['rm_questions'],
                    new_qs_prompt=self.prompts['rm_questions'],
                    previous_questions=self.conversation.questions,
                    doc_notes=self.conversation.doc_notes
                )
                
                logger.info("Questions to remove:")
                logger.info("-" * 50)
                logger.info(f"{removed_questions}")
                logger.info("-" * 50)
                
                self.conversation.questions = [q for q in new_questions if q not in removed_questions]
            else:
                self.conversation.questions = new_questions

            logger.info("Final question list:")
            logger.info("-" * 50)
            # for i, q in enumerate(self.conversation.questions, 1):
            #     logger.info(f"{i}. {q}")
            logger.info("-" * 50)
            
            await self.websocket.send_json({
                "type": "questions_update",
                "questions": self.conversation.questions
            })
            logger.info("📤 Sent questions update to client")
            
        except Exception as e:
            logger.error(f"❌ Error in question generation: {str(e)}")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("\n" + "=" * 80)
    logger.info("🔵 NEW WEBSOCKET CONNECTION")
    logger.info("=" * 80)

    try:
        # Load prompts
        logger.info("📚 Loading prompts...")
        prompts = {}
        prompts_path = Path(__file__).parent / 'backend' / 'prompts'
        for prompt_file in ['best_results.txt', 'new_questions.txt', 'rm_questions.txt', 'summarise.txt']:
            with (prompts_path / prompt_file).open('r') as f:
                prompts[prompt_file.replace('.txt', '')] = f.read()
                logger.info(f"✅ Loaded {prompt_file}")
        
        # Initialize Groq client
        logger.info("🔄 Initializing Groq client...")
        config_path = Path(__file__).parent.parent / 'config.json'
        with open(config_path) as f:
            config = json.load(f)
            client = Groq(api_key=config['groq_apikey'])
        logger.info("✅ Groq client initialized")
        
        manager = ConversationManager(websocket, client, prompts)
        
        while True:
            try:
                # Receive data
                data = await websocket.receive()
                
                # Handle different types of messages
                if 'bytes' in data:
                    logger.info(f"📥 Received binary data: {len(data['bytes'])} bytes")
                    await manager.process_audio(data['bytes'])
                elif 'text' in data:
                    message = json.loads(data['text'])
                    if message.get('type') == 'end':
                        logger.info("🏁 Received end-of-stream marker")
                        break
                    
            except Exception as e:
                logger.error(f"❌ Error processing message: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"❌ WebSocket handler error: {str(e)}")
    finally:
        logger.info("👋 WebSocket connection closed")
        logger.info("=" * 80 + "\n")

# Update the startup event to create the correct directory
@app.on_event("startup")
async def startup_event():
    """Create necessary directories on startup."""
    os.makedirs(AUDIO_PATH, exist_ok=True)
    logger.info(f"✅ Ensured audio directory exists at: {AUDIO_PATH}")

if __name__ == "__main__":
    # Add some visible startup logs
    print("\n" + "=" * 80)
    print("🚀 STARTING HEALTHCARE ASSISTANT SERVER")
    print("=" * 80 + "\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )