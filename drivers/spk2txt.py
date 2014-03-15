#!/usr/bin/env python

import urllib2
import tempfile 
import pyaudio
import wave
import json
import time
import plumbum
import threading
from plumbum.cmd import flac

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
        print "recording ..."
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

        flac['-f', '-o', outfn+'.flac', outfn+'.wav']()
        f = open(outfn+'.flac', 'rb')
        flacData = f.read()
        f.close()

        print 'Sending to google.'
        url = 'https://www.google.com/speech-api/v1/recognize?xjerr=1&pfilter=1&client=chromium&lang=%s&maxresults=1' %self.lang
        header = {'Content-Type' : 'audio/x-flac; rate=16000'}
        req = urllib2.Request(url, flacData, header)
        conn = urllib2.urlopen(req)
        data = json.loads(conn.read())
        ut = data['hypotheses']
        for i in ut:
            self.text += i['utterance']


    def __del__self(self):
        self.p.terminate()

