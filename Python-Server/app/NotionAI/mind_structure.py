import requests

from utils.custom_errors import OnCollectionNotAvailable, OnServerNotConfigured
from NotionAI.utils import get_joined_url,create_json_response
import json
import os
from utils.utils import SETTINGS_FOLDER, download_image_from_url
import urllib.parse

class MindStructure:
    def __init__(self,notion_ai, client, data, logging):
        self.client = client
        self.data = data
        self.collection_index = -1
        self.logging = logging
        self.notion_ai = notion_ai


        self.loaded = False

    def set_current_collection(self, index=0, id=None):
        print("Getting collection at index {0}".format(index))
        try:
            if hasattr(self, 'collection_index') and index == self.collection_index:
                print("Collection is the same as requested before. {0} {1}".format(self.collection_index, index))
            else:
                print("Collection is not the same as requested before. {0} {1}".format(self.collection_index, index))
                collection_id, id = self.get_collection_by_index(
                    int(index))  # collection is our database or "mind" in notion, as be have multiple, if not suplied, it will get the first one as the priority one.
                self.collection = self.client.get_collection(collection_id=collection_id)
                self.current_mind_id = id
                self.collection_index = index
        except requests.exceptions.HTTPError as e:
            print("Http error : " + str(e))
        except OnCollectionNotAvailable as e:
            print("mind error: " + str(e))

    def get_collection_by_index(self, index=0):
        structure = self.get_mind_structure_from_json()
        if len(structure) > 0 and int(index) >= 0:
            collection_id = structure[index]["collection_id"]
            collection_block_page_id = structure[index]["collection_block_page_id"]
            return collection_id, collection_block_page_id
        else:
            self.logging.info("No structure or collection was found")
            raise OnCollectionNotAvailable

    def get_mind_structure(self, notion_ai, structure_url=None):
        if structure_url is None:
            try:
                structure_url = self.data['url']
            except AttributeError as e:
                raise OnServerNotConfigured(str(e))


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
                    "collection_cover": self.process_cover(child.collection.cover,child.collection.id)
                }
                available_connections.append(x)
            else:
                print("Blank structure found.")

        if len(available_connections) > 0:
            self.save_mind_structure(available_connections)
            self.loaded = True
        else:
            self.loaded = False
        return create_json_response(notion_ai, status_code=300, append_content=available_connections)

    #https://github.com/jamalex/notion-py/issues/324
    def process_cover(self, cover, collection_id):
        url = cover
        if url:
            if "http" not in cover or "https" not in cover:
                url = "https://www.notion.so" + cover
            else:
                cover = urllib.parse.quote(cover)
                cover = cover.replace("/","%2F")
                url = "https://www.notion.so/image/{0}?table=collection&id={1}&width=300&userId={2}&cache=v2".format(cover,collection_id, self.client.current_user.id)
        else:
            url = "https://images.unsplash.com/photo-1579546929662-711aa81148cf?ixlib=rb-1.2.1&ixid=MXwxMjA3fDB8MHxleHBsb3JlLWZlZWR8MXx8fGVufDB8fHw%3D&w=1000&q=80"
        return url

    def save_mind_structure(self, available_connection):
        try:
            with open(SETTINGS_FOLDER + 'mind_structure.json', 'w') as f:
                json.dump(available_connection, f)
        except FileNotFoundError as e:
            raise OnServerNotConfigured(e)


    def get_mind_structure_from_json(self):
        if os.path.isfile(SETTINGS_FOLDER + 'mind_structure.json'):
            print("Mind json file found.")
            structure = {}
            with open(SETTINGS_FOLDER + 'mind_structure.json') as json_file:
                structure = json.load(json_file)
            return structure
        else:
            print("Mind json file not found. Creating...")
            return self.get_mind_structure(notion_ai=self.notion_ai)
