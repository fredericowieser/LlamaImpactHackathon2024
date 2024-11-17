from groq import Groq
from typing import List

TEMP = 0.5

def gen_new_questions(
        client: Groq,
        history: List[str],
        role: str,
        new_qs_prompt: str,
        previous_questions: str,
        doc_notes: str,
    ) -> str:
    """
    Provide new questions to ask the patient using the Groq summa
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
                "content": new_qs_prompt.format(
                    conversation=history,
                    previous_questions=previous_questions,
                ),
            }
        ],
        model="llama-3.2-90b-vision-preview",
        temperature=TEMP,
    )

    summary = chat_completion.choices[0].message.content

    return summary

def gen_remove_questions(
        client: Groq,
        history: List[str],
        role: str,
        new_qs_prompt: str,
        previous_questions: str,
        doc_notes: str = None,
    ) -> str:
    """
    Provide what questions should be removed from the questions array
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
                "content": new_qs_prompt.format(
                    conversation=history,
                    previous_questions=previous_questions,
                ),
            }
        ],
        model="llama-3.2-90b-vision-preview",
        temperature=TEMP,
    )

    summary = chat_completion.choices[0].message.content

    return summary

def gen_questions_combiner(
        client: Groq,
        role: str,
        new_qs_prompt: str,
        previous_questions: str,
        doc_notes: str = None,
    ) -> str:
    """
    """

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": role,
            },
            {
                "role": "user",
                "content": new_qs_prompt.format(
                    previous_questions=previous_questions,
                ),
            }
        ],
        model="llama-3.2-90b-vision-preview",
        temperature=TEMP,
    )