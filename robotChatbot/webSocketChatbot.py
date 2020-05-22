#! /usr/bin/env python
# encoding=utf8
import sys

from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import os
import time
import _thread as thread
import custom_speech_recog as sr
import Const
import collections
from utils import BotApi
from websocket import create_connection
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import json
import logging
logging.getLogger().setLevel(logging.DEBUG)

lang_code = {
	"en": "en-US",
	"vi": "vi-VN",
}

def getLangFromConfig():
	configFile = os.path.join(Const.configPath, "config.json")
	with open(configFile, "r+") as jsonFile:
		data = json.load(jsonFile)
		logging.info("Get lang from config: {}".format(data['lang']))
		return data["lang"]

class StreamAudio(WebSocket):
	def on_modified(self, event):
		self.configLang = lang_code[getLangFromConfig()]

	def sttGoogleApi(self, audio):
		try:
			data = self.recognizer.recognize_google_cloud(audio, credentials_json=Const.GOOGLE_CLOUD_SPEECH_CREDENTIALS, language=self.configLang)
			data = data.lower().strip()
			logging.debug('[User] ' + data)
		except sr.sr.UnknownValueError as e:
			data = "i can't hear!"
			logging.debug('[Bot] ' + data + " - Error:" + str(e))
			return
		except sr.sr.RequestError as e:
			data = "too noisy"
			logging.debug("Could not request results from Google Speech Recognition service; {0}".format(e))
			# wsControl = create_connection(Const.WEBSOCKET_CONTROL_URL)
			# wsControl.send("speak::::vi::::event/gstt_error.mp3")
			# wsControl.close()
			return
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			logging.error("File: {} - Line: {} - Error: {}".format(fname, exc_tb.tb_lineno, str(e)))
			return

		try:
			botRes = self.botApi.askBot(data)
			if botRes is not None:
				logging.debug('[Bot] ' + botRes)
			else:
				logging.debug('[Bot] None')
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			logging.error("File: {} - Line: {} - Error: {}".format(fname, exc_tb.tb_lineno, str(e)))

	def timerStopListening(self):
		try:
			while self.connected:
				if self.recognizer.start_speaking == True and self.last_message_at:
					if self.last_message_at + Const.STOP_LISTENING_TIMEOUT < time.time():
						self.recognizer.start_speaking = False
						self.recognizer.stop_speaking = False
						self.recognizer.frames = collections.deque()
						logging.debug('Stop Speaking - Timeout listening')
				time.sleep(1)
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			logging.error("File: {} - Line: {} - Error: {}".format(fname, exc_tb.tb_lineno, str(e)))

	def handleMessage(self):
		try:
			# Timeout - Did receive data from client
			self.last_message_at = time.time()
			audio = self.recognizer.listen_from_bytes(bytes(self.data), 15)
			if self.recognizer.stop_speaking:
				logging.debug('Stop Speaking - By voice')
			if audio is not None and type(audio) is not bool:
				thread.start_new_thread( self.sttGoogleApi, (audio, ) )
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			logging.error("File: {} - Line: {} - Error: {}".format(fname, exc_tb.tb_lineno, str(e)))

	def handleConnected(self):
		try:
			self.configLang = lang_code[getLangFromConfig()]
			event_handler = PatternMatchingEventHandler(patterns=["*.json"],
									ignore_patterns=[],
									ignore_directories=True)
			event_handler.on_modified = self.on_modified
			self.observer = Observer()
			self.observer.schedule(event_handler, path=Const.configPath, recursive=False)
			self.observer.start()

			self.connected = True
			logging.info(str(self.address) + ' connected')
			self.botApi = BotApi(Const.chatbot_id)

			self.recognizer = sr.CustomSpeechRecognition()
			self.recognizer.pause_threshold = Const.pause_threshold # length of silence (in seconds) that will register as the end of a phrase
			self.recognizer.dynamic_energy_threshold = True

			self.recognizer.custom_init(Const.CHUNK, Const.RATE)
			self.recognizer.energy_threshold = Const.energy_threshold
			self.recognizer.operation_timeout = Const.GOOGLE_CLOUD_TIME_OUT

			self.action_buf_len = 0
			self.action_buf = []

			thread.start_new_thread(self.timerStopListening,())

		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			logging.error("File: {} - Line: {} - Error: {}".format(fname, exc_tb.tb_lineno, str(e)))

	def handleClose(self):
		self.connected = False
		logging.debug(str(self.address) + ' closed')
		self.observer.stop()
		self.observer.join()

server = SimpleWebSocketServer('', Const.ROBOT_CHATBOT_WEBSOCKET_PORT, StreamAudio)
server.serveforever()
