from notion.client import NotionClient
from notion.block import ImageBlock, TextBlock

import validators
import os

from custom_errors import OnImageNotFound, OnUrlNotValid, EmbedableContentNotFound, NoTagsFound

import requests
import json

from threading import Thread

from image_tagging.image_tagging import ImageTagging
from lang_utils import get_response_text


class NotionAI:
    def __init__(self, logging):
        self.logging = logging
        logging.info("Initiating NotionAI Class.")
        if os.path.isfile('data.json'):
            print("Initiating with a found config file.")
            logging.info("Initiating with a found config file.")
            self.loaded = self.run(logging)
        else:
            print("You should go to the homepage and set the config.")
            self.logging.info("You should go to the homepage and set the config.")

    def run(self, logging, email=None, password=None):
        loaded = False
        data = {}
        with open('data.json') as json_file:
            data = json.load(json_file)
        try:
            self.logging = logging
            self.logging.info("Running notionAI with " + str(data))
            self.data = data

            if email is not None and password is not None:
                print("Login in with email")
                self.logging.info("Login in with email")
                self.client = NotionClient(email=email, password=password)
                token_v2 = self.client.session.cookies.get("token_v2")
            elif data['token']:
                print("Login in with tokenV2")
                self.logging.info("Login in with tokenV2")
                self.client = NotionClient(token_v2=data['token'])
                token_v2 = data['token']
            else:
                print("No token_v2 or email available")
                return

            self.token_v2 = token_v2

            print("Token V2: " + str(token_v2))

            mind_page = self.client.get_block(data['url'])

            self.mind_id = mind_page.id

            self.image_tagger = ImageTagging(data, logging)

            cv = self.client.get_collection_view(self.data['url'])

            self.collection = cv.collection

            loaded = True
        except requests.exceptions.HTTPError:
            self.logging.info("Incorrect token V2 from notion")
        return loaded

    def add_url_to_database(self, url, title):
        self.logging.info("Adding url to mind: {0} {1}".format(url.encode('utf8'), title.encode('utf8')))
        self.statusCode = 200  # at start we asume everything will go ok
        try:
            rowId = self.web_clipper_request(url, title)

            thread = Thread(target=self.add_url_thread, args=(rowId,))
            thread.daemon = True  # Daemonize thread
            thread.start()  # Start the execution

            return self.create_json_response(rowId=rowId)

        except OnUrlNotValid as invalidUrl:
            self.logging.info(invalidUrl)
            self.statusCode = 500
            return self.create_json_response()
        except AttributeError as e:
            self.logging.info(e)
            print(e)
            self.statusCode = 404
            return self.create_json_response()

    def add_text_to_database(self, text, url):
        self.logging.info("Adding text to mind: {0} {1}".format(url.encode('utf8'), text.encode('utf8')))
        self.statusCode = 200  # at start we asume everything will go ok
        try:
            if url == "" or text == "":
                self.statusCode = 500
                return self.create_json_response()
            else:

                thread = Thread(target=self.add_text_thread, args=(url, text,))
                thread.daemon = True  # Daemonize thread
                thread.start()  # Start the execution

                return self.create_json_response()
        except requests.exceptions.HTTPError as invalidUrl:
            print(invalidUrl)
            self.logging.info(invalidUrl)
            self.statusCode = 500

            return self.statusCode
        except AttributeError as e:
            self.logging.info(e)
            print(e)
            self.statusCode = 404
            return self.create_json_response()

    def add_image_to_database(self, image_src, url=None, image_src_url=None):
        is_local = image_src_url is None and url is None

        if is_local:
            self.logging.info("Adding image to mind: {0}".format(image_src.encode('utf8')))
        else:
            self.logging.info("Adding image to mind: {0} {1} {2}".format(url.encode('utf8'), image_src.encode('utf8'),
                                                                         image_src_url.encode('utf8')))

        self.statusCode = 200  # at start we asume everything will go ok

        try:

            thread = Thread(target=self.add_image_thread, args=(image_src, url, image_src_url, is_local,))
            thread.daemon = True  # Daemonize thread
            thread.start()  # Start the execution

            return self.create_json_response()

        except requests.exceptions.HTTPError as invalidUrl:
            self.logging.info(invalidUrl)
            self.statusCode = 500
            return self.create_json_response()
        except AttributeError as e:
            self.logging.info(e)
            print(e)
            self.statusCode = 404
            return self.create_json_response()

    def row_callback(self, record, difference):
        if len(self.row.AITagsText) == 0:
            print("Callback from row. Here's what was changed:")
            print(difference)
            self.page_content = difference[0][-1][0][1]
            try:
                img_url = self.extract_image_from_content(self.page_content)
                try:
                    self.row.remove_callbacks(self.row_callback)
                    self.add_tags_to_row(img_url, False)
                except NoTagsFound as e:
                    print(e)
                    self.logging.info(e)
                except ValueError as e:
                    print(e)
                    self.logging.info(e)
                except Exception as e:
                    print(e)
                    self.logging.info(e)
            except OnImageNotFound as e:
                print(e)
                self.row.AITagsText = "no-tags-available"
                self.logging.info(e)
            except EmbedableContentNotFound as e:
                print(e)
                self.logging.info(e)
        else:
            print("This row is added already")

    def add_url_thread(self, rowId):
        self.logging.info("Thread adding url %s: starting", rowId)
        self.page_content = None

        self.row = self.client.get_block(rowId)
        self.row.add_callback(self.row_callback)

        while self.page_content is None:
            self.row.refresh()

        self.logging.info("Thread %s: finishing", rowId)

    def add_text_thread(self, url, text):
        row = self.collection.add_row()
        self.row = row

        self.logging.info("Add text Thread %s: starting", row.id)

        row.name = "Extract from " + url

        text_block = row.children.add_new(TextBlock)
        text_block.title = text

        row.person = self.client.current_user
        row.url = url
        self.logging.info("Add text Thread %s: finished", row.id)

    def add_image_thread(self, image_src, url=None, image_src_url=None, is_local=False):
        row = self.collection.add_row()

        self.row = row

        self.logging.info("Image add Thread %s: starting", row.id)

        img_block = row.children.add_new(ImageBlock)

        if is_local:
            img_block.upload_file(image_src)
            row.name = "Image from phone"

        else:
            img_block.source = image_src
            row.name = "Image from " + str(image_src_url)
            row.url = url

        row.icon = img_block.source
        row.person = self.client.current_user

        self.analyze_image_thread(image_src, row, is_image_local=is_local)

    def add_tags_to_row(self, img_url, is_image_local):
        self.logging.info("Adding tags to image {0}".format(img_url))
        tags = self.image_tagger.get_tags(img_url, is_image_local)
        self.logging.info("Tags from image {0} : {1}".format(img_url, tags))
        self.row.AITagsText = tags

    def extract_image_from_content(self, page_content):
        url = " "
        for element in page_content:
            im = self.client.get_block(element)
            block_type = im.get('type')
            if block_type == 'image':
                url = im.source
                break
        if url == " ":
            raise OnImageNotFound("Thumbnail Image URL not found. Value is None", self)
        else:
            print(url)
            self.logging.info(url)
        return url

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
                "blockId": "{}".format(self.mind_id),
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
            return rowId
        else:
            raise OnUrlNotValid("Invalid url was sent", self)

    def analyze_image_thread(self, image_src, row, is_image_local=False):
        try:
            self.add_tags_to_row(image_src, is_image_local)
            self.logging.info("Image tag Thread %s: finished", row.id)
        except NoTagsFound as e:
            print(e)
            self.logging.info(e)
        except ValueError as e:
            print(e)
            self.logging.info(e)
        except Exception as e:
            print(e)
            self.logging.info(e)
        except OnImageNotFound as e:
            print(e)
            self.logging.info(e)
        except EmbedableContentNotFound as e:
            print(e)
            self.logging.info(e)

    def create_json_response(self, status_code=None, rowId=None):
        url = "https://github.com/elblogbruno/NotionAI-MyMind#love-to-try-it"

        if status_code is None:
            status_code = self.statusCode

        if rowId is not None:
            rowIdExtracted = rowId.split("-")
            str1 = ''.join(str(e) for e in rowIdExtracted)
            url = "https://www.notion.so/" + str1

        text_response, status_text = get_response_text(status_code)

        x = {
            "status_code": status_code,
            "text_response": text_response,
            "status_text": status_text,
            "block_url": url
        }

        # convert into JSON:
        json_response = json.dumps(x)

        return json_response
