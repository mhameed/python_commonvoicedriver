#!/usr/bin/env python3
import base64
import requests
import tempfile 
import pyaudio
import wave
import json
import time
import threading

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

class spk2txt(threading.Thread):

    def __init__(self, lang='en-GB', *args, **kwargs):
        super(spk2txt, self).__init__(*args, **kwargs)
        self.p = pyaudio.PyAudio()
        self.frames = []
        self._stop = threading.Event()
        self.text = ""
        self.lang = lang

    def stop(self):
        self._stop.set()

    def run(self):
        self.text = ""
        outfn = OUTPUT_FILENAME = tempfile.mktemp()
        stream = self.p.open(format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK)
        print("recording ...")
        while not self._stop.isSet():
            data = stream.read(CHUNK)
            self.frames.append(data)
            time.sleep(0)

        print("* done recording")

        stream.stop_stream()
        stream.close()

        wf = wave.open(outfn+".wav", 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()

        f = open(outfn+'.wav', 'rb')
        wavData = base64.standard_b64encode(f.read()).decode('ascii')
        f.close()
        data = {'audio': wavData}
        print('Sending to api.')
        url = 'https://api.hameed.info/mesar/speech/transcriber/'
        header = {'Content-Type' : 'Application/json'}
        r = requests.post(url, data=json.dumps(data), headers=header)
        data = r.json()
        ut = data['transcripts']
        for i in ut:
            self.text += i['utterance']


    def __del__self(self):
        self.p.terminate()

