# mphunzitsi_dynamic.py
import re
import joblib
import torch
import torchaudio
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import pyttsx3
import numpy as np
from playsound import playsound
import time


engine = pyttsx3.init()
engine.setProperty('rate', 160)

def speak(text):
    engine.say(text)
    engine.runAndWait()

processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
model_stt = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")

import sounddevice as sd
def record_audio(duration=5, fs=16000):
    print("Listening...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
    sd.wait()
    audio = np.squeeze(audio)
    return audio

def speech_to_text(audio):
    input_values = processor(audio, sampling_rate=16000, return_tensors="pt").input_values
    with torch.no_grad():
        logits = model_stt(input_values).logits
    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = processor.batch_decode(predicted_ids)[0]
    return transcription.lower()

training_data = [
    ("hello", "greeting"),
    ("hi there", "greeting"),
    ("hey", "greeting"),
    ("trace letter a", "trace"),
    ("i want to learn b", "trace"),
    ("goodbye", "goodbye"),
    ("bye", "goodbye"),
    ("thank you", "gratitude"),
]

X_train = [x[0] for x in training_data]
y_train = [x[1] for x in training_data]

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression

vectorizer = CountVectorizer()
X_vec = vectorizer.fit_transform(X_train)

model_ml = LogisticRegression()
model_ml.fit(X_vec, y_train)

# NLP / Response(loop response)
success_sound = "success.mp3"
error_sound = "error.mp3"

def generate_response(user_text):
    # Use ML model to predict intent
    x_vec = vectorizer.transform([user_text])
    intent = model_ml.predict(x_vec)[0]

    if intent == "greeting":
        response = "Hello! Ready to trace some letters today?"
    elif intent == "trace":
        letter_match = re.search(r'[a-z]', user_text)
        if letter_match:
            response = f"Let's trace the letter {letter_match.group().upper()}. Follow the dots carefully!"
        else:
            response = "Which letter would you like to trace?"
    elif intent == "goodbye":
        response = "Goodbye! You did amazing today. See you next time!"
    else:
        response = "Hmm, I didn’t quite get that. Can you say the letter you want to trace?"
    
    playsound(success_sound)
    
    return response

# Main Loop (continuous)

if __name__ == "__main__":
    speak("Hello! I'm Mphunzitsi AI. Which letter would you like to trace?")
    while True:
        audio_data = record_audio(duration=5)
        text = speech_to_text(audio_data)
        if not text:
            speak("Sorry, I didn't catch that. Try again.")
            playsound(error_sound)
            continue
        print("You said:", text)

        if "exit" in text or "quit" in text:
            speak("Goodbye for now!")
            break

        response = generate_response(text)
        print("AI:", response)
        speak(response)
        time.sleep(1)
