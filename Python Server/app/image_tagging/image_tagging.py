from image_tagging.clarifai_tagging.clarifai_tagging import ClarifaiAI
from image_tagging.tensorflow_tagging.tensorflow_tagging import TensorFlowTag
from utils.utils import settings_folder
import json


class ImageTagging:

    def __init__(self, data, logging):
        options = {}
        with open(settings_folder+'options.json') as json_file:
            options = json.load(json_file)
        try:
            self.options = options
            self.treshold = 0.20
            if 'treshold' in options:
                self.treshold = options['treshold']
            if options['use_clarifai']:
                self.predictor = ClarifaiAI(data['clarifai_key'])
                logging.info("Using clarifai predictor")
            else:
                self.predictor = TensorFlowTag(options['delete_after_tagging'])
                logging.info("Using tensorflow predictor, with delete_after_tagging = {}".format(
                    options['delete_after_tagging']))
        except FileNotFoundError:
            logging.info("options.json not found")
            print("Wrong file or file path")

    def get_tags(self, image_url, is_image_local):
        self.print_current_detector()
        return self.predictor.get_tags(image_url, is_image_local,self.treshold)

    def print_current_detector(self):
        if self.options['use_clarifai']:
            print("Using clarifai predictor with treshold: {}".format(self.treshold))
        else:
            print("Using tensorflow predictor, with delete_after_tagging = {0} and treshold: {1}".format(
                self.options['delete_after_tagging'],self.treshold))

    def remove_duplicated_tags(self,lists_of_tags):
        res = []
        for l in lists_of_tags:
            for i in l:
                if i not in res:
                    res.append(i)
        return res