import openai
import speech_recognition as sr
import pyttsx3
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get OpenAI API key from environment
OPENAI_KEY = os.getenv('OPENAI_KEY')

# Ensure the OpenAI key is set
if not OPENAI_KEY:
    raise ValueError(
        "OPENAI_KEY environment variable is not set. Check your .env file.")

# Set the OpenAI API key
openai.api_key = OPENAI_KEY


def SpeakText(command):
    engine = pyttsx3.init()
    engine.say(command)
    engine.runAndWait()


r = sr.Recognizer()


def record_text():
    try:
        with sr.Microphone() as source2:
            r.adjust_for_ambient_noise(source2, duration=0.25)
            print("I'm listening")
            audio2 = r.listen(source2)
            MyText = r.recognize_google(audio2)
            return MyText
    except sr.RequestError as e:
        print(f"Could not request results: {e}")
    except sr.UnknownValueError:
        print("An Unknown Error occurred...")


def send_to_chatGPT(messages, model="gpt-3.5-turbo"):
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            max_tokens=1000,
            n=1,
            stop=None,
            temperature=0.5,
        )
        message = response.choices[0].message['content']
        messages.append({'role': 'assistant', 'content': message})
        return message
    except Exception as e:
        print(f"Error communicating with OpenAI API: {e}")
        return "Sorry, I'm having trouble reaching OpenAI at the moment."


# Initial message to the AI
messages = [{'role': 'user',
             'content': 'Please act like Jarvis from Iron Man or like the Computer in Star Trek'}]

# Main loop for the chatbot
while True:
    text = record_text()
    if text:
        messages.append({'role': 'user', 'content': text})
        response = send_to_chatGPT(messages)
        SpeakText(response)
        print(response)
