import os
import json
from groq import Groq
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
<<<<<<< Updated upstream
=======
import subprocess
>>>>>>> Stashed changes
import asyncio
from typing import List, Dict, Any
import numpy as np
from dataclasses import dataclass, field
from io import BytesIO
<<<<<<< Updated upstream
from pydub import AudioSegment
=======
import io
import wave
>>>>>>> Stashed changes
import time
import uvicorn
import logging
from datetime import datetime
from pydub import AudioSegment
from backend.summary import summariser
from backend.questions import gen_new_questions, gen_remove_questions
<<<<<<< Updated upstream
from backend.transcription import transcribe_conv_slice, join_transcriptions

# Update the audio path constant to match transcription.py
=======
import wave
import struct
import tempfile

>>>>>>> Stashed changes
AUDIO_PATH = "./audio/"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

<<<<<<< Updated upstream

#Maintains a history of the conversation.
class ConversationHistory:
    def __init__(self, client: Groq, joiner_prompt: str):
        self.transcript: str = ""
        self.summary: str = ""
        self.questions: List[str] = field(default_factory=list)
        self.doc_notes: str = ""
        self.last_processed_time: float = field(default_factory=time.time)
        self.buffer_transcripts: List[str] = field(default_factory=list)  # Store individual transcripts
        self.client = client
        self.joiner_prompt = joiner_prompt

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
            combined = join_transcriptions(self.client, self.joiner_prompt, self.transcript, self.buffer_transcripts[1])
            if combined:
                self.transcript = combined
                # Remove the processed transcript from buffer
                self.buffer_transcripts.pop(0)
                logger.info(f"Updated full transcript: {self.transcript}")
            
        self.last_processed_time = time.time()

