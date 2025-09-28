from pyautogui import sleep
import openai
import os
import time
import numpy as np
os.environ["SD_ENABLE_ASIO"] = "1"
from dotenv import load_dotenv
load_dotenv(f'{os.path.dirname(os.path.realpath(__file__))}/../../../../.env')
import sounddevice as sd
import queue
import wave
from io import BytesIO
import threading

print(sd.query_hostapis())

class Transcriber:
    def __init__(self):
        openai.api_key = os.getenv("OPEN_API_KEY")
        self.client = openai
        self.recording = False
        self.audio_queue = None
        self.stream = None
        self.recording_thread = None

        self.file = None

    def begin_recording(self):
        """Starts recording audio and saves it to a BytesIO object."""
        if self.recording:
            print("Already recording!")
            return

        self.file = BytesIO()
        self.file.name = "audio.wav"

        self.recording = True
        self.audio_queue = queue.Queue()

        def callback(indata, frames, time, status):
            """Callback function to capture audio data."""
            if status:
                print("Status:", status)
            if self.recording:
                self.audio_queue.put((indata[:, 0] * 32767).astype(np.int16))

        def recording_worker():
            """Worker function to handle audio recording in a separate thread."""
            with wave.open(self.file, mode="wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(44100)

                print("Recording started... Call end_recording() to stop.")

                while self.recording:
                    try:
                        # Get audio data with timeout to allow checking recording flag
                        data = self.audio_queue.get(timeout=0.1)
                        wf.writeframes(data.tobytes())
                    except queue.Empty:
                        continue  # Continue loop to check if recording should stop

                # Process any remaining data in the queue
                while not self.audio_queue.empty():
                    try:
                        data = self.audio_queue.get_nowait()
                        wf.writeframes(data.tobytes())
                    except queue.Empty:
                        break

                print("Recording stopped.")

        # Start the audio stream
        self.stream = sd.InputStream(
            samplerate=44100,
            channels=1,
            blocksize=1024,
            callback=callback
        )
        self.stream.start()

        self.recording_thread = threading.Thread(target=recording_worker)
        self.recording_thread.start()

    def end_recording(self):
        """Stops the current recording."""
        if not self.recording:
            print("No recording in progress!")
            return

        print("Stopping recording...")
        self.recording = False

        if self.recording_thread:
            self.recording_thread.join()

        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        self.audio_queue = None

    def transcribe(self):
        """Transcribes the audio from the BytesIO object using OpenAI's Whisper model."""
        if self.file == None:
            print("Failed to fetch audio recording")
            return

        self.file.seek(0)
        try:
            transcription = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=self.file,
                response_format="text"
            )
            print("Transcription:", transcription)
            return transcription
        except Exception as e:
            print(f"Error during transcription: {e}")
            return None
