import os
from groq import Groq
from pydub import AudioSegment

AUDIO_PATH = "./audio/"

client = Groq(
    api_key = "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"
)
#filename = os.path.dirname(__file__) + "/audio.m4a"

def join_transcriptions(history: str, new_text: str) -> str:
    """ Joins a new transcription to an existing history, removing any overlapping text.
    Args:
        history (str): The existing transcribed text.
        transcription (str): The new transcribed text.
    Returns:
        str: The combined text.
    """
    completion = client.chat.completions.create(
        model="llama-3.2-90b-text-preview",
        messages=[
            {
                "role": "system",
                "content": "You are a system whose purpose is to join two transcriptions of the same conversation. You have two inputs: the beginning of the conversation and the end, though they will overlap. Your goal is to combine the two transcriptions while removing any overlapping text. The overlapping text may not match exactly, so you must select the most appropriate version for your output. The accuracy of the output is of the utmost importance, peoples’ lives may depend on it."
            },
            {
                "role": "user",
                "content": "The beginning transcription is: " + history + "\nThe end transcription is: " + new_text
            }
        ],
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
    )

    for chunk in completion:
        print(chunk.choices[0].delta.content or "", end="")

      
def transcibe_conv_slice(audio_filename: str, start_timestamp: int, length: int) -> str:
    """Transcribes a section of an audio file.
    Args:
        audio_filename (str): The filename inc local path of the full audio file.
        start_timestamp (int): The starting timestamp in seconds from start of file.
        length (int): The length of the audio to transcribe in seconds.
    Returns:
        str: The transcribed text.

    Questions: do we have assurance that we hav 10 secs til the end of the file?
    """
    slice_filename = AUDIO_PATH + "conversation_slice.wav"
 #   conversation_full = AudioSegment.from_wav(filename)
    conversation_full = AudioSegment.from_mp3(audio_filename)
    conversation_slice = conversation_full[start_timestamp * 1000: (start_timestamp + length) * 1000]   
    print("I am here")
    conversation_slice.export(slice_filename, format="wav")
    print("spliced")
    with open(slice_filename, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(slice_filename, file.read()),
            model="whisper-large-v3",
            language="en",
            response_format="verbose_json",
    )
    print("transcribed")
    print(transcription.text)
    return transcription.text

if __name__ == "__main__":
    history = "Smoke from hundreds of wildfires in Canada is triggering air quality alerts throughout the U.S. Skylines from Maine to Maryland to Minnesota are gray and smoggy. And in some places, the air quality warnings include the warning to stay inside. We wanted to better understand what's happening here and why, so we called Peter DiCarlo."
    transcription = transcibe_conv_slice("./audio/wildfires.mp3", 15, 10)
    full_convo = join_transcriptions(history, transcription)
