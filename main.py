#Copyright Anis AYARI (Defend Intelligence)
#N'oubliez pas de citer le projet d'origine ! Merci !

# IMPORT VARIABLE ENV
import sounddevice as sd
import openai
import pyaudio
import wave
from dotenv import load_dotenv , find_dotenv
from elevenlabs import generate, play, set_api_key, save, stream
from pydub import AudioSegment
from pydub.playback import play
import pvporcupine
from pvrecorder import PvRecorder
import os
import random


load_dotenv(find_dotenv())

porcupine = pvporcupine.create(
  access_key=os.getenv('ACCES_KEY_PORCUPINE'),
  keyword_paths=[os.getenv('KEYWORD_PATH_PORCUPINE')],
    model_path=os.getenv('MODEL_PATH_PROCUPINE')
)
set_api_key(os.getenv('ELEVENLAB_API_KEY'))
openai.api_key = os.getenv('OPENAI_API_KEY')
openai.organization = os.getenv('OPENAI_ORG')
sd.query_devices()
#FUNCTION WAKE_WORD


# FUNCTION REC MIC

#FUNCTION SPEECH TO TEXT (whisper)
def record_audio(filename, duration=5):
    #ADD DETECTOR SILENT TO CUT AUDIO AUTOMATICALLY
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024

    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    print("Recording...")

    frames = []

    for _ in range(0, int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Finished recording")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

def transcribe_audio(filename):
        with open(filename, "rb") as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
            return transcript["text"]

#FUNCTION TEXT TO SPEECH (ELEVEN LABS)
def get_generate_audio(text, name_audio):
    audio = generate(
        text=text,
        voice=os.getenv("ELEVENLAB_VOICE_ID"),
        model="eleven_multilingual_v1",
        stream=True
    )
    stream(audio)

#GET REPONSE GPT
def generate_script_gpt(text,messages_prev):
    if len(messages_prev) == 0:
        messages_prev = [
            {"role": "system", "content": """Tu es l'assistant IA de Defend Intelligence,
            un streamer et youtuber sur Twitch. Tu dois répondre de manière drôle et atypique, à ce que Defend Intelligence te dis.
            Dans la mesure du possible tu donneras des réponses assez courtes. """},

            {"role": "user", "content": f"""{text}"""}]
    else:
        messages_prev.append({"role": "user", "content": f"""{text}"""})
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", max_tokens=150, temperature=1,
                                            messages=messages_prev)
    res = response['choices'][0]['message']['content']
    messages_prev.append({"role": "assistant", "content": f"""{res}"""})
    if len(messages_prev)> 10:
        messages_prev = messages_prev[:-10]
    return res,messages_prev

def main(messages_prev):
    audio_filename = "recorded_audio.wav"
    print('1/4 RECORD AUDIO')
    record_audio(audio_filename)
    print('2/4 SPEECH TO TEXT')
    transcription = transcribe_audio(audio_filename)
    print(transcription)
    print('3/4 GENERATE SCRIPT GPT')
    res, messages_prev = generate_script_gpt(transcription,messages_prev)
    print('4/4 TEXT TO SPEECH')
    get_generate_audio(res,'output_elevenlabs')
    print("4/5 READING AUDIO GENERATED")
    return messages_prev

def get_random_mp3_file(folder_path):
    mp3_files = [file for file in os.listdir(folder_path) if file.endswith(".mp3")]
    if not mp3_files:
        return None
    random_file = random.choice(mp3_files)
    return os.path.join(folder_path, random_file)

if __name__ == "__main__":
    messages_prev = []
    print('LISTENING...')
    recorder = PvRecorder(
        frame_length=porcupine.frame_length)
    recorder.start()

    print('Listening ... (press Ctrl+C to exit)')
    while True:
        pcm = recorder.read()
        keyword_index = porcupine.process(pcm)
        print(keyword_index)
        if keyword_index==0:
            print('DETECTED !!!')
            song = AudioSegment.from_file(get_random_mp3_file('voix_intro'))
            play(song)
            messages_prev = main(messages_prev)

#ADD TWITCH LIVE