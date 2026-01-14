import os
import random
from dotenv import load_dotenv

load_dotenv()

def get_mock_response(message):
    """Fallback mock response when API is unavailable"""
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
