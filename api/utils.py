import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

import random
import time

def get_mock_response(message):
    message = message.lower()

    if "hello" in message or "hi" in message:
        return "I am good! How can I help you?"

    if "how are you" in message:
        return "I am doing great! Thanks for asking."

    responses = [
        "Here is your reply: " + message,
        "You said: " + message,
        "My answer to that is: " + message,
        "Let me respond: " + message,
    ]
    return random.choice(responses)

def get_chatbot_response(prompt_content, user_message, chat_history=None):
    api_key = os.getenv("OPENAI_API_KEY")
    force_mock = os.getenv("MOCK_MODE", "False").lower() == "true"
    
    # If Mock Mode is forced or Key is missing, use Mock Response
    if force_mock or not api_key or api_key == "your_openai_api_key_here":
        return get_mock_response(user_message)

    try:
        client = OpenAI(api_key=api_key)
        messages = [
            {"role": "system", "content": prompt_content},
        ]
        
        if chat_history:
            for msg in chat_history:
                messages.append({"role": msg['role'], "content": msg['content']})
                
        messages.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        # If we hit a quota limit, fallback to Mock Mode instead of showing error
        if "insufficient_quota" in str(e) or "429" in str(e):
            return get_mock_response(user_message)
        return f"Error connecting to AI: {str(e)}"
