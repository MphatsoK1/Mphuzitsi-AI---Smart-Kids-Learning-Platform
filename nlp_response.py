import re
import pyttsx3

engine = pyttsx3.init()
engine.setProperty('rate', 160)

def speak(text):
    engine.say(text)
    engine.runAndWait()

def process_input(user_text):
    text = user_text.lower().strip()

    # Recognize basic intents and sample interactions
    if re.search(r'\bhello|hi|hey\b', text):
        return "Hello! Ready to trace some letters today?"
    elif re.search(r'\btrace|learn|write\b', text):
        return "Okay! Which letter would you like to trace?"
    elif re.search(r'\ba\b', text):
        return "Let's trace the letter A. Start at the top and follow the dots down."
    elif re.search(r'\bb\b', text):
        return "Let’s trace the letter B together. Start at the top and make two big bumps."
    elif re.search(r'\bgoodbye|bye\b', text):
        return "Goodbye! You did amazing today. See you next time!"
    else:
        return "Hmm, I didn’t quite get that. Can you say the letter you want to trace?"

# the ending of code
if __name__ == "__main__":
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            break
        response = process_input(user_input)
        print("AI:", response)
        speak(response)
