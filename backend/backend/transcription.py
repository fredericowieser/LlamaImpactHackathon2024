import os
import re
from groq import Groq
from pydub import AudioSegment


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
                "content": joiner_prompt
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
