from groq import Groq

client = Groq(
    api_key = "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"
)
completion = client.chat.completions.create(
    model="llama-3.2-90b-text-preview",
    messages=[
        {
            "role": "user",
            "content": "Hello Llama my old friend"
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