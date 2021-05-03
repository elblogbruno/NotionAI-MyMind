from NotionAI.property_manager.multi_tag_manager import MultiTagManager
from utils.utils import SETTINGS_FOLDER
import json


class PropertyManager:
    def __init__(self, logging, client, mind_structure):
        self.logging = logging

        self.client = client
        self.mind_structure = mind_structure

        current_properties = {}
        with open(SETTINGS_FOLDER + 'properties.json') as json_file:
            current_properties = json.load(json_file)
            self.current_properties = current_properties
            self.multi_tag_manager = MultiTagManager(logging, self.client, self.mind_structure, current_properties)

    def update_properties(self, block, **kwargs):
        self.logging.info("Updating propertios {0} for this block {1}".format(kwargs.keys(), block.id))
        for key, value in kwargs.items():
            block.set_property(self.current_properties[str(key)], value)

    def get_properties(self, block, **kwargs):
        self.logging.info("Getting properties {0} for this block {1}".format(kwargs.keys(), block.id))
        for key, value in kwargs.items():
            return block.get_property(self.current_properties[str(key)])

    def get_property_name(self, block, **kwargs):
        self.logging.info("Getting properties {0} for this block {1}".format(kwargs.items().encode('utf8'), block.id))
        for key, value in kwargs.items():
            return self.current_properties[str(key)]
