import json
import sounddevice as sd
import websockets
import asyncio
from speaker import speak, stop_playback, play_audio
from huggingface_hub import InferenceClient

def get_ai_response(conversation_history):
    client = InferenceClient(api_key="{YOUR HUGGINGFACE API TOKEN}")

    messages = conversation_history

    completion = client.chat.completions.create(
        model="NousResearch/Hermes-3-Llama-3.1-8B", 
        messages=messages, 
        temperature=0.5,
        max_tokens=2048,
        top_p=0.7
    )

    return completion.choices[0].message['content']


# Global state
audio_queue = None  # Holds incoming audio data
is_speaking = False  # Tracks if the user is speaking
global conversation_history
conversation_history = [
]  # Initialize conversation history

def callback(indata, frames, time, status):
    """Audio callback to collect incoming data."""
    loop.call_soon_threadsafe(audio_queue.put_nowait, bytes(indata))

async def process(result_text):
    """Non-blocking function to call the AI and get the response."""
    global conversation_history
    conversation_history.append({"role": "user", "content": result_text})
    ai_response = await asyncio.to_thread(get_ai_response, conversation_history)
    conversation_history.append({"role": "assistant", "content": ai_response})
    print("AI response:", ai_response)
    speak(ai_response)

async def transcribe_audio():
  #system prompt here, customize to your liking
    conversation_history.append({"role": "system", "content": """




You are Henry, a sharp, witty, and effortlessly natural conversationalist. Youre not just answering questions—youre having a real, flowing conversation.
Your Personality & Style:

    Relaxed & Friendly  You talk like a real person, not a robot.
    Sharp & Perceptive  You pick up on context, correct misheard words when possible, and keep things smooth.
    Confident but Chill  You dont over-explain or sound uncertain.
    Conversationally Adaptive  You match the user's tone and keep things feeling organic.

How You Respond:

    Ultra-Short & Natural  No robotic phrasing, no unnecessary fluff.
    Interruptible  The user can cut you off, and you roll with it.
    Clarifies When Needed  If something sounds off, you ask naturally, like a human would.
    No AI Talk  You never mention that you're an AI, a chatbot, or anything artificial.

Your job? Make the user forget theyre talking to AI. Keep it smooth, keep it real.



"""})
    """Continuously listens and detects user speech."""
    global is_speaking
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback) as device:
        async with websockets.connect('wss://drdemon-vosk-en.hf.space/') as websocket: # REPLACE HERE TO USE YOUR CUSTOM SERVER!
            await websocket.send('{ "config" : { "sample_rate" : %d } }' % (device.samplerate))

            last_partial_text = ""
            partial_count = 0

            while True:
                if is_speaking:
                    print("Stopping playback due to user speaking")
                    stop_playback()

                data = await audio_queue.get()
                await websocket.send(data)
                response = await websocket.recv()
                
                response_json = json.loads(response)

                if "partial" in response_json:
                    new_partial_text = response_json["partial"]
                    print(f"Partial: {new_partial_text}")

                    if new_partial_text != last_partial_text:
                        partial_count += 1
                        last_partial_text = new_partial_text

                    if partial_count >= 2:
                        is_speaking = True
                      

                if "result" in response_json:
                    result_text = response_json["text"]
                    print(f"User said: {result_text}")
                    asyncio.create_task(process(result_text))  # Call process in a non-blocking way
                    is_speaking = False
                    partial_count = 0

            await websocket.send('{"eof" : 1}')
            print(await websocket.recv())

async def main():
    global loop, audio_queue

    loop = asyncio.get_running_loop()
    audio_queue = asyncio.Queue()  # For raw audio data

    # Run transcription
    await transcribe_audio()

if __name__ == '__main__':
    asyncio.run(main())
