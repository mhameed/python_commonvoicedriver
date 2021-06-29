#!/usr/bin/env python3
import trio
import httpx
import tempfile 
import json
import time
import threading
import logging
from audiohelper import AudioHelper

class spk2txt(object):

    def __init__(self, url, lang='en-GB', *args, **kwargs):
        super(spk2txt, self).__init__(*args, **kwargs)
        self.logger = logging.getLogger('motion.spk2txt')
        self.text = ""
        self.lang = lang
        self.audio = AudioHelper()
        self.url = url
        self.logger.debug('initialised')

    def start(self):
        self.logger.info('start')
        self.audio.record()

    async def stop(self):
        self.audio.stop()
        self.text = ""
        while self.audio.action != '':
            await trio.sleep(0.1)
        payload = {'audio': self.audio.base64()}
        header = {'Content-Type' : 'Application/json'}
        async with httpx.AsyncClient() as client:
            resp = await client.post(self.url, json=payload, headers=header)
            data = resp.json()
        ut = data['transcripts']
        for i in ut:
            self.text += i['utterance']
        self.logger.info('stop done')
