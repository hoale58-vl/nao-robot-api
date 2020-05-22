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
face_detect = FaceDetect(gpuid=0)

from retinaFace.src.face_recognition import RecognitionModel
agegender = RecognitionModel(gpuid=0)
import logging
logging.basicConfig(level=logging.DEBUG)

clients = []

gstream = NaoGstreamer(face_detect, agegender)
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
			logging.error("File: {} - Line: {} - Error: {}".format(fname, exc_tb.tb_lineno, str(e)))

	def handleConnected(self):
		try:
			logging.info(str(self.address) + ' Connected')
			self.clientMeta = {}
			self.clientMeta['socket'] = self
			clients.append(self.clientMeta)
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			logging.error("File: {} - Line: {} - Error: {}".format(fname, exc_tb.tb_lineno, str(e)))

	def handleClose(self):
		logging.info(str(self.address) + ' Disconnected')
		clients.remove(self.clientMeta)
		if (len(clients) == 0):
			gstream.stopPlaying()
			gstream.websocket_client = None

server = SimpleWebSocketServer('', Const.ROBOT_CONTROL_WEBSOCKET_PORT, NaoControlWebSocket)
server.serveforever()