import sys
sys.path.append("../insightface/src/common")
import face_preprocess
import cv2
import sklearn
import numpy as np
import mxnet as mx


class RecognitionModel:
	def __init__(self, gpuid, weight_path, threshold = 0.5, agegender = False):
		image_size = (112,112)
		ctx = mx.gpu(gpuid)
		if not agegender:
			self.model = self.get_model(ctx, image_size, weight_path, 'fc1')
		else:
			self.ga_model = self.get_model(ctx, image_size, weight_path, 'fc1')
		self.threshold = threshold
		self.image_size = image_size

	def get_model(self, ctx, image_size, weight_path, layer):
		epoch = 0
		sym, arg_params, aux_params = mx.model.load_checkpoint(weight_path, epoch)
		all_layers = sym.get_internals()
		sym = all_layers[layer+'_output']
		model = mx.mod.Module(symbol=sym, context=ctx, label_names = None)
		#model.bind(data_shapes=[('data', (args.batch_size, 3, image_size[0], image_size[1]))], label_shapes=[('softmax_label', (args.batch_size,))])
		model.bind(data_shapes=[('data', (1, 3, image_size[0], image_size[1]))])
		model.set_params(arg_params, aux_params)
		return model
		
	def preprocess(self, face_img, bbox, points):
		nimg = face_preprocess.preprocess(face_img, bbox, points, image_size='112,112')
		nimg = cv2.cvtColor(nimg, cv2.COLOR_BGR2RGB)
		aligned = np.transpose(nimg, (2,0,1))
		return aligned

	def get_feature(self, aligned):
		input_blob = np.expand_dims(aligned, axis=0)
		data = mx.nd.array(input_blob)
		db = mx.io.DataBatch(data=(data,))
		self.model.forward(db, is_train=False)
		embedding = self.model.get_outputs()[0].asnumpy()
		embedding = sklearn.preprocessing.normalize(embedding).flatten()
		return embedding

	def get_ga(self, aligned):
		input_blob = np.expand_dims(aligned, axis=0)
		data = mx.nd.array(input_blob)
		db = mx.io.DataBatch(data=(data,))
		self.ga_model.forward(db, is_train=False)
		ret = self.ga_model.get_outputs()[0].asnumpy()
		g = ret[:,0:2].flatten()
		gender = np.argmax(g)
		a = ret[:,2:202].reshape( (100,2) )
		a = np.argmax(a, axis=1)
		age = int(sum(a))

		return gender, age


def test_recog():
	gpuid = 0 # -> GPU or -1 -> CPU
	weight_path = './model-detect'
	recognition = RecognitionModel(gpuid=gpuid, weight_path=weight_path)

	# Face1
	face_num = 0
	img = cv2.imread('t2.jpg')
	align = recognition.preprocess(img, faces[face_num], landmarks[face_num])
	f1 = recognition.get_feature(align)

	# Face2
	face_num = 0
	img = cv2.imread('t3.jpg')
	align = recognition.preprocess(img, faces[face_num], landmarks[face_num])
	f2 = recognition.get_feature(align)

	# Euclide distance 
	dist = np.sum(np.square(f4-f5))
	print(dist)

	# Array multi
	sim = np.dot(f8, f9.T)
	print(sim)

def test_age_gender():
	gpuid = 0 # -> GPU or -1 -> CPU
	weight_path = './model-agegender'
	agegender = RecognitionModel(gpuid=gpuid, weigh t_path=weight_path, agegender = True)

	face_num = 0
	img = cv2.imread('t2.jpg')
	align = agegender.preprocess(img, faces[face_num], landmarks[face_num])
	gender, age = agegender.get_ga(align)
	print(gender, age)

	crop_img = img[int(faces[face_num][1]):int(faces[face_num][3]), int(faces[face_num][0]):int(faces[face_num][2])]
	filename = './age_gender.jpg'
	cv2.imwrite(filename, crop_img)