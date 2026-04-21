import os
import time
import random
import webbrowser
from datetime import datetime
import threading

import sounddevice as sd
import speech_recognition as sr
from gtts import gTTS
from playsound3 import playsound

ASSISTANT_NAME = "HeyShark"
VOICE_FILE = "voice.mp3"
THINKING_SOUND = "train_whistle.mov"

WAKE_WORDS = ["hey shark", "shark", "heyshark"]

WAKE_RESPONSES = [
    "What can I do for you?",
    "Let's get to it.",
    "Move along. I'm listening.",
    "Stay sharp. Talk to me.",
    "Let's move. What do you need?",
]

UNKNOWN_RESPONSES = [
    "That wasn't clear. Stay focused and try again.",
    "I need a stronger command than that.",
    "Let's tighten that up and try again.",
    "Move with purpose. Say that one more time.",
    "You're losing momentum. Try again.",
]

MOTIVATION_LINES = [
    "Keep it moving.",
    "Stay locked in.",
    "You have work to do.",
    "Let's stay productive.",
    "Discipline beats delay.",
    "Momentum matters.",
]

TRAINING_MODE_LINES = [
    "Training mode activated. Lock in.",
    "Training mode on. No drifting.",
    "You're in training mode now. Stay moving.",
]

PRODUCTIVITY_LINES = [
    "Focus on the next task.",
    "One step. Then the next.",
    "Stay consistent.",
    "Progress is built through motion.",
]

STARTUP_LINES = [
    "HeyShark online. Stay sharp and get moving.",
    "HeyShark ready. Let's get to work.",
    "Systems ready. Stay focused.",
]


def speak(text):
    """Convert text to speech and play it."""
    try:
        print(f"{ASSISTANT_NAME}: {text}")
        tts = gTTS(text=text, lang="en")
        tts.save(VOICE_FILE)
        playsound(VOICE_FILE)
        time.sleep(0.3)
    except Exception as e:
        print(f"Speech error: {e}")


def play_thinking_sound():
    """Play thinking sound in the background so it does not block speech."""
    def play():
        try:
            playsound(THINKING_SOUND)
        except Exception as e:
            print(f"Thinking sound error: {e}")

    threading.Thread(target=play, daemon=True).start()


def listen(duration=3, fs=16000):
    """Record audio and convert speech to text."""
    recognizer = sr.Recognizer()
    print("Listening now... speak")

    try:
        recording = sd.rec(
            int(duration * fs),
            samplerate=fs,
            channels=1,
            dtype="int16"
        )
        sd.wait()

        print("Processing...")

        audio_data = recording.flatten().tobytes()
        audio = sr.AudioData(audio_data, fs, 2)

        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text.lower().strip()

    except Exception as e:
        print(f"Could not understand audio: {e}")
        return ""


def is_wake_word(text):
    """Check if the wake word was spoken."""
    return any(wake_word in text for wake_word in WAKE_WORDS)


def tell_time():
    return datetime.now().strftime("It is %I:%M %p.")


def tell_date():
    return datetime.now().strftime("Today is %A, %B %d, %Y.")


def open_google():
    webbrowser.open("https://www.google.com")
    return "Opening Google. Stay on task."


def open_youtube():
    webbrowser.open("https://www.youtube.com")
    return "Opening YouTube. Use it well."


def open_chatgpt():
    webbrowser.open("https://chatgpt.com")
    return "Opening ChatGPT. Let's work."


def open_vscode():
    os.system("open -a 'Visual Studio Code'")
    return "Opening Visual Studio Code. Time to build."


def open_finder():
    os.system("open .")
    return "Opening Finder. Keep moving."


def tell_joke():
    jokes = [
        "Why don't sharks like weak ideas? Because they smell hesitation.",
        "Why did the shark become a coach? Because it never stops moving.",
        "Why was the computer nervous around the shark? Too much byte.",
    ]
    return random.choice(jokes)


def assistant_help():
    return (
        "You can ask me to tell the time, tell the date, open Google, "
        "open YouTube, open ChatGPT, open Visual Studio Code, open Finder, "
        "motivate you, start training mode, tell a joke, or say goodbye."
    )


