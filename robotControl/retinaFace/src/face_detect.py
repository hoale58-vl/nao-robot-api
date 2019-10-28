import cv2
import sys, os
PWD = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(PWD, "../insightface/RetinaFace"))
import numpy as np
import datetime
import os
import glob
from retinaface import RetinaFace

class FaceDetect:
	def __init__(self, thresh= 0.85, scales = [480, 640], gpuid=0, network='net3',  weight_path=os.path.join(PWD, '../model/mobilenet/mnet.25')):
		ctx_id = 0
		self.thresh = thresh
		self.detector = RetinaFace(weight_path, ctx_id, gpuid, network)
		self.scales = scales

	def get_scales(self, frame):
		im_shape = frame.shape
		target_size = self.scales[0]
		max_size = self.scales[1]
		im_size_min = np.min(im_shape[0:2])
		im_size_max = np.max(im_shape[0:2])
		#if im_size_min>target_size or im_size_max>max_size:
		im_scale = float(target_size) / float(im_size_min)
		# prevent bigger axis from being more than max_size:
		if np.round(im_scale * im_size_max) > max_size:
			im_scale = float(max_size) / float(im_size_max)
		scales = [im_scale]
		return scales

	def detect(self, frame, flip = False):
		scales = self.get_scales(frame)
		faces, landmarks = self.detector.detect(frame, self.thresh, scales=scales, do_flip=flip)
		return faces, landmarks
		
	def draw_rect(self, frame, faces):
		if faces is not None:
			# print('Find', faces.shape[0], 'faces')
			for i in range(faces.shape[0]):
				box = faces[i].astype(np.int)
				color = (0,0,255)
				cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), color, 2)
		return frame

	def disconnect(self):
		cv2.destroyAllWindows()

def test():
	gpuid = -1 # or -1 -> CPU
	weight_path = os.path.join(PWD, '../model/mobilenet/mnet.25')
	face_detect = FaceDetect(gpuid=gpuid, weight_path=weight_path)

	img = cv2.imread(os.path.join(PWD, '../test/test.jpg'))
	faces, landmarks = face_detect.detect(img)

	result = face_detect.draw_rect(img, faces)

	filename = os.path.join(PWD, '../test/detect_test.jpg')
	cv2.imwrite(filename, img)

	return faces, landmarks