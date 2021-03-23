from random import choice
from uuid import uuid1
import json
import matplotlib
import requests

from NotionAI.utils import create_json_response
from utils.utils import settings_folder


## This class manages the multi-choice tag property on a mind element. We can get current tags and add tags.

class MultiTagManager:
    def __init__(self, logging, client, mind_structure, options):
        self.logging = logging

        self.client = client
        self.mind_structure = mind_structure
        self.multi_tag_property = options['multi_tag_property']

    def get_multi_select_tags(self, collection_index=0):
        self.mind_structure.set_current_collection(int(collection_index))
        prop = self.multi_tag_property
        print(prop)
        collection_schema = self.mind_structure.collection.get("schema")
        prop_schema = next(
            (v for k, v in collection_schema.items() if v["name"] == prop), None
        )
        if not prop_schema:
            raise ValueError(
                f'"{prop}" property does not exist on the collection!'
            )
        if prop_schema["type"] != "multi_select":
            raise ValueError(f'"{prop}" is not a multi select property!')
        l = []

        if "options" in prop_schema:
            for element in prop_schema["options"]:
                color = "#505558"

                if element["color"]:
                    if element["color"] == 'default':
                        color = "#505558"
                    elif matplotlib.colors.cnames[element["color"]]:
                        color = matplotlib.colors.cnames[element["color"]]

                x = {
                    "option_name": element["value"],
                    "option_id": element["id"],
                    "option_color": color,
                }
                l.append(x)
            return create_json_response(self, status_code=200, append_content=l)
        else:
            raise ValueError(f'"{prop}" property has no tags on it.')

    def get_multi_select_tags_as_list(self, collection_index=0):
        self.mind_structure.set_current_collection(int(collection_index))
        prop = self.multi_tag_property
        collection_schema = self.mind_structure.collection.get("schema")
        prop_schema = next(
            (v for k, v in collection_schema.items() if v["name"] == prop), None
        )
        if not prop_schema:
            raise ValueError(
                f'"{prop}" property does not exist on the collection!'
            )
        if prop_schema["type"] != "multi_select":
            raise ValueError(f'"{prop}" is not a multi select property!')

        l = []

        if "options" in prop_schema:
            for element in prop_schema["options"]:
                l.append(element["value"])
            return l
        else:
            return l

    def update_multi_select_tags(self, id, tags_json, collection_index=0, color=None):
        try:
            # self.mind_structure.set_current_collection(int(collection_index))
            self.logging.info("Updating multi select tags for row {0} {1} {2}".format(id,tags_json,collection_index))
            print("Updating multi select tags for row {0} {1} {2}".format(id,tags_json,collection_index))
            block = self.client.get_block(id)

            current_tags_notion = self.get_multi_select_tags_as_list(collection_index)
            current_tags = block.get_property(self.multi_tag_property)
            tag_to_add = []

            for tag in tags_json:

                if tag['option_name'] not in current_tags_notion or len(current_tags_notion) == 0:
                    print(tag['option_name'] + " is new")
                    value = self.add_new_multi_select_value(self.multi_tag_property, tag['option_name'])
                else:
                    print(tag['option_name'] + " already exists")
                    value = tag['option_name']
                tag_to_add.append(value)

            block.set_property(self.multi_tag_property, tag_to_add)

            if len(block.get_property(self.multi_tag_property)) > 0:
                return create_json_response(self, status_code=205, rowId=id)
            else:
                return create_json_response(self, status_code=404, rowId=id)

        except ValueError as e:
            self.logging.info(e)
            print(e)
        except requests.exceptions.HTTPError as e:
            print(e)
            self.logging.info(e)
            return create_json_response(self, status_code=429, rowId=id)

    def add_new_multi_select_value(self, prop, value, color=None):
        colors = [
            "default",
            "gray",
            "brown",
            "orange",
            "yellow",
            "green",
            "blue",
            "purple",
            "pink",
            "red",
        ]
        """`prop` is the name of the multi select property."""
        if color is None:
            color = choice(colors)

        collection_schema = self.mind_structure.collection.get("schema")
        prop_schema = next(
            (v for k, v in collection_schema.items() if v["name"] == prop), None
        )
        if not prop_schema:
            raise ValueError(
                f'"{prop}" property does not exist on the collection!'
            )
        if prop_schema["type"] != "multi_select":
            raise ValueError(f'"{prop}" is not a multi select property!')

        if "options" in prop_schema: # if there are no options in it, means there's no tags.
            dupe = next(
                (o for o in prop_schema["options"] if o["value"] == value), None
            )
            if dupe:
                print(f'"{value}" already exists in the schema!')
                print(dupe['value'])
                return dupe['value']

            prop_schema["options"].append(
                {"id": str(uuid1()), "value": value, "color": color}
            )
            self.mind_structure.collection.set("schema", collection_schema)
            return value
        else:
            prop_schema["options"] = []
            prop_schema["options"].append({"id": str(uuid1()), "value": value, "color": color})

            self.mind_structure.collection.set("schema", collection_schema)
            return value