import json
from utils.lang_utils import get_response_text
from utils.custom_errors import OnUrlNotValid, OnImageNotFound
from notion.block import ImageBlock
from time import sleep

import requests
import validators
import webbrowser
import socket


##Makes a web request to the notion web clipper API to add url's and returns the rowId
def web_clipper_request(self, url, title):
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
            "blockId": "{}".format(self.current_mind_id),
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
        rowId = json_response['createdBlockIds'][0]
        print(rowId)
        return rowId
    else:
        raise OnUrlNotValid("Invalid url was sent", self)


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
        return extract_image_from_content(content, row_id)
    return list_of_img_url


def create_json_response(self, status_code=None, rowId=None):
    url = "https://github.com/elblogbruno/NotionAI-MyMind/wiki/Common-Issues"

    block_title = "-1"
    block_attached_url = "-1"

    if status_code is None:
        status_code = self.statusCode

    if rowId is not None:
        url = get_joined_url(rowId)
        row = self.client.get_block(rowId)
        block_title = row.title
        block_attached_url = row.url

    text_response, status_text = get_response_text(status_code)

    if len(block_attached_url) == 0:
        block_attached_url = "-1"

    if len(block_title) == 0:
        block_title = "-1"

    x = {
        "status_code": status_code,
        "text_response": text_response,
        "status_text": status_text,
        "block_url": url,
        "block_title": block_title,
        "block_attached_url": block_attached_url,
    }

    # convert into JSON:
    json_response = json.dumps(x)

    return json_response


# based on the machine doing the request we know which extension is being used
def get_current_extension_name(platform):
    if platform is None or len(platform) == 0:
        return "Unknown mind extension"
    elif platform in ['android', 'ipad', 'iphone', 'symbian', 'blackberry']:
        return "phone-app-extension"
    else:
        return "browser-extension"


def open_browser_at_start(self, port):
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    final_url = "http://{0}:{1}/".format(str(local_ip), str(port))

    print("You should go to the homepage and set the credentials. The url will open in your browser now. If can't "
          "access a browser you can access {0}".format(final_url))

    self.logging.info("You should go to the homepage and set the credentials. The url will open in your browser "
                      "now. If can't access a browser you can access {0}".format(final_url))

    webbrowser.open(final_url)


def get_joined_url(rowId):
    rowIdExtracted = rowId.split("-")
    str1 = ''.join(str(e) for e in rowIdExtracted)
    url = "https://www.notion.so/" + str1
    return url
