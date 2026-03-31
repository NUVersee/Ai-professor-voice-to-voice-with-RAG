import requests
import sounddevice as sd
from scipy.io.wavfile import write
import pygame
import keyboard
import time
import numpy as np
from urllib.parse import unquote

# --- Settings ---
HUGGING_FACE_URL = "https://ayyyhaga-prof2-ayhaga.hf.space/voice-to-voice"
SAMPLE_RATE = 16000
INPUT_FILENAME = "input.wav"
OUTPUT_FILENAME = "professor_voice.wav"

def record_audio():
    """Records audio while SPACE is held."""
    print("\n" + "=" * 30)
    print(":) Hold SPACE to talk to the Professor...")
    keyboard.wait("space")

    print("[LISTENING] Speak now...")
    recording = []

    def callback(indata, frames, time_info, status):
        recording.append(indata.copy())

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        callback=callback
    ):
        while keyboard.is_pressed("space"):
            sd.sleep(100)

    if not recording:
        return False

    audio_data = np.concatenate(recording, axis=0)
    write(INPUT_FILENAME, SAMPLE_RATE, audio_data)
    return True

def upload_and_process():
    """Sends audio and receives transcription, summary, and professor voice."""
    print("[THINKING] Uploading to AI Professor...")

    try:
        with open(INPUT_FILENAME, "rb") as f:
            files = {"file": (INPUT_FILENAME, f, "audio/wav")}
            response = requests.post(HUGGING_FACE_URL, files=files)

        if response.status_code == 200:
            # --- Headers ---
            raw_transcription = response.headers.get(
                "X-User-Transcription", "No transcription found"
            )
            raw_summary = response.headers.get(
                "X-Professor-Summary", "No summary found"
            )

            transcription = unquote(raw_transcription)
            summary = unquote(raw_summary)

            print(f"\n[YOU]: {transcription}")
            print(f"[PROFESSOR]: {summary}")
            print("-" * 30)

            # --- Save audio ---
            with open(OUTPUT_FILENAME, "wb") as f:
                f.write(response.content)

            # --- Play audio ---
            play_audio(OUTPUT_FILENAME)

        else:
            print(f"Error {response.status_code}: {response.text}")

    except Exception as e:
        print(f"Connection Error: {e}")

def play_audio(file_path):
    """Plays audio and safely releases file (Windows-friendly)."""
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

    # 🔑 CRITICAL FIX FOR WINDOWS FILE LOCKING
    pygame.mixer.music.stop()
    pygame.mixer.music.unload()
    pygame.mixer.quit()

def main():
    print("AI PROFESSOR TERMINAL INITIALIZED")
    try:
        while True:
            if record_audio():
                upload_and_process()
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nGoodbye!")

if __name__ == "__main__":
    main()
