#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from gstreamerOpencv import NaoGstreamer
import _thread as thread
import sys
import os
import time
import re
import Const
from retinaFace.src.face_detect import FaceDetect
face_detect = FaceDetect(gpuid=-1)
clients = []

class NaoControlWebSocket(WebSocket):
	def handleMessage(self):
		try:
			if data == 'alive':
				self.gstream = NaoGstreamer(self, face_detect)
				thread.start_new_thread(self.gstream.startPlaying, ())
			elif data == 'stop':
				self.gstream.stopPlaying()
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(fname, exc_tb.tb_lineno, e)

	def handleConnected(self):
		try:
			print(str(self.address) + ' Connected')
			self.clientMeta = {}
			self.clientMeta['socket'] = self
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(fname, exc_tb.tb_lineno, e)

	def handleClose(self):
		print(str(self.address) + ' Disconnected')
		clients.remove(self.clientMeta)
		self.gstream.stopPlaying()

server = SimpleWebSocketServer('', Const.ROBOT_CONTROL_WEBSOCKET_PORT, NaoControlWebSocket)
server.serveforever()