import os  # Import os module for operating system interactions
import time  # Import time module for delays and timing
import random  # Import random module for random selections
import webbrowser  # Import webbrowser module to open web pages
from datetime import datetime  # Import datetime for date and time functions

import sounddevice as sd  # Import sounddevice for audio recording
import speech_recognition as sr  # Import speech_recognition for speech-to-text
from gtts import gTTS  # Import gTTS for text-to-speech conversion
from playsound3 import playsound  # Import playsound3 to play audio files

ASSISTANT_NAME = "Animai"  # Define the assistant's name
VOICE_FILE = "voice.mp3"  # Define the filename for voice output

WAKE_WORDS = ["Hey Shark"]  # List of wake words to activate the assistant
WAKE_RESPONSES = [  # List of responses when wake word is detected
    "I'm listening.",
    "Yes?",
    "How can I help?",
    "Ready.",
    "What can I do for you?",
    
]


def speak(text):  # Function to convert text to speech and play it
    """Convert text to speech and play it."""  # Docstring for the function
    try:  # Try block for error handling
        print(f"{ASSISTANT_NAME}: {text}")  # Print the assistant's response to console
        tts = gTTS(text=text, lang="en")  # Create a gTTS object with the text
        tts.save(VOICE_FILE)  # Save the speech to a file
        playsound(VOICE_FILE)  # Play the saved audio file
        time.sleep(0.3)  # Short delay after speaking
    except Exception as e:  # Catch any exceptions
        print(f"Speech error: {e}")  # Print error message


def listen(duration=3, fs=16000):  # Function to record audio and convert to text
    """Record audio and convert speech to text."""  # Docstring
    recognizer = sr.Recognizer()  # Create a recognizer instance
    print("Listening...")  # Print listening message

    try:  # Try block for recording and recognition
        recording = sd.rec(  # Record audio using sounddevice
            int(duration * fs),  # Number of samples
            samplerate=fs,  # Sample rate
            channels=1,  # Mono channel
            dtype="int16"  # Data type
        )
        sd.wait()  # Wait for recording to finish

        print("Processing...")  # Print processing message

        audio_data = recording.flatten().tobytes()  # Flatten and convert to bytes
        audio = sr.AudioData(audio_data, fs, 2)  # Create AudioData object

        text = recognizer.recognize_google(audio)  # Recognize speech using Google
        print(f"You said: {text}")  # Print recognized text
        return text.lower().strip()  # Return lowercase, stripped text

    except Exception as e:  # Catch exceptions
        print(f"Could not understand audio: {e}")  # Print error
        return ""  # Return empty string on failure


def is_wake_word(text):  # Function to check if wake word is in text
    """Check if the wake word was spoken."""  # Docstring
    return any(wake_word in text for wake_word in WAKE_WORDS)  # Check for any wake word


def tell_time():  # Function to get current time
    return datetime.now().strftime("It is %I:%M %p.")  # Format and return time


def tell_date():  # Function to get current date
    return datetime.now().strftime("Today is %A, %B %d, %Y.")  # Format and return date


def open_google():  # Function to open Google
    webbrowser.open("https://www.google.com")  # Open Google in browser
    return "Opening Google."  # Return response message


def open_youtube():  # Function to open YouTube
    webbrowser.open("https://www.youtube.com")  # Open YouTube in browser
    return "Opening YouTube."  # Return response message


def open_chatgpt():  # Function to open ChatGPT
    webbrowser.open("https://chatgpt.com")  # Open ChatGPT in browser
    return "Opening ChatGPT."  # Return response message


def open_vscode():  # Function to open VS Code
    os.system("open -a 'Visual Studio Code'")  # Open VS Code using os command
    return "Opening Visual Studio Code."  # Return response message


def tell_joke():  # Function to tell a random joke
    jokes = [  # List of jokes
        "Why did the robot go to art school? Because it wanted to draw better circuits.",
        "Why was the computer cold? Because it left its windows open.",
        "Why did the AI assistant get promoted? Because it always had the right response."
    ]
    return random.choice(jokes)  # Return a random joke


def assistant_help():  # Function to provide help information
    return (  # Return help text
        "You can ask me to tell the time, tell the date, "
        "open Google, open YouTube, open ChatGPT, open Visual Studio Code, "
        "tell a joke, or say goodbye."
    )


def handle_command(text):  # Function to handle user commands
    """Handle user commands and return a spoken response."""  # Docstring
    if not text:  # If no text provided
        return "I didn't catch that."  # Return error message

    if "hello" in text or "hi" in text:  # Check for greeting
        return "Hello. I am ready."  # Return greeting response

    elif "what is your name" in text or "who are you" in text:  # Check for name query
        return f"I am {ASSISTANT_NAME}, your assistant."  # Return name response

    elif "time" in text:  # Check for time request
        return tell_time()  # Call tell_time function

    elif "date" in text or "today" in text:  # Check for date request
        return tell_date()  # Call tell_date function

    elif "open google" in text:  # Check for open Google
        return open_google()  # Call open_google function

    elif "open youtube" in text:  # Check for open YouTube
        return open_youtube()  # Call open_youtube function

    elif "open chatgpt" in text:  # Check for open ChatGPT
        return open_chatgpt()  # Call open_chatgpt function

    elif "open vs code" in text or "open visual studio code" in text:  # Check for open VS Code
        return open_vscode()  # Call open_vscode function

    elif "joke" in text:  # Check for joke request
        return tell_joke()  # Call tell_joke function

    elif "help" in text or "what can you do" in text:  # Check for help request
        return assistant_help()  # Call assistant_help function

    elif "stage" in text or "version" in text:  # Check for version info
        return "I am in phase two point one with wake word support."  # Return version response

    elif "exit" in text or "mute" in text or "goodbye" in text:  # Check for exit commands
        return "EXIT"  # Return exit signal

    return "I heard you, but I do not know how to respond to that yet."  # Default response


def run_assistant():  # Main function to run the assistant
    """Main loop with wake word support."""  # Docstring
    print(f"{ASSISTANT_NAME} is in sleep mode. Say 'Hey Animai' to wake me up.")  # Print initial message

    while True:  # Infinite loop for continuous listening
        text = listen(duration=2)  # Listen for wake word with short duration

        if not text:  # If no text heard
            continue  # Continue loop

        if is_wake_word(text):  # If wake word detected
            speak(random.choice(WAKE_RESPONSES))  # Speak a random wake response

            command = listen(duration=4)  # Listen for command with longer duration

            if not command:  # If no command heard
                speak("I didn't hear a command.")  # Speak error message
                continue  # Continue loop

            result = handle_command(command)  # Handle the command

            if result == "EXIT":  # If exit signal
                speak("Goodbye.")  # Speak goodbye
                break  # Break out of loop

            speak(result)  # Speak the result


if __name__ == "__main__":  # If script is run directly
    run_assistant()  # Call the main function