import json

from translation.translation_manager import TranslationManager
from .custom_errors import OnUrlNotValid, OnImageNotFound, OnServerNotConfigured, OnWebClipperError
from server_utils.utils import open_website

from notion.block import ImageBlock
from time import sleep

import requests
import validators
import socket




##Makes a web request to the notion web clipper API to add url's and returns the rowId

def web_clipper_request(self, url, title, current_mind_id, logging):
    try:
        cookies = {
            'token_v2': self.token_v2,
        }

        headers = {
            'Content-Type': 'application/json',
        }
        if title == None:
            title = url

        is_well_formed = validators.url(url)

        if is_well_formed:
            url_object = {
                "url": url,
                "title": title
            }
            data_dict = {
                "type": "block",
                "blockId": "{}".format(current_mind_id),
                "property": "P#~d",
                "items": [url_object],
                "from": "chrome"
            }
            data = json.dumps(data_dict)

            self.logging.info(data)
            response = requests.post('https://www.notion.so/api/v3/addWebClipperURLs', headers=headers, cookies=cookies,
                                     data=data)
            response_text = response.text

            json_response = json.loads(response_text)

            if 'createdBlockIds' in json_response:
                rowId = json_response['createdBlockIds'][0]
                return rowId
            else:
                raise OnWebClipperError(json_response)
        else:
            raise OnUrlNotValid("Invalid url was sent", self)
    except KeyError as e:
        raise OnServerNotConfigured(e)


##Extracts all images from content as a list of url's
def extract_image_from_content(self, page_content, row_id):
    print("Will look for images on {}".format(page_content))
    list_of_img_url = []
    ##This loop looks at all the page content and finds every image on it.
    for element in page_content:
        im = self.client.get_block(element)
        block_type = im.get('type')
        if block_type == 'image':
            list_of_img_url.append(im.source)
        elif len(im.children) > 0:
            for child in im.children:
                if isinstance(child, ImageBlock):
                    list_of_img_url.append(child.source)

    if len(list_of_img_url) == 0 and self.counter == self.times_to_retry:
        self.counter = 0
        print("Thumbnail Image URL not found. Value is None")
        raise OnImageNotFound("Thumbnail Image URL not found. Value is None", self)
    elif len(list_of_img_url) > 0:
        self.counter = 0
        self.logging.info("These images were found: " + str(list_of_img_url))
        return list_of_img_url
    else:
        row = self.client.get_block(row_id)
        row.refresh()
        content = row.get('content')
        sleep(0.15)
        self.counter += 1
        return extract_image_from_content(self, content, row_id)
    return list_of_img_url


def create_json_response(notion_ai, status_code = None, error_sentence=None, rowId=None, custom_sentence=None, append_content=None, port=None, custom_url="https://github.com/elblogbruno/NotionAI-MyMind/wiki/Common-Issues"):
    notion_ai.logging.info("Creating json response.")
    # if error_sentence is None:
    #     error_sentence = "No translation found"

    if hasattr(notion_ai, 'loaded') and notion_ai.loaded:
        url = custom_url

        block_title = "-1"
        block_attached_url = "-1"

        if status_code is None:
            if hasattr(notion_ai, "status_code"):
                status_code = notion_ai.status_code
            else:
                status_code = 404
        else:
            notion_ai.status_code = status_code

        if rowId is not None:
            url = get_joined_url(rowId)
            row = notion_ai.client.get_block(rowId)
            block_title = row.title
            block_attached_url = row.url

        text_response = error_sentence
        status_text = "error"

        if text_response is None:
            text_response, status_text = notion_ai.translation_manager.get_response_text(status_code)

        if text_response == "error":
            text_response = error_sentence

        if len(block_attached_url) == 0:
            block_attached_url = "-1"
            if notion_ai.counter <= notion_ai.times_to_retry:
                notion_ai.counter = notion_ai.counter + 1
                return create_json_response(notion_ai=notion_ai, error_sentence=error_sentence, status_code=status_code, rowId=rowId, custom_sentence=custom_sentence, append_content=append_content, port=port, custom_url=custom_url)

        if len(block_title) == 0:
            block_title = "-1"

        if custom_sentence:
            text_response = custom_sentence

        x = {
            "status_code": status_code,
            "text_response": text_response,
            "status_text": status_text,
            "block_url": url,
            "block_title": block_title,
            "block_attached_url": block_attached_url,
            "extra_content": "null",
        }

        if append_content:
            x["extra_content"] = append_content
        # convert into JSON:
        json_response = json.dumps(x, ensure_ascii=False)
        print(json_response)
        return json_response
    else:
        notion_ai.translation_manager = TranslationManager(notion_ai.logging, notion_ai.static_folder)  # we initialize the translation manager
        text_response, status_text = notion_ai.translation_manager.get_response_text(status_code)

        x = {
            "status_code": status_code,
            "text_response": text_response,
            "status_text": status_text,
            "block_url": get_server_url(port),
            "block_title": "-1",
            "block_attached_url": "-1",
            "extra_content": "null",
        }
        # convert into JSON:
        json_response = json.dumps(x)
        return json_response


# based on the machine doing the request we know which extension is being used
def get_current_extension_name(platform):
    print("Extension request platform is {}".format(platform))
    if platform is None or len(platform) == 0:
        print("Final platform is unknown")
        return "Unknown mind extension"
    elif 'dart' in platform:
        print("Final platform is android")
        return "phone-app-extension"
    else:
        print("Final platform is browser")
        return "browser-extension"


def open_browser_at_start(self, port):
    final_url = get_server_url(port)

    print("You should go to the homepage and set the credentials. The url will open in your browser now. If can't "
          "access a browser you can access {0}".format(final_url))

    self.logging.info("You should go to the homepage and set the credentials. The url will open in your browser "
                      "now. If can't access a browser you can access {0}".format(final_url))

    open_website(final_url)


def get_server_url(port):
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    final_url = "http://{0}:{1}/".format(str(local_ip), str(port))
    return final_url


def get_joined_url(rowId):
    rowIdExtracted = rowId.split("-")
    str1 = ''.join(str(e) for e in rowIdExtracted)
    url = "https://www.notion.so/" + str1
    return url
