import os
import numpy as np
import cv2
import natsort

from .RefinedTramsmission import Refinedtransmission
from .getAtomsphericLight import getAtomsphericLight
from .getGbDarkChannel import getDarkChannel
from .getTM import getTransmission
from .sceneRadiance import sceneRadianceRGB

from config import config

def run(base_path=None, input_dirname=None, output_dirname=None):

	if base_path is None:
		base_path = config.get('BASE_PATH')
	if input_dirname is None:
		input_dirname = config.get('INPUT_DIRNAME')
	if output_dirname is None:
		output_dirname = config.get('OUTPUT_DIRNAME')

	in_path = os.path.join(base_path, input_dirname)
	out_path = os.path.join(base_path, output_dirname)
	files = os.listdir(in_path)
	files = natsort.natsorted(files)
	before_paths = []
	after_paths = []

	for i in range(len(files)):
		file = files[i]
		if file in config.get('IGNORE_FILES'):
			continue

		filepath = os.path.join(in_path, file)
		prefix = file.split('.')[0]
		format_ = file.split('.')[1]
		if os.path.isfile(filepath):
			print('Working on', file)
			before_paths.append(os.path.join(in_path, file))
			img = cv2.imread(before_paths[-1])

			blockSize = 9
			GB_Darkchannel = getDarkChannel(img, blockSize)
			AtomsphericLight = getAtomsphericLight(GB_Darkchannel, img)
			print('AtomsphericLight', AtomsphericLight)
			transmission = getTransmission(img, AtomsphericLight, blockSize)
			transmission = Refinedtransmission(transmission, img)
			sceneRadiance = sceneRadianceRGB(img, transmission, AtomsphericLight)
			
			after_paths.append(os.path.join(out_path, prefix + '_UDCP.' + format_))
			cv2.imwrite(after_paths[-1], sceneRadiance)
			cv2.imwrite(os.path.join(out_path, prefix + '_UDCP_transmission.' + format_), np.uint8(transmission * 255))
	
	return (before_paths, after_paths)


