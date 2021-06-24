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

class spk2txt(object):

    def __init__(self, lang='en-GB', *args, **kwargs):
        super(spk2txt, self).__init__(*args, **kwargs)
        self.p = pyaudio.PyAudio()
        self.frames = []
        self._stop = threading.Event()
        self.text = ""
        self.lang = lang
        self.t = None

    def start(self):
        self.frames = []
        self._stop.clear()
        self.t = threading.Thread(target=self.run)
        self.t.start()

    def stop(self):
        self._stop.set()
        self.t.join()

    def run(self):
        self.text = ""
        outfn = OUTPUT_FILENAME = tempfile.mktemp()
        stream = self.p.open(format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK)
        while not self._stop.isSet():
            data = stream.read(CHUNK)
            self.frames.append(data)
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
        url = 'https://api.hameed.info/mesar/speech/transcriber/'
        header = {'Content-Type' : 'Application/json'}
        r = requests.post(url, data=json.dumps(data), headers=header)
        data = r.json()
        ut = data['transcripts']
        for i in ut:
            self.text += i['utterance']


    def __del__self(self):
        self.p.terminate()

