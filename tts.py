# Import necessary libraries
import requests  # Used for making HTTP requests
import json  # Used for working with JSON data

import pydub
import pyaudio
import wave

import time
import os
# Define constants for the script
CHUNK_SIZE = 1024  # Size of chunks to read/write at a time
XI_API_KEY = 'Your API key for authentication'  # Your API key for authentication
VOICE_ID = "ID of the voice model to use"  # ID of the voice model to use
TEXT_TO_SPEAK = "hello i am elon musk, nice to meet you"  # Text you want to convert to speech
OUTPUT_PATH = "output.wav"  # Path to save the output audio file

# Construct the URL for the Text-to-Speech API request
tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream"

# Set up headers for the API request, including the API key for authentication

# Define a function to play the WAV audio file
p = pyaudio.PyAudio()
# Open a stream on the PyAudio object
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                output=True)



def play_wav(file_path):
    # Open the WAV file
    wf = wave.open(file_path, 'rb')

    # Play the audio by writing the data to the stream

    data = wf.readframes(CHUNK_SIZE)
    while data:
        stream.write(data)
        data = wf.readframes(CHUNK_SIZE)

    #delet the file
    os.remove(file_path)


import threading
from queue import Queue
audio_files_queue = Queue()
def play_audio_thread():
    while True:
        audio = audio_files_queue.get()
        if audio == None:
            break
        play_wav(audio)

def get_wav(text):
    if text == None:
        return None
    # Set up headers for the API request, including the API key for authentication
    headers = {
        "Accept": "application/json",
        "xi-api-key": XI_API_KEY
    }

    # Set up the data payload for the API request, including the text and voice settings
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8,
            "style": 0.0,
            "use_speaker_boost": True
        }
    }

    # Make the POST request to the TTS API with headers and data, enabling streaming response
    response = requests.post(tts_url, headers=headers, json=data, stream=True)

    file_path = 'cache/'+str(time.time())+'.mp3'

    # Check if the request was successful
    if response.ok:
        # Open the output file in write-binary mode
        with open(file_path, "wb") as f:
            # Read the response in chunks and write to the file
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                f.write(chunk)
        # Inform the user of success
        print("Audio stream saved successfully.")
    else:
        # Print the error message if the request was not successful
        print(response.text)

    #convert mp3 to wav
    sound = pydub.AudioSegment.from_mp3(file_path)
    sound.export(file_path.replace('.mp3','.wav'), format="wav")

    os.remove(file_path)

    file_path = file_path.replace('.mp3','.wav')

    return file_path

import wave
import contextlib

def get_wav_duration(wav_path):
    """ 读取WAV文件的播放时长 """
    with contextlib.closing(wave.open(wav_path, 'rb')) as file:
        # 获取音频的帧数
        frames = file.getnframes()
        # 获取音频的帧率（每秒帧数）
        rate = file.getframerate()
        # 计算播放时长
        duration = frames / float(rate)
        return duration

def play_audio(text):

    sentences = []
    sentence = ''
    for ch in text:
        sentence += ch
        if "." in ch or "？" in ch or "！" in ch or "。" in ch or "；" in ch or "?" in ch or "!" in ch or ";" in ch:
            sentences += [sentence]
            sentence = ''
    sentences += [None]

    play_thread = threading.Thread(target=play_audio_thread).start()

    for sentence in sentences:
        audio = get_wav(sentence)

        if audio != None:
            duration = get_wav_duration(audio)
            # print(duration)
        
        audio_files_queue.put(audio)

    time.sleep(duration+0.3)
    # play_thread.join()
    



if __name__ == "__main__":
    play_audio('hello , i am elon musk, nice to meet you. how are you today?i am fine, thank you.')