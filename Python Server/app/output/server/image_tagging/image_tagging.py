from image_tagging.clarifai_tagging.ClarifaiAI import ClarifaiAI
from image_tagging.tensorflow_tagging.tensorflow_tagging import TensorFlowTag
import json


class ImageTagging:

    def __init__(self, data, logging):
        options = {}
        with open('options.json') as json_file:
            options = json.load(json_file)
        try:
            self.options = options
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
        return self.predictor.get_tags(image_url, is_image_local)

    def print_current_detector(self):
        if self.options['use_clarifai']:
            print("Using clarifai predictor")
        else:
            print("Using tensorflow predictor, with delete_after_tagging = {}".format(
                self.options['delete_after_tagging']))
