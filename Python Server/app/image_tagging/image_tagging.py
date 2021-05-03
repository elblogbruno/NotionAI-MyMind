from NotionAI.property_manager.tag_object import TagObject
from image_tagging.clarifai_tagging.clarifai_tagging import ClarifaiAI
from image_tagging.tensorflow_tagging.tensorflow_tagging import TensorFlowTag
from utils.utils import SETTINGS_FOLDER
import json


# This class holds the image tagging system, and it seems as a parent for the Clarifai and Tensorflow tagging
# mechanisms.
class ImageTagging:

    def __init__(self, data, logging):
        options = {}
        self.logging = logging
        with open(SETTINGS_FOLDER + 'tagging_options.json') as json_file:
            options = json.load(json_file)
        try:
            self.options = options
            self.treshold = 0.20
            if 'confidence_treshold' in options:
                self.treshold = float(options['confidence_treshold'])
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
        return self.predictor.get_tags(image_url, is_image_local, self.treshold)

    def print_current_detector(self):
        if self.options['use_clarifai']:
            self.logging.info("Using clarifai predictor with treshold: {}".format(self.treshold))
        else:
            self.logging.info("Using tensorflow predictor, with delete_after_tagging = {0} and treshold: {1}".format(
                self.options['delete_after_tagging'], self.treshold))

    def remove_duplicated_tags(self, lists_of_tags):
        res = []
        for l in lists_of_tags:
            for i in l:
                if i not in res:
                    res.append(i)
        return res

    def count_duplicated_tags(self, lists_of_tags):
        res = {}
        for tags in lists_of_tags:
            for tag in tags:
                if tag:
                    if tag not in res:
                        res[tag] = 1
                    else:
                        res[tag] = res[tag] + 1
        return res

    def get_most_used_ai_tags(self,notion_ai,collection_index):
        print("Getting most tags")
        #notion_ai.mind_structure.set_current_collection(collection_index)

        rows = notion_ai.mind_structure.collection.get_rows()

        all_tags = []

        for row in rows:
            ai_tags = notion_ai.property_manager.get_properties(row, ai_tags_property=1).split(",")
            if len(ai_tags) > 0:
                all_tags.append(ai_tags)

        freq = self.count_duplicated_tags(all_tags)

        sorted_freq = sorted(freq, key=freq.get, reverse=True)

        if len(sorted_freq) > 0:
            for i in range(len(sorted_freq)):
                sorted_freq[i] = TagObject(tag_value=sorted_freq[i]).to_dict()

        return sorted_freq
