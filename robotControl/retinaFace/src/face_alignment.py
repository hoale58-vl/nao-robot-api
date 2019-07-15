import sys
sys.path.append("../insightface/alignment")
import argparse
import cv2
import sys
import numpy as np
import os
import mxnet as mx
import datetime
import img_helper

class FaceAlignment:
	def __init__(self, weight_path, epoch=0, gpuid=0):
		if gpuid>=0:
			ctx = mx.gpu(gpuid)
		else:
			ctx = mx.cpu()
		sym, arg_params, aux_params = mx.model.load_checkpoint(weight_path, epoch)
		all_layers = sym.get_internals()
		sym = all_layers['heatmap_output']
		image_size = (128, 128)
		self.image_size = image_size
		model = mx.mod.Module(symbol=sym, context=ctx, label_names = None)
		model.bind(for_training=False, data_shapes=[('data', (1, 3, image_size[0], image_size[1]))])
		model.set_params(arg_params, aux_params)
		self.model = model
	
	def align(self, frame, faces):
		if faces.shape[0]==0:
			return None
		
		faces = faces[:,0:4]
		align_faces = []
		M_array = []
		ta = datetime.datetime.now()
		for j in range(faces.shape[0]):
			M = img_helper.estimate_trans_bbox(faces[j], self.image_size[0], s = 2.0)
			rimg = cv2.warpAffine(frame, M, self.image_size, borderValue = 0.0)
			frame2 = cv2.cvtColor(rimg, cv2.COLOR_BGR2RGB)
			frame2 = np.transpose(frame2, (2,0,1)) #3*112*112, RGB
			input_blob = np.zeros( (1, 3, self.image_size[1], self.image_size[0]),dtype=np.uint8 )
			input_blob[0] = frame2
			data = mx.nd.array(input_blob)
			db = mx.io.DataBatch(data=(data,))
			self.model.forward(db, is_train=False)
			alabel = self.model.get_outputs()[-1].asnumpy()[0]
			ret = np.zeros( (alabel.shape[0], 2), dtype=np.float32)
			for i in range(alabel.shape[0]):
				a = cv2.resize(alabel[i], (self.image_size[1], self.image_size[0]))
				ind = np.unravel_index(np.argmax(a, axis=None), a.shape)
				ret[i] = (ind[1], ind[0]) #w, h
			align_faces.append(ret)
			M_array.append(M)
			
		tb = datetime.datetime.now()
		print('Align module ', faces.shape[0] , ' faces with time cost: ', (tb-ta).total_seconds())
		return align_faces, M_array
	
	def visualize_landmark(self, frame, align_faces, M_array):
		for j in range(len(M_array)):
			IM = cv2.invertAffineTransform(M_array[j])
			for i in range(align_faces[j].shape[0]):
				p = align_faces[j][i]
				point = np.ones( (3,), dtype=np.float32)
				point[0:2] = p
				point = np.dot(IM, point)
				point = (int(point[0]), int(point[1]))
				cv2.circle(frame, point, 1, (0, 255, 0), 2)
		return frame
	
	def test_align_one_face(self, frame, landmark):
		for i in range(landmark.shape[0]):
				p = landmark[i]
				point = np.ones( (3,), dtype=np.float32)
				point[0:2] = p
				point = (int(point[0]), int(point[1]))
				cv2.circle(frame, point, 1, (0, 255, 0), 2)
		return frame


def test():
	gpuid = 0 # -> GPU or -1 -> CPU
	weight_path = './insightface/alignment/model/model'
	face_align = FaceAlignment(gpuid=gpuid, weight_path=weight_path)

	align_faces, M_array = face_align.align(img, faces)
	return align_faces, M_array