def motivational_push():
    return random.choice(MOTIVATION_LINES)


def productivity_push():
    return random.choice(PRODUCTIVITY_LINES)


def start_training_mode():
    return random.choice(TRAINING_MODE_LINES)


def handle_command(text):
    """Handle user commands and return a spoken response."""
    if not text:
        return "I didn't catch that. Speak with purpose."

    text = text.lower().strip()

    greetings = ["hello", "hi", "hey"]
    identity = ["what is your name", "who are you", "your name", "tell me your name"]
    time_cmds = ["what time is it", "tell me the time", "current time", "time is it"]
    date_cmds = ["what date is it", "what day", "today", "tell me the date", "current date"]
    google_cmds = ["open google", "go to google"]
    youtube_cmds = ["open youtube", "go to youtube"]
    chatgpt_cmds = ["open chatgpt", "go to chatgpt"]
    vscode_cmds = ["open vs code", "open visual studio code", "open code", "launch vs code"]
    finder_cmds = ["open finder", "open my files"]
    motivate_cmds = ["motivate me", "push me", "give me motivation", "say something motivating"]
    training_cmds = ["training mode", "start training mode", "activate training mode"]
    focus_cmds = ["focus mode", "start focus mode", "activate focus mode"]
    status_cmds = ["status", "system status", "how are you", "report status"]
    help_cmds = ["help", "what can you do", "show commands", "what do you do"]
    joke_cmds = ["joke", "tell me a joke", "make me laugh"]
    version_cmds = ["stage", "version", "what version", "what stage"]
    exit_cmds = ["exit", "mute", "goodbye", "shut down", "stop"]

    if any(cmd in text for cmd in greetings):
        return "HeyShark is here. What can I do for you?"
    if any(cmd in text for cmd in identity):
        return "I am HeyShark. Built to keep you moving."
    if any(cmd in text for cmd in time_cmds):
        return f"{tell_time()} {motivational_push()}"
    if any(cmd in text for cmd in date_cmds):
        return f"{tell_date()} Stay on schedule."
    if any(cmd in text for cmd in google_cmds):
        return open_google()
    if any(cmd in text for cmd in youtube_cmds):
        return open_youtube()
    if any(cmd in text for cmd in chatgpt_cmds):
        return open_chatgpt()
    if any(cmd in text for cmd in vscode_cmds):
        return open_vscode()
    if any(cmd in text for cmd in finder_cmds):
        return open_finder()
    if any(cmd in text for cmd in motivate_cmds):
        return "Get up, lock in, and handle what is in front of you."
    if any(cmd in text for cmd in training_cmds):
        return start_training_mode()
    if any(cmd in text for cmd in focus_cmds):
        return "Focus mode engaged. Cut distractions and move."
    if any(cmd in text for cmd in status_cmds):
        return f"HeyShark is active. {productivity_push()}"
    if any(cmd in text for cmd in help_cmds):
        return assistant_help()
    if any(cmd in text for cmd in joke_cmds):
        return tell_joke()
    if any(cmd in text for cmd in version_cmds):
        return "I am HeyShark, phase two point three. Sharper and stronger."
    if any(cmd in text for cmd in exit_cmds):
        return "EXIT"

    return random.choice(UNKNOWN_RESPONSES)


def run_assistant():
    """Main loop with wake word support."""
    print(f"{ASSISTANT_NAME} is in sleep mode. Say 'Hey Shark' to wake me up.")
    speak(random.choice(STARTUP_LINES))

    while True:
        text = listen(duration=2)

        if not text:
            continue

        if is_wake_word(text):
            speak(random.choice(WAKE_RESPONSES))
            time.sleep(0.8)

            command = listen(duration=5)

            if not command:
                speak("I didn't hear a command. Stay sharp and try again.")
                continue

            play_thinking_sound()
            result = handle_command(command)

            if result == "EXIT":
                speak("Goodbye. Stay disciplined.")
                break

            speak(result)


if __name__ == "__main__":
    run_assistant()