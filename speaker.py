import shutil
import os
from playsound import playsound
import pyaudio
import wave
from pydub import AudioSegment
import time
import edge_tts
import asyncio
from io import BytesIO
import threading

CHUNK_SIZE = 20 * 1024  # Assuming around 1024 bytes per chunk (adjust based on format)

stop_event = threading.Event()

async def speak_blocking(text):
    global stop_event
    stop_event.clear()  # Clear the stop event before starting playback
    try:
        communicate = edge_tts.Communicate(text, "en-GB-RyanNeural", rate="+13%")
        pyaudio_instance = pyaudio.PyAudio()
        audio_stream = pyaudio_instance.open(format=pyaudio.paInt16, channels=1, rate=24000, output=True)

        total_data = b''  # Store audio data instead of chunks

        async for chunk in communicate.stream():
            if chunk["type"] == "audio" and chunk["data"]:
                if stop_event.is_set():
                    print("Playback interrupted")
                    break  # Stop playback if interrupted
                print(f"Received chunk of size: {len(chunk['data'])} bytes")  # Debug print
                total_data += chunk["data"]
                if len(total_data) >= CHUNK_SIZE:
                    play_audio(total_data[:CHUNK_SIZE], audio_stream)  # Play first CHUNK_SIZE bytes
                    total_data = total_data[CHUNK_SIZE:]  # Remove played data
                    if stop_event.is_set():
                        break  # Stop playback if interrupted

        # Play remaining audio if not interrupted
        if not stop_event.is_set() and total_data:
            play_audio(total_data, audio_stream)

        audio_stream.stop_stream()
        audio_stream.close()
        pyaudio_instance.terminate()
        print("Playback finished")
    except Exception as e:
        print(f"An error occurred during speech generation: {e}")

def play_audio(data: bytes, stream: pyaudio.Stream) -> None:
    stream.write(AudioSegment.from_mp3(BytesIO(data)).raw_data)
    if stop_event.is_set():
        print("Playback interrupted during play_audio")
        return  # Stop playback if interrupted

def stop_playback():
    global stop_event
    stop_event.set()

def speak(text):
    threading.Thread(target=asyncio.run, args=(speak_blocking(text),)).start()
