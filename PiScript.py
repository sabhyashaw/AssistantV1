import pyttsx3
import requests
import json
import os

# ================= CONFIG =================
WEATHER_API_KEY = "a0e22b4a030bbd219200b031e59dec34"
MEMORY_FILE = "memory.json"

# ================= INIT =================
engine = pyttsx3.init()

# Male voice & faster
voices = engine.getProperty('voices')
for voice in voices:
    if "male" in voice.name.lower():
        engine.setProperty('voice', voice.id)
        break

engine.setProperty('rate', 200)

# ================= MEMORY =================
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_memory():
    with open(MEMORY_FILE, 'w') as f:
        json.dump(memory, f)

memory = load_memory()

# ================= SPEAK =================
def speak(text):
    print(f"Jarvis: {text}")
    engine.say(text)
    engine.runAndWait()

# ================= TEXT INPUT =================
def listen():
    return input("You: ").strip().lower()

# ================= WEATHER =================
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

# ================= LOCAL LLM =================
def query_remote_llm(prompt):
    try:
        response = requests.post(
            "http://192.168.0.115:5000/ask",
            json={"prompt": prompt},
            timeout=120
        )
        return response.json().get("response", "No response from server.")
    except Exception:
        return "I can't reach my brain right now."

# ================= MAIN =================
speak("Hello I am Jarvis! How can I help you Shaggy?")

while True:
    command = listen()
    if not command:
        continue

    cmd = command.lower()

    # --- Name Memory ---
    if "my name is" in cmd:
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
            speak("I don't know your name yet. Please tell me by saying 'My name is...'")

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

    # --- Exit ---
    elif any(word in cmd for word in ["bye", "stop", "shut up", "you can go", "exit", "quit"]):
        speak("Goodbye. Stay sharp.")
        break

    # --- LLM Fallback ---
    else:
        speak("Thinking...")
        response = query_remote_llm(cmd)
        speak(response)