class AudioProcessor:
    """Handles audio processing and maintains conversation state."""
    def __init__(self, client:Groq, chunk_duration: int = 10, overlap_duration: int = 5):
        self.chunk_duration = chunk_duration
        self.overlap_duration = overlap_duration
        self.buffer = BytesIO()
        self.start_time = time.time()
        self.chunk_count = 0
        self.accumulated_data = BytesIO()
        self.last_transcription_time = 0
        self.client = client
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
                    transcribed_text = transcribe_conv_slice(
                        self.client,
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
=======
@dataclass
class ConversationHistory:
    transcript: str = ""
    summary: str = ""
    questions: List[str] = field(default_factory=list)
    doc_notes: str = ""
    last_processed_time: float = field(default_factory=time.time)
    buffer_transcripts: List[str] = field(default_factory=list)
    last_update_time: float = 0

    async def update_transcript(self, new_text: str) -> bool:
        """
        Update transcript and return whether a full update should be triggered.
        Returns True if enough time has passed for a full update.
        """
        UPDATE_INTERVAL = 10  # Seconds between full updates

        if new_text:
            logger.info("\n" + "=" * 50)
            logger.info("🔄 Updating conversation transcript")
            logger.info(f"New transcription: {new_text}")
            
            # Add new transcription to buffer
            self.buffer_transcripts.append(new_text)
            
            # Join transcripts if we have multiple
            if len(self.buffer_transcripts) >= 2:
                self.transcript = " ".join(self.buffer_transcripts)
                logger.info(f"Updated full transcript: {self.transcript}")
            else:
                self.transcript = new_text
            
            current_time = time.time()
            should_update = (current_time - self.last_update_time) >= UPDATE_INTERVAL
            
            if should_update:
                self.last_update_time = current_time
                logger.info("💫 Triggering full update (summary + questions)")
            
            return should_update
        return False

>>>>>>> Stashed changes

class ConversationManager:
    def __init__(self, websocket: WebSocket, client: Groq, prompts: Dict[str, str]):
        self.websocket = websocket
        self.client = client
        self.prompts = prompts
<<<<<<< Updated upstream
        self.conversation = ConversationHistory(client, prompts['joiner'])
        self.audio_processor = AudioProcessor(client)
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
=======
        self.conversation = ConversationHistory()
        # Pass the client to AudioProcessor
        self.audio_processor = AudioProcessor(client=client)
        self.last_update_time = time.time()
        self.update_interval = 10
        logger.info("✅ ConversationManager initialized")
        
    async def _process_full_update(self) -> None:
        """Process full update including summary and questions."""
        try:
            logger.info("🔄 Processing full update")
            
            # Generate new summary
            self.conversation.summary = summariser(
>>>>>>> Stashed changes
                client=self.client,
                history=self.conversation.transcript,
                role=self.prompts['best_results'],
                summary_prompt=self.prompts['summarise'],
                doc_notes=self.conversation.doc_notes,
                old_summary=self.conversation.summary
            )
            
<<<<<<< Updated upstream
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
=======
            # Generate new questions
>>>>>>> Stashed changes
            new_questions = gen_new_questions(
                client=self.client,
                history=self.conversation.transcript,
                role=self.prompts['new_questions'],
                new_qs_prompt=self.prompts['new_questions'],
                previous_questions=self.conversation.questions,
                doc_notes=self.conversation.doc_notes
            )
            
<<<<<<< Updated upstream
            logger.info("New questions generated:")
            logger.info("-" * 50)
            # for i, q in enumerate(new_questions, 1):
            #     logger.info(f"{i}. {q}")
            logger.info("-" * 50)
            
            if self.conversation.questions:
                logger.info("🔍 Checking for questions to remove...")
=======
            # Process question removals if we have existing questions
            if self.conversation.questions:
>>>>>>> Stashed changes
                removed_questions = gen_remove_questions(
                    client=self.client,
                    history=self.conversation.transcript,
                    role=self.prompts['rm_questions'],
                    new_qs_prompt=self.prompts['rm_questions'],
                    previous_questions=self.conversation.questions,
                    doc_notes=self.conversation.doc_notes
                )
<<<<<<< Updated upstream
                
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
=======
                self.conversation.questions = [q for q in new_questions if q not in removed_questions]
            else:
                self.conversation.questions = new_questions
            
            await self._send_updates()
            
        except Exception as e:
            logger.error(f"❌ Error in full update: {str(e)}")

    async def _send_transcript_update(self) -> None:
        """Send only transcript update to client."""
        try:
            await self.websocket.send_json({
                "type": "transcript_update",
                "transcript": self.conversation.transcript
            })
            logger.info("📤 Sent transcript update")
        except Exception as e:
            logger.error(f"❌ Error sending transcript update: {str(e)}")

    async def _send_updates(self) -> None:
        """Send full updates to client."""
        try:
            logger.info("📤 Sending full update to client")
            
            update_data = {
                "type": "full_update",
                "transcript": self.conversation.transcript,
                "summary": self.conversation.summary,
                "questions": self.conversation.questions
            }
            
            await self.websocket.send_json(update_data)
            
            logger.info("\nUpdate details:")
            logger.info(f"📝 Transcript length: {len(self.conversation.transcript)} chars")
            logger.info(f"📋 Summary length: {len(self.conversation.summary)} chars")
            logger.info(f"❓ Questions: {len(self.conversation.questions)}")
            
        except Exception as e:
            logger.error(f"❌ Error sending updates: {str(e)}")

class AudioProcessor:
    def __init__(self, client):
        self.client = client
        self.chunk_count = 0
        self.accumulated_data = bytearray()
        self.last_transcription_time = 0
        self.min_chunk_size = 16000
        logger.info("AudioProcessor initialized")

    async def process_chunk(self, audio_data: bytes) -> str:
        """Process a chunk of audio data."""
        try:
            current_time = time.time()
            
            # Accumulate the binary data
            if isinstance(audio_data, (bytes, bytearray)):
                self.accumulated_data.extend(audio_data)
            else:
                logger.error(f"❌ Unexpected audio data type: {type(audio_data)}")
                return ""
                
            current_size = len(self.accumulated_data)
            time_since_last = current_time - self.last_transcription_time
            
            # Only process if we have enough data
            if current_size >= self.min_chunk_size and time_since_last >= 5:
                self.last_transcription_time = current_time
                
                try:
                    # Save audio chunk to temporary file
                    with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as temp_file:
                        temp_file.write(bytes(self.accumulated_data))
                        temp_path = temp_file.name
                    
                    # Transcribe using the temporary file
                    with open(temp_path, 'rb') as audio_file:
                        file_tuple = (
                            "audio.webm",     # Filename
                            audio_file.read(),
                            "audio/webm"      # MIME type
                        )
                        
                        transcription = self.client.audio.transcriptions.create(
                            file=file_tuple,
                            model="whisper-large-v3",
                            language="en",
                            response_format="verbose_json"
                        )
                    
                    logger.info(f"✅ Transcription successful: {transcription.text}")
                    
                    # Update state
                    self.chunk_count += 1
                    overlap_size = min(8000, current_size)
                    self.accumulated_data = self.accumulated_data[-overlap_size:]
                    
                    return transcription.text
                    
                finally:
                    # Cleanup
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    
            return ""
            
        except Exception as e:
            logger.error(f"❌ Processing error: {str(e)}")
            return ""
>>>>>>> Stashed changes

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
<<<<<<< Updated upstream
    logger.info("\n" + "=" * 80)
    logger.info("🔵 NEW WEBSOCKET CONNECTION")
    logger.info("=" * 80)

    try:
        # Load prompts
        logger.info("📚 Loading prompts...")
        prompts = {}
        prompts_path = Path(__file__).parent / 'backend' / 'prompts'
        for prompt_file in ['best_results.txt', 'new_questions.txt', 'rm_questions.txt', 'summarise.txt', 'joiner.txt']:
=======
    logger.info("🔵 NEW WEBSOCKET CONNECTION")
    
    try:
        # Load prompts and initialize Groq client
        logger.info("📚 Loading prompts...")
        prompts = {}
        prompts_path = Path(__file__).parent / 'backend' / 'prompts'
        for prompt_file in ['best_results.txt', 'new_questions.txt', 'rm_questions.txt', 'summarise.txt']:
>>>>>>> Stashed changes
            with (prompts_path / prompt_file).open('r') as f:
                prompts[prompt_file.replace('.txt', '')] = f.read()
                logger.info(f"✅ Loaded {prompt_file}")
        
<<<<<<< Updated upstream
        # Initialize Groq client
=======
>>>>>>> Stashed changes
        logger.info("🔄 Initializing Groq client...")
        config_path = Path(__file__).parent.parent / 'config.json'
        with open(config_path) as f:
            config = json.load(f)
            client = Groq(api_key=config['groq_apikey'])
        logger.info("✅ Groq client initialized")
        
        manager = ConversationManager(websocket, client, prompts)
        
        while True:
            try:
<<<<<<< Updated upstream
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
=======
                data = await websocket.receive()
                
                if data["type"] == "bytes":
                    # Handle audio data
                    audio_data = data["bytes"]
                    logger.info(f"📥 Received audio chunk: {len(audio_data)} bytes")
                    
                    transcribed_text = await manager.audio_processor.process_chunk(audio_data)
                    if transcribed_text:
                        should_update = await manager.conversation.update_transcript(transcribed_text)
                        if should_update:
                            await manager._process_full_update()
                        else:
                            await manager._send_transcript_update()
                            
                elif data["type"] == "text":
                    # Handle text messages (like [RESTART])
                    if data["text"] == "[RESTART]":
                        manager = ConversationManager(websocket, client, prompts)
                        await websocket.send_json({
                            "type": "transcript_update",
                            "transcript": "Session restarted"
                        })
                    
            except WebSocketDisconnect:
                logger.info("👋 WebSocket disconnected")
                break
            except Exception as e:
                logger.error(f"❌ Error in websocket loop: {str(e)}")
>>>>>>> Stashed changes
                continue
                
    except Exception as e:
        logger.error(f"❌ WebSocket handler error: {str(e)}")
    finally:
        logger.info("👋 WebSocket connection closed")
        logger.info("=" * 80 + "\n")

<<<<<<< Updated upstream
# Update the startup event to create the correct directory
=======
>>>>>>> Stashed changes
@app.on_event("startup")
async def startup_event():
    """Create necessary directories on startup."""
    os.makedirs(AUDIO_PATH, exist_ok=True)
    logger.info(f"✅ Ensured audio directory exists at: {AUDIO_PATH}")

if __name__ == "__main__":
<<<<<<< Updated upstream
    # Add some visible startup logs
=======
>>>>>>> Stashed changes
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