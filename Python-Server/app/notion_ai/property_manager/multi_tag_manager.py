from random import choice
from uuid import uuid1

import json
import requests

from notion_ai.property_manager.tag_object import TagObject
from notion_ai.utils import create_json_response
from server_utils.utils import SETTINGS_FOLDER, DEFAULT_COLOR


## This class manages the multi-choice tag property on a mind element. We can get current tags and add tags.
class MultiTagManager:
    def __init__(self, logging, client, mind_structure, options):
        self.logging = logging

        self.client = client
        self.mind_structure = mind_structure
        self.multi_tag_property = options['multi_tag_property']

    def get_multi_select_tags(self,notion_ai, append_tags, collection_index=None):
        #self.mind_structure.set_current_collection(int(collection_index))
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
                color = DEFAULT_COLOR
                print(element)
                if "color" in element:
                    color = self._notion_color_to_hex(element["color"])
                else:
                    element["color"] = color

                x = TagObject().parse_from_notion_element(element=element, tag_color=color)

                l.append(x)

            l = l + append_tags
            return create_json_response(notion_ai, status_code=200, append_content=l)
        else:
            if len(append_tags) > 0:
                return create_json_response(notion_ai, status_code=200, append_content=append_tags)
            else:
                raise ValueError(f'"{prop}" property has no tags on it.')

    def _get_multi_select_tags_as_list(self, collection_index=0):
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

    def update_multi_select_tags(self,notion_ai, id, tags_json, collection_index=0, color=None):
        try:
            # self.mind_structure.set_current_collection(int(collection_index))
            self.logging.info("Updating multi select tags for row {0} {1} {2}".format(id, tags_json, collection_index))
            print("Updating multi select tags for row {0} {1} {2}".format(id, tags_json, collection_index))
            block = self.client.get_block(id)

            current_tags_notion = self._get_multi_select_tags_as_list(collection_index)
            tag_to_add = []

            for tag in tags_json:

                if tag['option_name'] not in current_tags_notion or len(current_tags_notion) == 0:
                    print(tag['option_name'] + " is new")
                    value = self.add_new_multi_select_value(self.multi_tag_property, tag['option_name'], tag['option_color'])
                else:
                    print(tag['option_name'] + " already exists")
                    value = tag['option_name']
                tag_to_add.append(value)

            block.set_property(self.multi_tag_property, tag_to_add)

            if len(block.get_property(self.multi_tag_property)) > 0:
                return create_json_response(notion_ai, status_code=205, rowId=id)
            else:
                return create_json_response(notion_ai, status_code=206, rowId=id)

        except ValueError as e:
            self.logging.info(e)
            print(e)
        except requests.exceptions.HTTPError as e:
            print(e)
            self.logging.info(e)
            return create_json_response(notion_ai, status_code=e.response.status_code, rowId=id)

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
        else:
            color = self._hex_to_notion_color(color)

        print("Tag color for {0} will be {1}".format(value,color))

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

        if "options" in prop_schema:  # if there are no options in it, means there's no tags.
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

    def _notion_color_to_hex(self,color_name):
        if color_name == None:
            return  "#505558"
        elif color_name == "default":
            return  "#505558"
        elif color_name == "gray":
            return  "#6B6F71"
        elif color_name == "brown":
            return  "#695B55"
        elif color_name == "orange":
            return  "#9F7445"
        elif color_name == "yellow":
            return  "#9F9048"
        elif color_name == "green":
            return  "#467870"
        elif color_name == "blue":
            return  "#487088"
        elif color_name == "purple":
            return  "#6C598F"
        elif color_name == "pink":
            return  "#904D74"
        elif color_name == "red":
            return  "#9F5C58"

    def _hex_to_notion_color(self,color_name):
        if color_name == None:
            return  "default"
        if color_name == "#505558":
            return  "default"
        elif color_name == "#6B6F71":
            return  "gray"
        elif color_name == "#695B55":
            return  "brown"
        elif color_name == "#9F7445":
            return  "orange"
        elif color_name == "#9F9048":
            return  "yellow"
        elif color_name == "#467870":
            return  "green"
        elif color_name == "#487088":
            return  "blue"
        elif color_name == "#6C598F":
            return  "purple"
        elif color_name == "#904D74":
            return  "pink"
        elif color_name == "#9F5C58":
            return  "red"

