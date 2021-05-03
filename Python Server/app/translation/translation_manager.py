import json
import re
from utils.custom_errors import OnServerNotConfigured
from utils.utils import SETTINGS_FOLDER




class TranslationManager:
    def __init__(self, logging, static_folder):
        self.language_code = self.get_current_language_code()
        self.TRANSLATIONS_FOLDER = "{0}/translations/".format(static_folder)
        logging.info("Translation Manager created with this language code {0}".format(self.language_code))

    def get_sentence_by_code(self, status_code):
        filename = "{0}{1}.json".format(self.TRANSLATIONS_FOLDER, self.language_code)
        translated_sentence = "no translation found"
        status = "error"
        with open(filename, encoding='utf8') as json_file:
            data = json.load(json_file)
            translated_sentence = str(data['sentences'][str(status_code)]["response"])
            status = str(data['sentences'][str(status_code)]["status"])
        return translated_sentence, status

    def get_response_text(self, status_code):
        print("Sending response {}".format(status_code))
        return self.get_sentence_by_code(status_code)

    def get_current_language_code(self):
        option_file = SETTINGS_FOLDER + "options.json"
        language_code = "en_US"
        try:
            with open(option_file) as option_file:
                data = json.load(option_file)
                language_code = data['language_code']
            return language_code
        except FileNotFoundError as e:
            return language_code
