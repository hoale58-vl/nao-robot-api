#! /usr/bin/env python
# encoding=utf8
import sys
from gi.repository import Gst
import Const
import _thread as thread
import os
from utils import gst_to_opencv
import cv2
import gi
import logging

logging.getLogger().setLevel(logging.INFO)

gi.require_version('Gst', '1.0')

font                                     = cv2.FONT_HERSHEY_SIMPLEX
bottomLeftCornerOfText = (10,500)
fontScale                            = 0.75
fontColor                            = (255,255,255)
fontColor2                            = (51, 51, 255)
lineType                             = 2
gender_label = ['F', 'M']
namedWindow = "FaceDetect"
if Const.SHOW_SCREEN:
	cv2.namedWindow(namedWindow, cv2.WINDOW_NORMAL)
	cv2.resizeWindow(namedWindow, 1200,900)

class NaoGstreamer(object):
	def __init__(self,  face_detect=None, agegender=None):
		super(NaoGstreamer, self).__init__()
		Gst.init(None)
		self.websocket_client = None
		CLI = ("udpsrc port={} ! application/x-rtp, encoding-name=JPEG,payload=26 ! rtpjpegdepay ! jpegdec ! appsink name=sink").format(Const.GSPORT)
		self.pipeline = Gst.parse_launch(CLI)
		self.sink = self.setupSink()
		self.sink.connect("new-sample", self.new_buffer, self.sink)

		self.image_arr = None
		self.bus = None
		self.face_detect = face_detect
		self.agegender = agegender

		self.faceDetected = False

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
				logging.error("Unable to set the pipeline to the playing state.")

			self.bus = self.pipeline.get_bus()
			self.play()
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			logging.error("File: {} - Line: {} - Error: {}".format(fname, exc_tb.tb_lineno, str(e)))

	def greetingHuman(self):
		try:
			if self.websocket_client is not None:
				self.websocket_client.sendMessage("face::::detected::::detected")
			self.faceDetected = True
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			logging.error("File: {} - Line: {} - Error: {}".format(fname, exc_tb.tb_lineno, str(e)))

	def detectFaceThread(self):
		while True:
			if self.running:
				if self.image_arr is not None and self.face_detect:
					try:
						faces, landmarks = self.face_detect.detect(self.image_arr)
						if faces.shape[0]:
							# logging.debug("Face detected")
							if Const.SHOW_SCREEN:
								self.image_arr = self.face_detect.draw_rect(self.image_arr, faces)
								if self.agegender:
									for face_num in range(len(faces)):
										align = self.agegender.preprocess(self.image_arr, faces[face_num], landmarks[face_num])
										gender, age = self.agegender.get_ga(align)
										text = gender_label[gender] + ' - ' + str(age)
										cv2.putText(self.image_arr, text, 
											(int(faces[face_num][0]), int(faces[face_num][1])), 
											font, 
											fontScale,
											fontColor2,
											lineType
										)
								cv2.imshow(namedWindow, self.image_arr)
								cv2.waitKey(1)
							self.greetingHuman()
						else:
							if Const.SHOW_SCREEN:
								cv2.imshow(namedWindow, self.image_arr)
								cv2.waitKey(1)
							# logging.debug("No Face")
							self.faceDetected = False
					except Exception as e:
						exc_type, exc_obj, exc_tb = sys.exc_info()
						fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
						logging.error("File: {} - Line: {} - Error: {}".format(fname, exc_tb.tb_lineno, str(e)))

	def play(self):
		self.running = False
		thread.start_new_thread(self.detectFaceThread, ())
		while True:
			if self.running:
				if self.image_arr is not None:
					try:
						pass
					except Exception as e:
						exc_type, exc_obj, exc_tb = sys.exc_info()
						fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
						logging.error("File: {} - Line: {} - Error: {}".format(fname, exc_tb.tb_lineno, str(e)))

				message = self.bus.timed_pop_filtered(10000, Gst.MessageType.ANY)
				self.handleMessage(message)

	def stopPlaying(self):
		try:
			self.running = False
			# self.pipeline.set_state(Gst.State.NULL)
			self.face_detect.disconnect()
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			logging.error("File: {} - Line: {} - Error: {}".format(fname, exc_tb.tb_lineno, str(e)))

	def handleMessage(self, message):
		if message:
			if message.type == Gst.MessageType.ERROR:
				err, debug = message.parse_error()
				logging.error("Error received from element %s: %s" % (message.src.get_name(), err))
				logging.debug("Debugging information: %s" % debug)
				self.stopPlaying()
			elif message.type == Gst.MessageType.EOS:
				logging.info("End-Of-Stream reached.")
				self.stopPlaying()
			elif message.type == Gst.MessageType.STATE_CHANGED:
				if isinstance(message.src, Gst.Pipeline):
					old_state, new_state, pending_state = message.parse_state_changed()
					logging.info("Pipeline state changed from %s to %s." % (old_state.value_nick, new_state.value_nick))
			else:
				logging.info("Unexpected message received.")

