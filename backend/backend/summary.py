from groq import Groq
from typing import List

def summariser(
        client: Groq,
        history: List[str],
        role: str,
        summary_prompt: str,
        doc_notes: str = None,
        old_summary: str = None,
    ) -> str:
    """
    Summarise the patient's history using the Groq summarisation model.

    Args:
        client (Groq): The Groq client.
        history (List[str]): A list of the patient's history.

    Returns:
        str: The summarised text.
    """
    # Join the history into a single string
    # history_text = " ".join(history)

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": role,
            },
            {
                "role": "user",
                "content": summary_prompt.format(
                    conversation=history,
                    doctors_notes=doc_notes,
                    previous_summary=old_summary,
                ),
            }
        ],
        model="llama-3.2-90b-vision-preview",
        temperature=0,
    )

    summary = chat_completion.choices[0].message.content

    return summary