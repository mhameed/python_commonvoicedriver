import os
import shutil
import tempfile
import threading
import Xlib
import Xlib.X
import Xlib.XK
import Xlib.display
from driver import KBDDriver

import sys
import trio
import httpx
from plumbum.cmd import xte, spd_say, xsel, echo, notify_send
from utils import Spk2Txt
from .dictationcorrection import DictationCorrection
import threading
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

_say = spd_say['-r', '100', '-P', 'important', '-e']

def say(text):
    f = open('/tmp/speech.txt', 'w')
    f.write(text)
    f.close()
    (_say < '/tmp/speech.txt')()

async def child1(win, nursery):
    win.show_all()

class Driver(KBDDriver):
    def __init__(self, api_url, device, *args, **kwargs):
        super(Driver, self).__init__(device=device, *args, **kwargs)
        self.api_url = api_url
        self.display = Xlib.display.Display()
        self.m = Spk2Txt(f"{self.api_url}/transcribe")
        self.dictationcorrection = DictationCorrection(self.on_abort_callback, self.on_play_callback, self.on_submit_callback)
        self.dictationcorrection.connect("destroy", Gtk.main_quit)

    def on_abort_callback(self, widget):
        parent = widget.get_toplevel()
        parent.set_visible(False)

    def on_play_callback(self, widget):
        self.m.audio.play()

    def on_submit_callback(self, widget):
        parent = widget.get_toplevel()
        parent.set_visible(False)
        text = self.dictationcorrection.entry.get_text()
        self.dictationcorrection.entry.set_text("")
        fname = tempfile.mktemp('.wav')
        shutil.copy2(self.m.audio.filename, fname)
        thread = threading.Thread(target=self.post, args=[f'{self.api_url}/correct', fname, text], kwargs={'logger':self.logger})
        thread.start()

    def post(self, url, filename, text, *args, **kwargs):
        logger = kwargs.get('logger', None)
        headers = {'Content-Type': 'Audio/Wav','sentence': text}
        with httpx.Client() as client:
            with open(filename, 'rb') as f:
                resp = client.post(url, headers=headers, content=f)
            data = resp.json()
            if logger:
                logger.debug('data: ' %data)

    async def kbd_btn272(self, **kwargs):
        value = kwargs.get('evalue')
        self.logger.debug('left button val=%d' % value)
        if value:
            self.m.start()
            self.logger.debug('started recording')
        else:
            await self.m.stop()
            self.logger.debug('stopped recording')
            say(self.m.text)
            self.dictationcorrection.entry.set_text(self.m.text)
            self.logger.debug(f'text: %s' %self.m.text)

    async def kbd_btn273(self, **kwargs):
        value = kwargs.get('evalue')
        self.logger.debug('right button val=%d' % value)
        if value:
            #xte['str %s ' % self.m.text]()
            (xsel['-i', '-b'] < '/tmp/speech.txt' )()
            xte['keydown Control_L', 'key v', 'keyup Control_L']()

    async def kbd_btn274(self, **kwargs):
        value = kwargs.get('evalue')
        self.logger.debug('middle button val=%d' % value)
        if value:
            async with trio.open_nursery() as nursery:
                dc = self.dictationcorrection
                nursery.start_soon(child1, dc, nursery)
