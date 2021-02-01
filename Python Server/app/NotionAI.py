from notion.client import NotionClient
from notion.block import ImageBlock, TextBlock

import validators
import os

from custom_errors import OnImageNotFound, OnUrlNotValid, EmbedableContentNotFound, NoTagsFound

import requests
import json

from uuid import uuid1
from random import choice
from time import sleep

import threading

from image_tagging.image_tagging import ImageTagging


class NotionAI:
    def __init__(self, logging):
        logging.info("Initiating NotionAI Class.")

        if os.path.isfile('data.json'):
            print("Initiating with a found config file.")
            logging.info("Initiating with a found config file.")
            self.logging = logging
            loaded = self.run(logging)
        else:
            print("You should go to the homepage and set the config.")
            logging.info("You should go to the homepage and set the config.")

    def run(self, logging):
        loaded = False
        data = {}
        with open('data.json') as json_file:
            data = json.load(json_file)
        try:
            self.logging = logging

            self.logging.info("Running notionAI with " + str(data))

            self.data = data

            self.client = NotionClient(token_v2=data['token'])

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
        self.logging("Adding url {} to mind with title {}".format(url,title))
        self.statusCode = 200  # at start we asume everything will go ok
        try:
            rowId = self.web_clipper_request(url, title)
            x = threading.Thread(target=self.add_url_thread, args=(rowId,))
            x.start()
        except OnUrlNotValid as invalidUrl:
            print(invalidUrl)
            self.logging.info(invalidUrl)
            self.statusCode = 500

    def add_url_thread(self, rowId):
        self.logging.info("Thread %s: starting", rowId)
        row = self.client.get_block(rowId)
        try:
            page_content = self.get_content_from_row(row, 0)
            img_url = self.extract_image_from_content(page_content)
            try:
                tags = self.image_tagger.get_tags(img_url)
                print(tags)
                self.logging.info(tags)
                row.AITagsText = tags
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
        self.logging.info("Thread %s: finishing", rowId)

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

    def get_content_from_row(self, row, n):
        row.refresh()
        content = row.get('content')
        if content is None and n < 15:
            sleep(0.15)
            print("No content available yet " + str(n))
            self.logging.info("No content available yet " + str(n))
            return self.get_content_from_row(row, n + 1)
        else:
            if content is None:
                raise EmbedableContentNotFound("This url had no image to tag, but was added to your mind.", self)
            else:
                return content

    def web_clipper_request(self, url, title):
        cookies = {
            'token_v2': self.data['token'],
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
            # self.logging.info(str(json_response))
            rowId = json_response['createdBlockIds'][0]
            return rowId
        else:
            raise OnUrlNotValid

    def add_text_to_database(self, text, url):
        print("The text is " + text + " context: " + url)
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
        print("The Image is " + image_src + " context: " + image_src_url)
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
            x = threading.Thread(target=self.analyze_image_thread, args=(image_src, row, image_src_url))
            x.start()

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

    def analyze_image_thread(self, image_src,row, image_src_url="no context"):
        try:
            self.logging.info("Image tag Thread %s: starting", row.id)
            tags = self.image_tagger.get_tags(image_src)
            self.logging.info("Tags from image {0} : {1}".format(image_src_url, tags))
            row.AITagsText = tags
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

