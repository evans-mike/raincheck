# Questions to ask
# 1. Get event time and place, and create an event object
# 2. Get subscriber phone, and create a subscriber object
# 3. Ask if the subscriber wants to subscribe to texts or emails
# 4 Confirm the event time and place, and subscriber phone are correct
# 5. Create the subscription
# 6. Return the forecast for the event time and place

# utilize https://cookbook.openai.com/examples/how_to_call_functions_with_chat_models

import json
from openai import OpenAI

# import openai
from tenacity import retry, wait_random_exponential, stop_after_attempt
from termcolor import colored
from dotenv import dotenv_values

config = dotenv_values(".env")

openai_client = OpenAI(
    api_key=config["OPENAI_API_KEY"],
)


message = {
    "role": "user",
    "content": input(
        'This is the beginning of your chat with AI. [To exit, send "###".]\n\nYou:'
    ),
}

conversation = [{"role": "system", "content": "DIRECTIVE_FOR_gpt-3.5-turbo"}]

while message["content"] != "###":
    conversation.append(message)
    completion = openai_client.chat.completions.create(
        model="gpt-3.5-turbo", messages=conversation
    )
    message["content"] = input(
        f"Assistant: {completion.choices[0].message.content} \nYou:"
    )
    print()
    conversation.append(completion.choices[0].message)
