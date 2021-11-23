import uuid
import random

class TagObject:
    def __init__(self, tag_value=None, tag_id=None, tag_color=None):
        self.option_name = tag_value

        if tag_id is None:
            tag_id = str(uuid.uuid1())
        if tag_color is None:
            tag_color = "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])

        x = {
            "option_name": tag_value,
            "option_id": tag_id,
            "option_color": tag_color,
        }

        self.dic = x

    def __str__(self):
        return self.dic

    def to_dict(self):
        return self.dic

    def value(self):
        return self.dic["option_name"]

    def id(self):
        return self.dic["option_id"]

    def color(self):
        return self.dic["option_color"]

    def parse_from_notion_element(self, element, tag_color):
        print("Parsing Notion Element Tag {0}".format(element))

        x = {
            "option_name": element["value"],
            "option_id": element["id"],
            "option_color": tag_color,
        }

        return x
