#! /usr/bin/env python
# encoding=utf8
import sys
from gi.repository import Gst
import Const
import _thread as thread
import os
import time
from utils import gst_to_opencv

class NaoGstreamer(object):
	def __init__(self,  websocket_client, face_detect=None):
		super(NaoGstreamer, self).__init__()
		Gst.init(None)
		self.websocket_client = websocket_client
		CLI = ("udpsrc port={} ! application/x-rtp, encoding-name=JPEG,payload=26 ! rtpjpegdepay ! jpegdec ! appsink name=sink").format(Const.GSPORT)
		self.pipeline = Gst.parse_launch(CLI)
		self.sink = self.setupSink()
		self.sink.connect("new-sample", self.new_buffer, self.sink)

		self.image_arr = None
		self.bus = None
		self.face_detect = face_detect

		self.faceDetected = False
		self.last_greeting_time = time.time() - Const.TIMEOUT_GREETING_PERSON

	def new_buffer(self, sink, data):
		sample = self.sink.emit("pull-sample")
		arr = gst_to_opencv(sample)
		self.image_arr = arr
		return Gst.FlowReturn.OK

	def setupSink(self):
		sink = self.pipeline.get_by_name("sink")
		sink.set_property("emit-signals", True)
		sink.set_property("max-buffers", 2)
		sink.set_property("drop", True)
		sink.set_property("sync", False)
		return sink

	def startPlaying(self):
		try:
			ret = self.pipeline.set_state(Gst.State.PLAYING)
			if ret == Gst.StateChangeReturn.FAILURE:
				print("Unable to set the pipeline to the playing state.")

			self.bus = self.pipeline.get_bus()
			self.play()
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(fname, exc_tb.tb_lineno, e)

	def greetingHuman(self):
		if self.last_greeting_time + Const.TIMEOUT_GREETING_PERSON < time.time():
			try:
				websocket_client.sendMessage(command)
				self.faceDetected = True
				self.last_greeting_time = time.time()
			except Exception as e:
				exc_type, exc_obj, exc_tb = sys.exc_info()
				fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
				print(fname, exc_tb.tb_lineno, e)

	def detectFaceThread(self):
		while self.running:
			if self.image_arr is not None and self.face_detect:
				try:
					faces, landmarks = self.face_detect.detect(self.image_arr)
					if faces:
						print('Face detected')
						self.greetingHuman()
					else:
						print('No Face')
						self.faceDetected = False
				except Exception as e:
					exc_type, exc_obj, exc_tb = sys.exc_info()
					fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
					print(fname, exc_tb.tb_lineno, e)

	def play(self):
		self.running = True
		thread.start_new_thread(self.detectFaceThread, ())
		while self.running:
			if self.image_arr is not None:
				try:
					pass
				except Exception as e:
					exc_type, exc_obj, exc_tb = sys.exc_info()
					fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
					print(fname, exc_tb.tb_lineno, e)

			message = self.bus.timed_pop_filtered(10000, Gst.MessageType.ANY)
			self.handleMessage(message)

	def stopPlaying(self):
		try:
			self.running = False
			self.pipeline.set_state(Gst.State.NULL)
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(fname, exc_tb.tb_lineno, e)

	def handleMessage(self, message):
		if message:
			if message.type == Gst.MessageType.ERROR:
				err, debug = message.parse_error()
				print('gstreamer', '222', "Error received from element %s: %s" % (message.src.get_name(), err))
				print("Debugging information: %s" % debug)
				self.stopPlaying()
			elif message.type == Gst.MessageType.EOS:
				print("End-Of-Stream reached.")
				self.stopPlaying()
			elif message.type == Gst.MessageType.STATE_CHANGED:
				if isinstance(message.src, Gst.Pipeline):
					old_state, new_state, pending_state = message.parse_state_changed()
					print("Pipeline state changed from %s to %s." % (old_state.value_nick, new_state.value_nick))
			else:
				print("Unexpected message received.")

