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

class StreamAudio(WebSocket):
	def sttGoogleApi(self, audio):
		try:
			data = self.recognizer.recognize_google_cloud(audio, credentials_json=Const.GOOGLE_CLOUD_SPEECH_CREDENTIALS, language='vi-VI')
			data = data.lower().strip()
			print('[User] ' + data)
		except sr.sr.UnknownValueError:
			data = "i can't hear!"
			print('[Bot] ' + data)
			return
		except sr.sr.RequestError as e:
			data = "too noisy"
			print("Could not request results from Google Speech Recognition service; {0}".format(e))
			sendCommand("speak::::vi::::event/gstt_error.mp3")
			return
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(fname, exc_tb.tb_lineno, e)
			return

		try:
			botRes = askBot(data)
			print('[Bot] ' + botRes)
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(fname, exc_tb.tb_lineno, e)

	def timerStopListening(self):
		try:
			while self.connected:
				if self.recognizer.start_speaking == True and self.last_message_at:
					if self.last_message_at + Const.STOP_LISTENING_TIMEOUT < time.time():
						self.recognizer.start_speaking = False
						self.recognizer.stop_speaking = False
						self.recognizer.frames = collections.deque()
						print('Stop Speaking - Timeout listening')
				time.sleep(1)
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(fname, exc_tb.tb_lineno, e)

	def handleMessage(self):
		try:
			for client in clients:
				if client == self.id:
					# Timeout - Did receive data from client
					self.last_message_at = time.time()
					audio = self.recognizer.listen_from_bytes(bytes(self.data), 7)
					if self.recognizer.stop_speaking:
						print('Stop Speaking - By voice')
					if audio is not None and type(audio) is not bool:
						thread.start_new_thread( self.sttGoogleApi, (audio, ) )
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			log.errorLog(fname, exc_tb.tb_lineno, e)

	def handleConnected(self):
		try:
			self.connected = True
			print(str(self.address) + ' connected')
			id = 1
			while (True):
				if id in clients:
					id+=1
				else:
					self.id = id
					clients.append(self.id)
					break
			self.botApi = BotApi(self.id)

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
			print(fname, exc_tb.tb_lineno, e)

	def handleClose(self):
		self.connected = False
		clients.remove(self.id)
		print(str(self.address) + ' closed')

server = SimpleWebSocketServer('', Const.ROBOT_CHATBOT_WEBSOCKET_PORT, StreamAudio)
server.serveforever()