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
# from retinaFace.src.face_recognition import RecognitionModel, test_age_gender
face_detect = FaceDetect(gpuid=0)
# agegender = RecognitionModel(gpuid=0)
# test_age_gender()

clients = []

gstream = NaoGstreamer(face_detect)
thread.start_new_thread(gstream.startPlaying, ())

class NaoControlWebSocket(WebSocket):
	def handleMessage(self):
		try:
			if self.data == 'alive':
				gstream.running = True
				gstream.websocket_client = self
			elif self.data == 'stop':
				gstream.running = False
				gstream.websocket_client = None
				face_detect.disconnect()
			elif re.match('([^:]+)::::([^:]+)::::([^:]+)', self.data):
				for client in clients:
					if client['socket'] != self:
						client['socket'].sendMessage(self.data)
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(fname, exc_tb.tb_lineno, e)

	def handleConnected(self):
		try:
			print(str(self.address) + ' Connected')
			self.clientMeta = {}
			self.clientMeta['socket'] = self
			clients.append(self.clientMeta)
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(fname, exc_tb.tb_lineno, e)

	def handleClose(self):
		print(str(self.address) + ' Disconnected')
		clients.remove(self.clientMeta)
		if (len(clients) == 0):
			gstream.stopPlaying()
			gstream.websocket_client = None

server = SimpleWebSocketServer('', Const.ROBOT_CONTROL_WEBSOCKET_PORT, NaoControlWebSocket)
server.serveforever()