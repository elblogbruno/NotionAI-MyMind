from notion.client import NotionClient
from notion.block import ImageBlock, TextBlock

import validators
import os

from custom_errors import OnImageNotFound, OnUrlNotValid, EmbedableContentNotFound, NoTagsFound

import requests
import json

import threading

from image_tagging.image_tagging import ImageTagging


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

    def run(self, logging, email_s=None, password_s=None):
        loaded = False
        data = {}
        with open('data.json') as json_file:
            data = json.load(json_file)
        try:
            self.logging = logging
            self.logging.info("Running notionAI with " + str(data))
            self.data = data

            if email_s is not None and password_s is not None:
                print("Login in with email")
                self.logging.info("Login in with email")
                self.client = NotionClient(email=email_s, password=password_s)
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
            self.add_url_thread(rowId)
        except OnUrlNotValid as invalidUrl:
            print(invalidUrl)
            self.logging.info(invalidUrl)
            self.statusCode = 500

    def add_text_to_database(self, text, url):
        self.logging.info("Adding text to mind: {0} {1}".format(url.encode('utf8'), text.encode('utf8')))
        self.statusCode = 200  # at start we asume everything will go ok
        row = self.collection.add_row()
        self.row = row
        try:
            if url == "" or text == "":
                self.statusCode = 409
            else:
                row.name = "Extract from " + url
                text_block = row.children.add_new(TextBlock)
                text_block.title = text
                row.person = self.client.current_user
                row.url = url
        except requests.exceptions.HTTPError as invalidUrl:
            print(invalidUrl)
            self.logging.info(invalidUrl)
            self.statusCode = 500

    def add_image_to_database(self, url, image_src, image_src_url):
        self.logging.info("Adding image to mind: {0} {1} {2}".format(url.encode('utf8'), image_src.encode('utf8'),
                                                                     image_src_url.encode('utf8')))
        self.statusCode = 200  # at start we asume everything will go ok
        row = self.collection.add_row()
        self.row = row
        try:
            row.name = "Image from " + image_src_url
            row.url = image_src_url
            img_block = row.children.add_new(ImageBlock)
            img_block.source = image_src
            row.icon = img_block.source
            row.person = self.client.current_user
            self.analyze_image_thread(image_src, row, image_src_url)
            # x = threading.Thread(target=self.analyze_image_thread, args=(image_src, row, image_src_url))
            # x.start()

        except requests.exceptions.HTTPError as invalidUrl:
            print(invalidUrl)
            self.logging.info(invalidUrl)
            self.statusCode = 500

    def add_image_to_database_by_post(self, image_src):
        print("The Image is " + image_src)
        self.statusCode = 200  # at start we asume everything will go ok
        row = self.collection.add_row()
        self.row = row

        try:
            row.name = "Image from " + image_src
            row.url = image_src
            img_block = row.children.add_new(ImageBlock)
            img_block.upload_file(image_src)
            row.icon = img_block.source
            row.person = self.client.current_user

            x = threading.Thread(target=self.analyze_image_thread, args=(image_src, row))
            x.start()
        except requests.exceptions.HTTPError as invalidUrl:
            print(invalidUrl)
            self.logging.info(invalidUrl)
            self.statusCode = 500

    def row_callback(self, record, difference):
        if len(self.row.AITagsText) == 0:
            print("Callback from row. Here's what was changed:")
            print(difference)
            self.page_content = difference[0][-1][0][1]
            try:
                img_url = self.extract_image_from_content(self.page_content)
                try:
                    self.row.remove_callbacks(self.row_callback)
                    self.add_tags_to_row(img_url)
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
        self.logging.info("Thread %s: starting", rowId)
        self.page_content = None

        self.row = self.client.get_block(rowId)
        self.row.add_callback(self.row_callback)

        while self.page_content is None:
            self.row.refresh()

        self.logging.info("Thread %s: finishing", rowId)

    def add_tags_to_row(self, img_url):
        self.logging.info("Adding tags to image {0}".format(img_url))
        tags = self.image_tagger.get_tags(img_url)
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

    def analyze_image_thread(self, image_src, row, image_src_url="no context"):
        try:
            self.logging.info("Image tag Thread %s: starting", row.id)
            self.add_tags_to_row(image_src)
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
