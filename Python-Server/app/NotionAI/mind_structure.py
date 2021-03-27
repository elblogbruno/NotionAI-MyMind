import requests

from utils.custom_errors import OnCollectionNotAvailable
from NotionAI.utils import get_joined_url
import json
import os
from utils.utils import settings_folder

class MindStructure:
    def __init__(self, client, data):
        self.client = client
        self.data = data
        self.collection_index = -1

    def set_current_collection(self, index=0,id=None):
        print("Getting collection at index {}".format(index))
        try:
            if hasattr(self, 'collection_index') and index == self.collection_index:
                print("Collection is the same as requested before. {0} {1}".format(self.collection_index, index))
            else:
                collection_id, id = self.get_collection_by_index(
                    index)  # collection is our database or "mind" in notion, as be have multiple, if not suplied, it will get the first one as the priority one.
                self.collection = self.client.get_collection(collection_id=collection_id)
                self.current_mind_id = id
                self.collection_index = index
        except requests.exceptions.HTTPError as e:
            print("Http error : " + str(e))

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
                    "collection_block_page_id": child.id,
                    "collection_cover": self.process_cover(child.collection.cover)
                }
                available_connections.append(x)
            else:
                print("Blank structure found.")

        self.save_mind_structure(available_connections)
        return available_connections

    def process_cover(self, cover):
        url = cover
        if url:
            if "http" not in cover or "https" not in cover:
                url = "https://www.notion.so" + cover
        else:
            url = "https://images.unsplash.com/photo-1579546929662-711aa81148cf?ixlib=rb-1.2.1&ixid=MXwxMjA3fDB8MHxleHBsb3JlLWZlZWR8MXx8fGVufDB8fHw%3D&w=1000&q=80"
        print(url)
        return url

    def save_mind_structure(self, available_connection):
        with open(settings_folder+'mind_structure.json', 'w') as f:
            json.dump(available_connection, f)

    def get_mind_structure_from_json(self):
        if os.path.isfile(settings_folder+'mind_structure.json'):
            structure = []
            with open(settings_folder+'mind_structure.json') as json_file:
                structure = json.load(json_file)
            return structure
        else:
            return self.get_mind_structure()
