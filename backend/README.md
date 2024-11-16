-  Send a stream of audio that we 
-  



history = []

call_llama:
    send 'this is my history and my new result. Please define the new distory'
    await
    return

def send_audio_to_groq:
    receive audio from frontend
    timer(10sec)
    send_to_groq
    await result
    get joiner response
    history.append
    return start again


def joiner(history, result): 
    new_history = call_llama
    return new_history


def ask_question(new_history, old_history, existing_question):
    ask llama if there should be a new question
    await yes/no
    if yes, ask_question abd send question to frontend