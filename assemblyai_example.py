# `pip3 install assemblyai` (macOS)
# `pip install assemblyai` (Windows)

import assemblyai as aai

aai.settings.api_key = "e4846aa190ad4d9897e0346a179585cf"
transcriber = aai.Transcriber()

#file_url = "https://assembly.ai/news.mp4"
file_url = "https://assembly.ai/wildfires.mp3"
#file_url = transcriber.transcribe("./my-local-audio-file.wav")

config = aai.TranscriptionConfig(speaker_labels=True)

transcriber = aai.Transcriber()
transcript = transcriber.transcribe(
  file_url,
  config=config
)

for utterance in transcript.utterances:
  print(f"Speaker {utterance.speaker}: {utterance.text}")
