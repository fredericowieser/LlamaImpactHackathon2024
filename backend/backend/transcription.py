import os
import re
from groq import Groq
from pydub import AudioSegment
import subprocess
import logging

logger = logging.getLogger(__name__)


AUDIO_PATH = "./audio/"
#filename = os.path.dirname(__file__) + "/audio.m4a"

def join_transcriptions(client: Groq, joiner_prompt: str, history: str, new_text: str) -> str:
    """ Joins a new transcription to an existing history, removing any overlapping text.
    Args:
        client: Instantiated Groq client.
        joiner_prompt (str): The system prompt to use for the joiner model.
        history (str): The existing transcribed text.
        transcription (str): The new transcribed text.
    Returns:
        str: The combined text.
    """
    combined_text = ""
    completion = client.chat.completions.create(
        model="llama-3.2-90b-text-preview",
        messages=[
            {
                "role": "system",
<<<<<<< Updated upstream
                "content": joiner_prompt
=======
                "content": "You are a system whose purpose is to join two transcriptions of the same conversation. You have two inputs: the beginning of the conversation and the end, though they will overlap. Your goal is to combine the two transcriptions while removing any overlapping text. The overlapping text may not match exactly, so you must select the most appropriate version for your output. The accuracy of the output is of the utmost importance, peoples' lives may depend on it."
>>>>>>> Stashed changes
            },
            {
                "role": "user",
                "content": "<BEGINNING>" + history + "</BEGINNING>\n<END>" + new_text + "<END>"
            }
        ],
        temperature=0,
        max_tokens=1024,
        top_p=1,
        stream=False
    )

<<<<<<< Updated upstream
#    for chunk in completion:
#        print(chunk.choices[0].delta.content or "", end="")
    output = completion.choices[0].message.content
    #Include only output inbetween the <OUTPUT> tags and strip them (only if Llama has added them)
    match = re.search(r"<OUTPUT>(.*)</OUTPUT>", output)
    if match is not None: output = match.group(1)
    return output

def transcribe_conv_slice(client: Groq, audio_filename: str, start_timestamp: int, length: int) -> str:
    """Transcribes a section of an audio file.
    Args:
        client: Instantiated Groq client.
        audio_filename (str): The filename inc local path of the full audio file.
        start_timestamp (int): The starting timestamp in seconds from start of file.
        length (int): The length of the audio to transcribe in seconds.
    Returns:
        str: The transcribed text.

    Questions: do we have assurance that we hav 10 secs til the end of the file?
    """
    slice_filename = AUDIO_PATH + "conversation_slice.wav"
 #   conversation_full = AudioSegment.from_wav(audio_filename)
 #   conversation_full = AudioSegment.from_mp3(audio_filename)
    conversation_full = AudioSegment.from_file(audio_filename) #should autodetect format
    conversation_slice = conversation_full[start_timestamp * 1000: (start_timestamp + length) * 1000]   
    conversation_slice.export(slice_filename, format="wav")
    with open(slice_filename, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(slice_filename, file.read()),
            model="whisper-large-v3",
            language="en",
            response_format="verbose_json",
    )
    return transcription.text
=======
    # Collect the streamed response
    for chunk in completion:
        if chunk.choices[0].delta.content:
            combined_text += chunk.choices[0].delta.content

    return combined_text

      
def transcibe_conv_slice(audio_filename: str, start_timestamp: int, length: int) -> str:
    """Transcribes a section of an audio file."""
    try:
        temp_wav = AUDIO_PATH + "temp_conversion.wav"
        slice_filename = AUDIO_PATH + "conversation_slice.wav"
        
        # First, ensure the WebM file is valid
        with open(audio_filename, 'rb') as f:
            webm_data = f.read()
            
        # Add WebM header if missing
        if not webm_data.startswith(b'\x1a\x45\xdf\xa3'):
            webm_header = (
                b'\x1a\x45\xdf\xa3'  # EBML header
                b'\x01\x00\x00\x00\x00\x00\x00\x20'  # EBML version
                b'\x42\x86\x81\x01'  # EBMLVersion
                b'\x42\x87\x81\x04'  # EBMLReadVersion
                b'\x42\x82\x84\x77\x65\x62\x6D'  # DocType "webm"
            )
            webm_data = webm_header + webm_data
            
            # Write corrected file
            with open(audio_filename, 'wb') as f:
                f.write(webm_data)
        
        # Convert to WAV using ffmpeg with more detailed parameters
        try:
            ffmpeg_command = [
                'ffmpeg',
                '-i', audio_filename,
                '-c:a', 'pcm_s16le',
                '-ac', '1',
                '-ar', '16000',
                '-f', 'wav',
                '-y',
                temp_wav
            ]
            
            # Run ffmpeg with full error capture
            result = subprocess.run(
                ffmpeg_command,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info("✅ Successfully converted audio to WAV")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg conversion error:\n{e.stderr}")
            raise Exception(f"FFmpeg conversion failed: {e.stderr}")
        
        # Load and process the audio
        try:
            conversation_full = AudioSegment.from_wav(temp_wav)
            total_duration = len(conversation_full)
            
            # Calculate slice duration
            end_time = min((start_timestamp + length) * 1000, total_duration)
            conversation_slice = conversation_full[start_timestamp * 1000: end_time]
            
            # Export the slice
            conversation_slice.export(slice_filename, format="wav")
            
            # Transcribe using OpenAI
            with open(slice_filename, "rb") as file:
                transcription = client.audio.transcriptions.create(
                    file=(slice_filename, file.read()),
                    model="whisper-large-v3",
                    language="en",
                    response_format="verbose_json",
                )
            
            logger.info(f"✅ Transcription successful: {transcription.text}")
            return transcription.text
            
        finally:
            # Clean up temporary files
            for file in [temp_wav, slice_filename]:
                if os.path.exists(file):
                    try:
                        os.remove(file)
                    except Exception as e:
                        logger.warning(f"Failed to remove temporary file {file}: {e}")
                        
    except Exception as e:
        logger.error(f"Error in transcription process: {str(e)}")
        return ""
>>>>>>> Stashed changes

if __name__ == "__main__":
    """Example usage of the functions in this module."""

    history = "Smoke from hundreds of wildfires in Canada is triggering air quality alerts throughout the U.S. Skylines from Maine to Maryland to Minnesota are gray and smoggy. And in some places, the air quality warnings include the warning to stay inside. We wanted to better understand what's happening here and why, so we called Peter DiCarlo."

    client = Groq(
        api_key = "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"
    ) 

    transcription = transcribe_conv_slice(client, "./audio/wildfires.mp3", 15, 10)

    prompt_filename = "./backend/backend/prompts/joiner.txt"
    with open(prompt_filename) as prompt_file:
        joiner_prompt = prompt_file.read()
    
    full_conversation = join_transcriptions(client, joiner_prompt, history, transcription)
    print(full_conversation)
