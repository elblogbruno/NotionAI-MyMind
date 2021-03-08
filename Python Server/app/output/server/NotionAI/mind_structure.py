from utils.custom_errors import OnCollectionNotAvailable
from NotionAI.utils import get_joined_url
import json
import os

class MindStructure:
    def __init__(self, client, data):
        self.client = client
        self.data = data

    def get_collection_by_index(self, index=0):
        structure = self.get_mind_structure_from_json()
        if len(structure) > 0:
            collection_id = structure[index]["collection_id"]
            collection_block_page_id = structure[index]["collection_block_page_id"]
            return collection_id, collection_block_page_id
        else:
            self.logging.info("No structure or collection was found")
            raise OnCollectionNotAvailable

    def get_mind_structure(self, structure_url=None):
        if structure_url is None:
            structure_url = self.data['url']

        structure = self.client.get_block(structure_url)
        structure.refresh()
        available_connections = []
        for child in structure.children:
            if len(child.title) > 0:
                x = {
                    "collection_name": child.title,
                    "collection_id": child.collection.id,
                    "collection_url": get_joined_url(child.id),
                    "collection_block_page_id": child.id
                }
                available_connections.append(x)
            else:
                print("Blank structure found.")

        self.save_mind_structure(available_connections)
        return available_connections

    def save_mind_structure(self, available_connection):
        with open('mind_structure.json', 'w') as f:
            json.dump(available_connection, f)

    def get_mind_structure_from_json(self):
        if os.path.isfile('mind_structure.json'):
            structure = []
            with open('mind_structure.json') as json_file:
                structure = json.load(json_file)
            return structure
        else:
            return self.get_mind_structure()
