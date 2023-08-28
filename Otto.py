import os
import struct
import wave
import pvporcupine
from pvrecorder import PvRecorder
import pyttsx3
import threading
from oswaveplayer import *
import speech_recognition as sr
import time
from datetime import datetime
import subprocess
import openai

openai.api_key =  "9s9O__Df67cCE0DI3X3vWqoL1MxOvdorsPCqraaKUDs"
openai.api_base = "https://chimeragpt.adventblocks.cc/api/v1"



def get_headers():
    return {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}

def save_to_file(content):
    with open("output.txt", "a") as file:
        file.write(content)






r = sr.Recognizer()
print("Starting Otto...")
voice = sr.AudioFile('voice.wav')
with voice as source:
    audio = r.record(source)
    command = r.recognize_google(audio)
    print("Otto version: 1.0.0")

def play_voice():
    engine.runAndWait()

engine = pyttsx3.init()

access_key = "I6tODUeq7aHSiLYui53UpoIUNIE/DdtKuVOTRE0U47MkUoSIvtlqEQ=="
keyword_paths = ["/home/pi/hey-Otto_en_raspberry-pi_v2_2_0.ppn"]
sensitivities = [0.5] * len(keyword_paths)

try:
    porcupine = pvporcupine.create(
        access_key=access_key,
        keyword_paths=keyword_paths,
        sensitivities=sensitivities
    )

    keywords = [os.path.basename(x).replace('.ppn', '').split('_')[0] for x in keyword_paths]

    print('Porcupine version: %s' % porcupine.version)

    recorder = PvRecorder(frame_length=porcupine.frame_length, device_index=-1)
    recorder.start()

    wav_file = None
    output_path = None

    if output_path is not None:
        wav_file = wave.open(output_path, "w")
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)

    print('Listening ... (press Ctrl+C to exit)')

    while True:
        pcm = recorder.read()
        result = porcupine.process(pcm)

        if wav_file is not None:
            wav_file.writeframes(struct.pack("h" * len(pcm), *pcm))

        if result >= 0:
            print('[%s] Detected %s' % (str(datetime.now()), keywords[result]))
            yourSound = playwave("Wakewordnoise.wav")
            engine.say(' . ')
            threading.Thread(target=play_voice).start()

            import pyaudio
            def record_audio(filename, duration=5, sample_rate=44100, chunk_size=1024, format_=pyaudio.paInt16, channels=2):
                audio = pyaudio.PyAudio()
                stream = audio.open(format=format_, channels=channels, rate=sample_rate, input=True, frames_per_buffer=chunk_size)
                print("Recording...")
                frames = []
                for i in range(0, int(sample_rate / chunk_size * duration)):
                    data = stream.read(chunk_size)
                    frames.append(data)
                print("Recording finished.")
                stream.stop_stream()
                stream.close()
                audio.terminate()
                wave_file = wave.open(filename, "wb")
                wave_file.setnchannels(channels)
                wave_file.setsampwidth(audio.get_sample_size(format_))
                wave_file.setframerate(sample_rate)
                wave_file.writeframes(b''.join(frames))
                wave_file.close()

            output_filename = "voice.mp3"
            recording_duration = 5
            record_audio(output_filename, duration=recording_duration)
            voice = sr.AudioFile('voice.mp3')
            with voice as source:
                audio = r.record(source)
            command = r.recognize_google(audio)

            past_responses = []
            try:
                with open("past_responses.txt", "r") as file:
                    past_responses = [line.strip() for line in file.readlines()]
            except FileNotFoundError:
                pass
            
            with open('past_conversations.txt', 'r') as file:
                past_conversations = file.read()

            with open('otto_commands.txt', 'r') as file:
                commands = file.read()

            with open('people_info.txt', 'r') as file:
                people_info = file.read()

            current_time = datetime.now()

            file_content = ""
            user_messages = [
                {"role": "system", "content": f"You are a robot called Otto. Your creator is a boy called Ezra. We live in a town in Illinois called Geneva. You were made in a makerspace called FOX.BUILD. Don't make up anything I did'nt tell you unless I ask.  past conversations: {past_conversations}  information about people: {people_info}  commands: {commands}" },
                {"role": "user", "content": command}
            ]


            response = openai.ChatCompletion.create(
                model='gpt-3.5-turbo-16k',
                messages=user_messages,
                stream=True
            )

            ai_response = ""
            for chunk in response:
                ai_response += chunk.choices[0].delta.get("content", "")
                file_content += f"User: {command}\nAI: {ai_response}\n\n"
                save_to_file(file_content)
            with open('past_conversations.txt', 'a') as file:
                file.write(f"Human: {command}\nAI: {ai_response}\n\n")


            print("Otto:", ai_response)

            engine.say(ai_response)
            threading.Thread(target=play_voice).start()



except KeyboardInterrupt:
   print('Stopping ...')
finally:
    recorder.delete()
    porcupine.delete()
    if wav_file is not None:
        wav_file.close()
