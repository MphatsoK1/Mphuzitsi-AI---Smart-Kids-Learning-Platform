# main_app.py
from speech_module import listen, speak
from nlp_module import process_input

def main():
    speak("Hello! I'm Mphunzitsi AI. Which letter would you like to trace?")
    while True:
        text = listen()
        if not text:
            continue
        if "exit" in text or "quit" in text:
            speak("Goodbye for now!")
            break
        response = process_input(text)
        speak(response)

if __name__ == "__main__":
    main()
