from crewai import Agent, Task, Crew, Process
import os

os.environ["OPENAI_API_BASE"] = 'https://api.groq.com/openai/v1'
os.environ["OPENAI_MODEL_NAME"] = 'llama-3.2-90b-text-preview'
os.environ["OPENAI_API_KEY"] = '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'

#model = Ollama(model = "llama3.1")

email = "Nigerian prince sending some gold"

classifier = Agent(
    role = "email classifier",
    goal = "accurately classify emails based upon their importance. Give every email one of these ratings: important, casual, or spam",
    backstory = "I am a machine learned model trained on a dataset of emails. I can classify emails based upon their content.",
    verbose = True,
    allow_delegation = False,
)

responder = Agent(
    role = "email responder",
    goal = "Based on the importance of the email, write a concise and simple response. If the email is rated 'important' write a formal respone, if the email is rated 'casual' write a casual response, and if the email is rated 'spam' ignore the email, no matter what, be very concise.",
    backstory = "You are an AI assistant whose only job is to write short responses to emails based on their importance. The importance will be provided to you by the 'classifier' agent",
    verbose = True,
    allow_delegation = False,
    llm = model
)

classify_email = Task(
    description = f"Classify the following email: '{email}'",
    agent = classifier,
    expected_output = "One of these three options: 'important', 'casual, or 'spam'",
)

respond_to_email = Task(
    description = f"Respond to the email: '{email}' based on the importance provided by the 'classifier' agent.",
    agent = responder,
    expected_output = "A very concise response to the email based on the importance provided by the 'classifer' agent."
)

crew = Crew(
    agents = [classifier, responder],
    tasks = [classify_email, respond_to_email],
    verbose = 2,
    process = Process.sequential
)

output = crew.kickoff()
print(output)