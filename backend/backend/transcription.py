import os
from groq import Groq
from pydub import AudioSegment

AUDIO_PATH = "./audio/"

client = Groq(
    api_key = "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"
)
#filename = os.path.dirname(__file__) + "/audio.m4a"


      
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

if __name__ == "__main__":

    transcibe_conversation("./audio/wildfires.mp3", 10, 10)