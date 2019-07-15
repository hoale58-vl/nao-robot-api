import numpy as np
import cv2
import os, sys

def gst_to_opencv(sample):
	try:
		buf = sample.get_buffer()
		caps = sample.get_caps()
		height = caps.get_structure(0).get_value('height')
		width = caps.get_structure(0).get_value('width')

		height = height * 3 / 2

		arr = np.frombuffer(buf.extract_dup(0, buf.get_size()), dtype=np.uint8)
		cv_mat = arr.reshape((height, width, -1))
		rgb = cv2.cvtColor(cv_mat, cv2.COLOR_YUV420P2RGB)
		return rgb
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(fname, exc_tb.tb_lineno, e)
	return None