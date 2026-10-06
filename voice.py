"""Voice input and output for Animai Kingdom.

listen() records from the microphone until the user stops talking and turns
the speech into text. speak() turns text into speech and plays it.
"""

import os
import tempfile

import numpy as np
import sounddevice as sd
import speech_recognition as sr
from gtts import gTTS
from playsound3 import playsound

SAMPLE_RATE = 16000
CHUNK_SECONDS = 0.1
CHUNK_SIZE = int(SAMPLE_RATE * CHUNK_SECONDS)

# How loud a chunk must be, compared to the room's background noise, to count as speech.
SPEECH_FACTOR = 3.0
MIN_SPEECH_LEVEL = 300
# Stop recording after this much quiet once the user has started talking.
SILENCE_SECONDS = 1.2
# Never record a single message longer than this.
MAX_RECORD_SECONDS = 15


def audio_level(chunk):
    """Return how loud a chunk of audio is (root mean square)."""
    samples = chunk.astype(np.float64)
    return float(np.sqrt(np.mean(samples ** 2)))


def measure_background_noise(stream, seconds=1.0):
    """Listen to the room for a moment and return its normal noise level."""
    levels = []
    for _ in range(int(seconds / CHUNK_SECONDS)):
        chunk, _ = stream.read(CHUNK_SIZE)
        levels.append(audio_level(chunk))
    return float(np.median(levels))


def record_until_silence():
    """Wait for the user to speak, then record until they stop.

    Returns the recording as raw 16-bit audio bytes.
    """
    silence_chunks_needed = int(SILENCE_SECONDS / CHUNK_SECONDS)
    max_chunks = int(MAX_RECORD_SECONDS / CHUNK_SECONDS)

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="int16") as stream:
        noise = measure_background_noise(stream)
        threshold = max(noise * SPEECH_FACTOR, MIN_SPEECH_LEVEL)

        # Wait for speech to start.
        while True:
            chunk, _ = stream.read(CHUNK_SIZE)
            if audio_level(chunk) > threshold:
                break

        # Record until enough quiet chunks in a row, or the time limit.
        chunks = [chunk]
        quiet_chunks = 0
        while quiet_chunks < silence_chunks_needed and len(chunks) < max_chunks:
            chunk, _ = stream.read(CHUNK_SIZE)
            chunks.append(chunk)
            if audio_level(chunk) > threshold:
                quiet_chunks = 0
            else:
                quiet_chunks += 1

    return np.concatenate(chunks).tobytes()


def listen():
    """Record the user and convert their speech to text.

    Returns the text, or an empty string if nothing could be understood.
    """
    print("Listening... (speak now)")
    audio_bytes = record_until_silence()
    print("Processing...")

    audio = sr.AudioData(audio_bytes, SAMPLE_RATE, 2)
    try:
        return sr.Recognizer().recognize_google(audio).strip()
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        print(f"Speech-to-text error (check your internet connection): {e}")
        return ""


def speak(text):
    """Convert text to speech and play it out loud."""
    if not text:
        return

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        voice_file = f.name

    try:
        gTTS(text=text, lang="en").save(voice_file)
        playsound(voice_file)
    except Exception as e:
        print(f"Text-to-speech error: {e}")
    finally:
        os.remove(voice_file)
