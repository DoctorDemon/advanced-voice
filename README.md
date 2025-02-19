<p align="center">
  <img src="https://i.imagicx.de/i/Gh16dwczvrYO.png" width="600">
</p>

This project is a voice assistant that listens to user speech, transcribes it, and generates AI responses using the Hugging Face API. The assistant can speak the AI responses back to the user but like OpenAI's advanced voice mode, you can interupt the assistant by just speaking while it speaks. <br>
The system uses huggingface's inference API to use specific models (which you can customize) and it works well on the free tier, consuming <1¢ developing it. (NousResearch/Hermes-3-Llama-3.1-8B) <br>
The system also uses Vosk for the speech to text conversion. You can setup your own, completely free huggingface space to do this with almost no latency.

## Features

- Natural interruption by speaking over the assistant.
- Real-time speech recognition using Vosk. ([learn how to setup a Vosk API server for free](https://github.com/DoctorDemon/Vosk-API-Huggingface))
- AI response generation using Hugging Face's Inference API. (You can customize it to use a provider of your choice)
- Text-to-speech conversion using Edge TTS, streaming the response to ensure ultra fast feedback for the natural conversation flow.

## Requirements

- [A Vosk API server](https://github.com/DoctorDemon/Vosk-API-Huggingface)
- A huggingface token
- Python 3.7+
- Required Python packages:
  - `playsound`
  - `pyaudio`
  - `wave`
  - `pydub`
  - `edge_tts`
  - `sounddevice`
  - `websockets`
  - `huggingface_hub`

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/DoctorDemon/advanced-voice.git
    cd advanced-voice
    ```

2. Install the required packages:
    ```sh
    pip install playsound pyaudio wave pydub edge_tts sounddevice websockets huggingface_hub
    ```

3. Obtain an API key from Hugging Face and replace `{YOUR HUGGINGFACE API TOKEN}` in `assistant.py` with your actual API key.

## Usage

1. Run the assistant:
    ```sh
    python assistant.py
    ```

2. The assistant will start listening for your speech. Speak into your microphone, and the assistant will transcribe your speech, generate an AI response, and speak the response back to you. <br>
You can interrupt it to test the interruption feature, the assistant should stop.

## Files

- `assistant.py`: Main script for the voice assistant.
- `speaker.py`: Contains functions for text-to-speech conversion streaming from edge TTS (free) and playback control.

## Customization

- Modify the `conversation_history` in `assistant.py` to change the assistant's personality and style.
- Adjust the `CHUNK_SIZE` in `speaker.py` to change the audio chunk size for playback.

## Troubleshooting

- Ensure your microphone is properly configured and working.
  you can change the input device the program is using by changing the device ID in the RawInputStream initialisation like this:
  ```python
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback, device=1)
    ```
  where device ID is your systems audio device ID.
  
- Check your internet connection as the assistant relies on online services.
- If you encounter any issues, refer to the error messages for debugging.
- If there are any more problems, feel free to open an issue!

### You may use these code snippets freely in your projects!

*Built by developers, for developers! ❤️*
