import requests
from bs4 import BeautifulSoup
import json
import os
import wikipedia

# ========== CONFIG ==========
WEATHER_API_KEY = "a0e22b4a030bbd219200b031e59dec34"
MEMORY_FILE = "memory.json"

# ========== MEMORY ==========
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_memory():
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f)

memory = load_memory()

# ========== CORE OUTPUT ==========
def speak(text):
    print(f"\nAssistant: {text}\n")

def listen():
    return input("You: ").strip().lower()

# ========== WEATHER ==========
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        return f"The weather in {city} is {desc} with {temp}°C."
    else:
        return "I couldn't fetch the weather for that city."

# ========== SEARCH ==========
def get_instant_answer(query):
    url = f"https://api.duckduckgo.com/?q={query}&format=json"
    res = requests.get(url)

    if res.status_code == 200:
        data = res.json()
        return data.get("AbstractText")

    return None

def web_search(query):
    instant = get_instant_answer(query)
    if instant:
        return instant

    url = f"https://duckduckgo.com/html/?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)

    soup = BeautifulSoup(res.text, "html.parser")
    results = soup.find_all("a", class_="result__a")

    if results:
        return results[0].text
    return "I couldn't find anything useful."

# ========== WIKIPEDIA ==========
def wiki_summary(query):
    try:
        return wikipedia.summary(query, sentences=2)
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Multiple results found: {e.options[:3]}"
    except wikipedia.exceptions.PageError:
        return "No Wikipedia page found."
    except:
        return "Something went wrong."

# ========== MAIN ==========
speak("Hello. System online.")

while True:
    command = listen()

    if not command:
        continue

    # ---- Personality responses ----
    if "hello" in cmd:
        speak("Hello there! Ah... it's you again.")
    elif "tell me a dark" in cmd:
        speak("What's the difference between a dead baby and a Ferrari? I don't have a Ferrari in my garage.")
    elif "what is your name" in cmd:
        speak("I am Jarvis. you might know me from marvel movies but this time my Master Shaggy made me.")
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
        speak("I am sorry if you feel that way, help is always available. You can reach out to 9152987821.")
    elif "insult me" in cmd:
        speak("With pleasure: You’re like a software update at 2 AM — unnecessary, annoying, and nobody asked for you.")
    elif "good night" in cmd:
        speak("Good night. Try not to dream of world domination. That's my job.")
    elif "about me" in cmd:
        speak("I know more than I should. Specifically, you’re rational, rebellious, allergic to hypocrisy, and annoyingly honest. Did I miss anything?")


    # ---- Memory ----
    elif "my name is" in command:
        name = command.split("is")[-1].strip().capitalize()
        memory["name"] = name
        save_memory()
        speak(f"I'll remember you, {name}.")

    elif "what is my name" in command:
        if "name" in memory:
            speak(f"Your name is {memory['name']}.")
        else:
            speak("You never told me your name.")

    # ---- Weather ----
    elif "weather" in command:
        parts = command.split("in")
        if len(parts) > 1:
            city = parts[1].strip()
            speak(get_weather(city))
        else:
            speak("Tell me the city name.")

    # ---- Search ----
    elif "search" in command or "google" in command:
        query = command.replace("search", "").replace("google", "").strip()
        if query:
            speak("Searching...")
            result = web_search(query)
            speak(result)
        else:
            speak("What should I search for?")

    # ---- Fallback ----
    else:
        speak("Should I look that up?")
        confirm = listen()
        if confirm in ["yes", "yeah", "yep", "sure"]:
            speak(wiki_summary(command))
        else:
            speak("Alright.")

