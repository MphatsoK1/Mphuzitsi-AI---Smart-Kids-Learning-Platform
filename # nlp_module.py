# nlp_module.py (updated)
from ml_module import predict_intent
import pyttsx3

engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def process_input(user_text):
    intent = predict_intent(user_text)

    responses = {
        "greeting": "Hello! Ready to trace some letters today?",
        "trace": "Okay! Which letter would you like to trace?",
        "goodbye": "Goodbye! You did amazing today. See you next time!",
        "gratitude": "You're welcome! Let’s keep learning together!",
    }

    return responses.get(intent, "Hmm, I didn’t quite get that. Can you say that again?")
