# Import time module for delays
import time
# Import playsound3 for audio playback
from playsound3 import playsound
# Import gTTS for text-to-speech conversion
from gtts import gTTS
# Import speech_recognition for audio-to-text conversion
import speech_recognition as sr
# Import sounddevice for audio recording
import sounddevice as sd
# Import numpy for audio data handling
import numpy as np
# Import requests for HTTP requests
import requests

# Configuration section header
# 🔹 CONFIGURE THESE
# Set your Google API Key for search functionality
API_KEY = "AIzaSyAkHL-Hs_jQq9RHkMlSAgVEtq6bCogUJJY"  # Your Google API Key
# Set your Custom Search Engine ID
CSE_ID = "37e6519dabc1d4851"                          # Your Custom Search Engine ID
# End of configuration section
# 🔹 CONFIGURE THESE

# Define function to perform Google searches
def google_search(api_key, search_engine_id, query, **extra_params):
    # Set the Google Custom Search API endpoint URL
    url = "https://www.googleapis.com/customsearch/v1"

    # Create a dictionary with base API parameters
    params = {
        "key": api_key,
        "cx": search_engine_id,
        "q": query,
        "num": 1
    }

    # Merge any additional parameters into the params dictionary
    params.update(extra_params)

    # Use try-except to handle errors
    try:
        # Send GET request to Google API
        response = requests.get(url, params=params)
        # Raise an exception if the HTTP status code indicates an error
        response.raise_for_status()
        # Parse the JSON response
        data = response.json()
        # Print the response data for debugging
        print(data)  # Optional: debug output

        # Check if search results are in the response
        if "items" in data:
            # Return the first result's snippet, limited to 300 characters
            return data["items"][0]["snippet"][:300]  # limit snippet for faster speech
        # If no items found, return a default message
        else:
            return "I couldn't find an answer."
    # Catch HTTP errors
    except requests.exceptions.HTTPError as e:
        # Print the HTTP error
        print("HTTP error:", e)
        # Return an error message
        return "Search failed due to HTTP error."
    # Catch all other exceptions
    except Exception as e:
        # Print the error
        print("Error:", e)
        # Return a generic error message
        return "Search failed due to an error."

# Define function to convert text to speech and play it
def speak(text):
    # Create a gTTS object with the text in English
    tts = gTTS(text=text, lang="en")
    # Set the output filename
    filename = "voice.mp3"
    # Save the audio to the file
    tts.save(filename)
    # Play the audio file
    playsound(filename)
    # Wait 0.5 seconds to ensure microphone is ready
    time.sleep(0.5)  # ensure mic is free

# Define function to capture and recognize audio
def get_audio(duration=5, fs=16000):
    # Create a Recognizer object for speech recognition
    r = sr.Recognizer()
    # Print status message
    print("Listening...")

    # Record audio using sounddevice for the specified duration
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    # Wait for recording to complete
    sd.wait()
    # Convert the recording to bytes
    audio_data = recording.flatten().tobytes()
    # Create an AudioData object for recognition (width=2 for int16 format)
    audio = sr.AudioData(audio_data, fs, 2)  # width=2 for int16

    # Use try-except to handle recognition errors
    try:
        # Use Google Speech Recognition to convert audio to text
        said = r.recognize_google(audio)
        # Print what the user said
        print("You said:", said)
        # Return the recognized text in lowercase
        return said.lower()
    # Catch any recognition errors
    except Exception as e:
        # Print the error message
        print("Could not understand audio:", e)
        # Return empty string if recognition fails
        return ""

# Main assistant loop section header
# 🔹 MAIN ASSISTANT LOOP
# 🔹 MAIN ASSISTANT LOOP
# Initial greeting
speak("Hello sir")
# Start infinite loop for continuous listening
while True:
    # Get audio input from user
    text = get_audio()

    # Check if text is empty or has less than 2 characters
    if not text or len(text.strip()) < 2:
        # Skip to next iteration if input is too short
        continue  # skip empty input

    # Check if user wants to perform a Google search
    if "search" in text or "google" in text:
        # Extract the search query by removing search keywords
        query = text.replace("search", "").replace("google", "").strip()
        # Check if a query was provided
        if query:
            # Inform user that search is starting
            speak("Searching")
            # Perform the Google search
            result = google_search(API_KEY, CSE_ID, query)
            # Speak the search result
            speak(result)
        # If no query provided, ask user to specify search terms
        else:
            speak("Please tell me what to search.")

    # Check for predefined responses
    # Check if user asked for the assistant's name
    elif "what is your name" in text:
        # Respond with philosophical answer
        speak("I am a being that you have created.")
    # Check if user mentioned "name"
    elif "name" in text:
        # Respond with creator's name
        speak("I am a being that was created by Josiah.")
    # Check if user said hello
    elif "hello" in text:
        # Respond with greeting
        speak("Hello sir, how are you doing today?")
    # Check if user mentioned "stage" or version
    elif "stage" in text:
        # Respond with version information
        speak("I am in version 0.01, your future plans are to improve me, right?")
    # Check if user wants to exit or mute the assistant
    elif "exit" in text or "mute" in text:
        # Say goodbye
        speak("Goodbye sir")
        # Exit the main loop
        break  # Stop assistant
