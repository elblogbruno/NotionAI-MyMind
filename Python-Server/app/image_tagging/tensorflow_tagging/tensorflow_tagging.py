from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np

from tensorflow.python.keras.applications.inception_v3 import InceptionV3, preprocess_input, decode_predictions
from tensorflow.python.keras.preprocessing import image
import os
from utils.utils import download_image_from_url, createFolder


class TensorFlowTag:

    def __init__(self, delete_image_after_tagging=True):
        self.delete_after_tagging = delete_image_after_tagging
        self.model = InceptionV3(weights='imagenet')
        createFolder("./image_tagging/temp_image_folder")

    def get_tags(self, image_url, is_local_image, treshold):
        if treshold is None:
            treshold = 0.10

        if is_local_image:
            file = "./uploads/" + image_url.split("/")[-1]
        else:
            file = download_image_from_url(image_url)

        img = image.load_img(file, target_size=(299, 299))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)

        preds = self.model.predict(x)
        prediction_decoded = decode_predictions(preds, top=20)[0]

        print('Predicted:', prediction_decoded)

        tags = []
        for element in prediction_decoded:
            if element[2] > treshold:
                tags.append(element[1])

        if self.delete_after_tagging:
            os.remove(file)

        #str1 = ','.join(str(e) for e in tags)

        return tags
