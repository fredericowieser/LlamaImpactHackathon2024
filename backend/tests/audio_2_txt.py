import os
import json
from groq import Groq
from pathlib import Path

# Load API key from config.json (two directories up)
config_path = Path(__file__).parent.parent.parent / 'config.json'
with open(config_path) as f:
    config = json.load(f)
    GROQ_API_KEY = config.get('groq_apikey')

# Initialize Groq client
client = Groq(
    api_key=GROQ_API_KEY,
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Explain the importance of fast language models",
        }
    ],
    model="llama3-8b-8192",
)

print(chat_completion.choices[0].message.content)