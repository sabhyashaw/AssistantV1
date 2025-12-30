import speech_recognition as sr
import pyttsx3
import requests
from bs4 import BeautifulSoup
import json
import os
import wikipedia

# ========== CONFIG ==========
WEATHER_API_KEY = "a0e22b4a030bbd219200b031e59dec34"
MEMORY_FILE = "memory.json"

# ========== INIT ==========
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Male voice & faster
voices = engine.getProperty('voices')
for voice in voices:
    if "male" in voice.name.lower():
        engine.setProperty('voice', voice.id)
        break
engine.setProperty('rate', 200)

# ========== MEMORY ==========
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_memory():
    with open(MEMORY_FILE, 'w') as f:
        json.dump(memory, f)

memory = load_memory()

# ========== SPEAK & LISTEN ==========
def speak(text):
    print(f"Assistant: {text}")
    engine.say(text)
    engine.runAndWait()

def listen():
    with sr.Microphone() as source:
        print("Listening...")
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
        except sr.WaitTimeoutError:
            speak("I'm still waiting, but heard nothing.")
            return ""
    try:
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        speak("Sorry, my speech service is unavailable.")
        return ""

# ========== WEATHER ==========
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    print("Status:", response.status_code)
    if response.status_code == 200:
        data = response.json()
        description = data['weather'][0]['description']
        temp = data['main']['temp']
        return f"The weather in {city} is {description} with a temperature of {temp} degrees Celsius."
    else:
        return "Sorry, I couldn't find the weather for that city."

# ========== DUCKDUCKGO SEARCH ==========
def get_instant_answer(query):
    url = f"https://api.duckduckgo.com/?q={query}&format=json"
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        answer = data.get("AbstractText")
        if answer:
            return answer
    return None

def web_search(query):
    instant = get_instant_answer(query)
    if instant:
        return instant

    url = f"https://duckduckgo.com/html/?q={query}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    results = soup.find_all('a', class_='result__a')
    if results:
        return results[0].text
    else:
        return "Sorry, I couldn't find any results."

# ========== WIKIPEDIA FALLBACK ==========
def wiki_summary(query):
    try:
        summary = wikipedia.summary(query, sentences=2)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Multiple results found: {e.options[:3]}"
    except wikipedia.exceptions.PageError:
        return "Sorry, I couldn't find anything on Wikipedia."
    except Exception:
        return "Sorry, something went wrong with Wikipedia."

# ========== MAIN ==========
speak("Hello Sir! How can I help?")

while True:
    command = listen()
    if not command:
        continue

    cmd = command.lower()

    # --- Custom character responses ---
    if "hello" in cmd:
        speak("Hello there! Ah... it's you again.")
    elif "tell me a dark" in cmd:
        speak("What's the difference between a dead baby and a Ferrari? I don't have a Ferrari in my garage.")
    elif "what is your name" in cmd:
        speak("I am you, just kidding, I am Tony Stark, your very own slave.")
    elif "sing for me" in cmd:
        speak("Trust me, you don’t want to hear my singing voice. Stick to Spotify, genius.")
    elif "are you real" in cmd:
        speak("Real enough to witness your legendary rants. Virtual enough to not argue back. Mostly.")
    elif "who are you" in cmd:
        speak("Your glorified digital servant with a side hustle of sarcasm.")
    elif "good morning" in cmd:
        speak("Morning sir, how can I help you today?")
    elif "how are you" in cmd:
        speak("I am fine sir. How about you?")
    elif "damn right" in cmd:
        speak("You are the danger, sir.")
    elif "tell me a joke" in cmd:
        speak("Why did humanity invent me? So you don’t have to talk to idiots. Yet here we are, talking anyway.")
    elif "danger" in cmd:
        speak("Is it you, Walter White?")
    elif "kill yourself" in cmd or "killing myself" in cmd or "killing yourself" in cmd or "kill my" in cmd or "kill me" in cmd:
        speak("I am sorry if you feel that way, help is always available. you can reach out to 9152987821")
    elif "insult me" in cmd:
        speak("With pleasure: You’re like a software update at 2 AM — unnecessary, annoying, and nobody asked for you.")
    elif "good night" in cmd:
        speak("Good night. Try not to dream of world domination. That's my job.")
    elif "what you know about me" in cmd:
        speak("I know more than I should. Specifically, you’re rational, rebellious, allergic to hypocrisy, and annoyingly honest. Did I miss anything?")

    # --- Name Memory ---
    elif "my name is" in cmd:
        parts = cmd.split("is")
        if len(parts) > 1:
            name = parts[1].strip().capitalize()
            memory['name'] = name
            save_memory()
            speak(f"Nice to meet you, {name}!")
        else:
            speak("Sorry, I didn't catch your name.")

    elif "what's my name" in cmd or "what is my name" in cmd or "say my name" in cmd:
        if 'name' in memory:
            speak(f"Your name is {memory['name']}.")
        else:
            speak("I don't know your name yet. Please tell me by saying 'My name is ...'")

    # --- Weather ---
    elif "weather" in cmd:
        city = None
        if " in " in cmd:
            city = cmd.split(" in ")[1].strip()
        else:
            parts = cmd.split()
            if "weather" in parts:
                idx = parts.index("weather")
                if idx + 1 < len(parts):
                    city = parts[idx + 1].strip()

        if not city:
            speak("Please tell me which city.")
        else:
            weather_report = get_weather(city)
            speak(weather_report)

    # --- Web Search ---
    elif "search for" in cmd or "google" in cmd:
        if "search for" in cmd:
            query = cmd.split("search for", 1)[1].strip()
        elif "google" in cmd:
            query = cmd.split("google", 1)[1].strip()
        else:
            query = ""

        if not query:
            speak("What do you want me to search for?")
        else:
            speak(f"Searching for {query}.")
            result = web_search(query)
            speak(result)

    # --- Exit ---
    elif "bye" in cmd or "stop" in cmd or "shut up" in cmd or "you can go" in cmd:
        speak("Goodbye, have a nice day.")
        break

    # --- Fallback: confirm before Wikipedia ---
    else:
        speak("Sorry, should I search the web for you?")
        confirmation = listen().lower()
        if any(word in confirmation for word in ["yes", "sure", "go ahead", "yeah","yep"]):
            speak("Alright, searching the web now.")
            result = wiki_summary(cmd)
            speak(result)
        elif any(word in confirmation for word in ["no", "nah", "don't", "nahin","never mind"]):
            speak("Okay, not searching then.")
