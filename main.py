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
import socket
import signal


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

def init_twitch():
    server = 'irc.chat.twitch.tv'
    port = 6667
    nickname = 'defendintelligence'

    token = os.getenv('TOKEN_TWITCH')
    channel = os.getenv('USERNAME_TWITCH')

    sock = socket.socket()
    sock.connect((server, port))

    sock.send(f"PASS {token}\n".encode('utf-8'))
    sock.send(f"NICK {nickname}\n".encode('utf-8'))
    sock.send(f"JOIN #{channel}\n".encode('utf-8'))
    return sock

def detect_twitch_bot_command(sock):
    resp = sock.recv(2048).decode('utf-8')
    print(resp)
    if resp.startswith('PING'):
        sock.send("PONG :tmi.twitch.tv\n".encode('utf-8'))
    elif 'PRIVMSG' in resp and 'wizebot' not in resp and '!yomanu' in resp:
        user = resp.split('PRIVMSG')[0].split(':')[1].split('!')[0]
        msg = resp.split('PRIVMSG')[1].split(':')
        res = msg[1].replace('!yomanu','')
        return f"L'utilisateur {user} te dit {res}"
    else:
        return ''


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
            Dans la mesure du possible tu donneras des réponses assez courtes. 
            Si un utilisateur te dis quelque chose tu devras lui répondre en citant son pseudo en premier, et en reformulant ce qu'il te demande"""},

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

def main(messages_prev,kind,**kwargs):
    if kind == 'vocal':
        audio_filename = "recorded_audio.wav"
        print('1/4 RECORD AUDIO')
        record_audio(audio_filename)
        print('2/4 SPEECH TO TEXT')
        transcription = transcribe_audio(audio_filename)
        print(transcription)
        print('3/4 GENERATE SCRIPT GPT')
    if kind == 'chat':
        transcription = kwargs.get('text_chat')
        messages_prev = []
    res, messages_prev = generate_script_gpt(transcription,messages_prev)
    print('4/4 TEXT TO SPEECH')
    get_generate_audio(res,'output_elevenlabs')
    print("4/5 READING AUDIO GENERATED")
    if kind == 'vocal':
        return messages_prev

def get_random_mp3_file(folder_path):
    mp3_files = [file for file in os.listdir(folder_path) if file.endswith(".mp3")]
    if not mp3_files:
        return None
    random_file = random.choice(mp3_files)
    return os.path.join(folder_path, random_file)

def signal_handler(signal, frame):
    print("\nProgramme terminé.")
    sock.close()
    recorder.stop()
    exit(0)

if __name__ == "__main__":
    messages_prev = []
    print('LISTENING...')
    recorder = PvRecorder(
        frame_length=porcupine.frame_length)
    recorder.start()
    sock = init_twitch()
    print('Listening ... (press Ctrl+C to exit)')
    timer=300
    message = ''
    signal.signal(signal.SIGINT, signal_handler)

    while True:
        if timer > 0:
            timer -= 1
        pcm = recorder.read()
        keyword_index = porcupine.process(pcm)
        print(keyword_index)
        print('TIMER:',timer)
        if timer == 0:
            message = detect_twitch_bot_command(sock)
            print(f'MESSAGE SENT TO BOT : {message}')
        if keyword_index == 0 or (len(message) > 0 and timer ==0):
            print('DETECTED !!!')
            if keyword_index ==0:
                song = AudioSegment.from_file(get_random_mp3_file('voix_intro'))
                play(song)
                messages_prev = main(messages_prev, kind='vocal')
            elif len(message) > 0:
                main(messages_prev, kind='chat',text_chat=message)
                timer = 300
                keyword_index = -1

#ADD TWITCH LIVE