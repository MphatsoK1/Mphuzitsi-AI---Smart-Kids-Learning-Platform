import speech_recognition as sr
import pyttsx3

r = sr.Recognizer()
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio).lower()
            print(f"You said: {text}")
            return text
        except:
            speak("Sorry, I didn’t catch that. Can you say it again?")
            return None

# Example interaction
speak("Which letter do you want to trace?")
letter = listen()

if letter:
    speak(f"Okay! Let's trace the letter {letter.upper()}")
