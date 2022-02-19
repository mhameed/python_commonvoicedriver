#!/usr/bin/env python3
import base64
import os
import sounddevice as sd
import soundfile as sf
import tempfile
import threading
from plumbum.cmd import sox

class AudioHelper():

    def __init__(self, filename = tempfile.mktemp('.wav'), normalize=True):
        self._stop = threading.Event()
        self._thread = None
        self._action = ''
        self.filename = filename
        self.normalize = normalize

    @property
    def action(self):
        return self._action

    def _do_play(self):
        self._action = 'playing'
        with sf.SoundFile(self.filename, 'r') as wf:
            with sd.OutputStream(samplerate=wf.samplerate, channels=wf.channels) as stream:
                while not self._stop.isSet() and wf.tell() != wf.frames:
                    stream.write(wf.read(stream.write_available, dtype='float32'))
        self._action = ''

    def _do_record(self):
        self._action = 'recording'
        mySampleRate = 44100
        fname = tempfile.mktemp('.wav')
        with sd.InputStream(samplerate=mySampleRate, dtype='float32', channels=1) as stream:
            with sf.SoundFile(fname, 'w', samplerate=mySampleRate, channels=1) as wf:
                while not self._stop.isSet():
                    wf.write(stream.read(1024)[0])
        if self.normalize:
            sox_cmd = sox[fname, self.filename, 'norm', '-0.1']()
            os.remove(fname)
        else:
            os.rename(fname, self.filename)
        self._action = ''

    def _do_action(self, action):
        if self._thread and self._thread.is_alive():
            raise ValueError("Can only perform one action at any given time.")
        self._stop.clear()
        self._thread = threading.Thread(target=action)
        self._thread.start()

    def play(self):
        self._do_action(self._do_play)

    def record(self):
        self._do_action(self._do_record)

    def stop(self):
        self._stop.set()

    @property
    def is_recording(self):
        return self._action == 'recording'

    @property
    def is_playing(self):
        return self._action == 'playing'

    def base64(self):
        if self._thread and self._thread.is_alive():
            raise ValueError("file is active.")
        with open(self.filename, 'rb') as f:
            data = base64.standard_b64encode(f.read()).decode('ascii')
        return data
