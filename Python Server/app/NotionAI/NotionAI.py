from notion.client import NotionClient
from notion.block import ImageBlock, TextBlock

from utils.custom_errors import OnImageNotFound, OnUrlNotValid, NoTagsFound

import os
import requests
import json
import webbrowser
import socket

from threading import Thread
from image_tagging.image_tagging import ImageTagging
from NotionAI.utils import create_json_response, web_clipper_request, extract_image_from_content, \
    get_current_extension_name


class NotionAI:
    def __init__(self, logging, port):
        self.logging = logging
        logging.info("Initiating NotionAI Class.")
        if os.path.isfile('data.json'):  # If we have a data.json with credentials, we start with these credentials
            print("Initiating with a found config file.")
            logging.info("Initiating with a found config file.")
            self.loaded = self.run(logging)
        else:  # Instead it is  the first time running the server, so we open the server url.
            self.open_browser_at_start(port)

    def open_browser_at_start(self, port):
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        final_url = "http://{0}:{1}/".format(str(local_ip), str(port))

        print("You should go to the homepage and set the credentials. The url will open in your browser now. If can't "
              "access a browser you can access {0}".format(final_url))

        self.logging.info("You should go to the homepage and set the credentials. The url will open in your browser "
                          "now. If can't access a browser you can access {0}".format(final_url))

        webbrowser.open(final_url)

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

            self.image_tagger = ImageTagging(data, logging)  # we initialize the image tagger with our data.

            cv = self.client.get_collection_view(self.data['url'])

            self.collection = cv.collection  # collection is our database or "mind" in notion

            self.counter = 0

            self.times_to_retry = 5  # if no image is found initially, it will retry this many times

            loaded = True
        except requests.exceptions.HTTPError:
            self.logging.info("Incorrect token V2 from notion")
        return loaded

    def add_url_to_database(self, url, title):
        if url is None or title is None:
            self.statusCode = 500
            return create_json_response(self)
        else:
            self.logging.info("Adding url to mind: {0} {1}".format(url.encode('utf8'), title.encode('utf8')))
            self.statusCode = 200  # at start we asume everything will go ok
            try:
                rowId = web_clipper_request(self, url, title)

                thread = Thread(target=self.add_url_thread, args=(rowId,))
                thread.daemon = True  # Daemonize thread
                thread.start()  # Start the execution

                return create_json_response(self, rowId=rowId)

            except OnUrlNotValid as invalidUrl:
                self.logging.info(invalidUrl)
                self.statusCode = 500
                return create_json_response(self)
            except AttributeError as e:
                self.logging.info(e)
                print(e)
                self.statusCode = 404
                return create_json_response(self)

    def add_text_to_database(self, text, url):
        self.logging.info("Adding text to mind: {0} {1}".format(url.encode('utf8'), text.encode('utf8')))
        self.statusCode = 200  # at start we asume everything will go ok
        try:
            if url == "" or text == "":
                self.statusCode = 500
                return create_json_response(self)
            else:
                row = self.collection.add_row()
                self.row = row

                thread = Thread(target=self.add_text_thread, args=(url, text,))
                thread.daemon = True  # Daemonize thread
                thread.start()  # Start the execution

                return create_json_response(self, rowId=row.id)
        except requests.exceptions.HTTPError as invalidUrl:
            print(invalidUrl)
            self.logging.info(invalidUrl)
            self.statusCode = 500

            return self.statusCode
        except AttributeError as e:
            self.logging.info(e)
            print(e)
            self.statusCode = 404
            return create_json_response(self)

    def add_image_to_database(self, image_src, url=None, image_src_url=None):
        is_local = image_src_url is None and url is None

        if is_local:
            self.logging.info("Adding image to mind: {0}".format(image_src.encode('utf8')))
        else:
            self.logging.info("Adding image to mind: {0} {1} {2}".format(image_src.encode('utf8'), url.encode('utf8'),
                                                                         image_src_url.encode('utf8')))
        self.statusCode = 200  # at start we asume everything will go ok

        try:
            row = self.collection.add_row()
            self.row = row

            thread = Thread(target=self.add_image_thread, args=(image_src, url, image_src_url, is_local,))
            thread.daemon = True  # Daemonize thread
            thread.start()  # Start the execution

            return create_json_response(self, rowId=row.id)

        except requests.exceptions.HTTPError as invalidUrl:
            self.logging.info(invalidUrl)
            self.statusCode = 500
            return create_json_response(self)
        except AttributeError as e:
            self.logging.info(e)
            print(e)
            self.statusCode = 404
            return create_json_response(self)

    def modify_row_by_id(self, id, title, url):
        self.statusCode = 204  # at start we asume everything will go ok
        try:
            block = self.client.get_block(id)

            if url == "" or title == "":
                self.statusCode = 500
                return create_json_response(self)
            else:
                block.title = title
                block.url = url
                return create_json_response(self)

        except OnUrlNotValid as invalidUrl:
            self.logging.info(invalidUrl)
            self.statusCode = 500
            return create_json_response(self)
        except AttributeError as e:
            self.logging.info(e)
            print(e)
            self.statusCode = 404
            return create_json_response(self)

    def row_callback(self, record, difference):
        if len(self.row.AITagsText) == 0 and len(self.row.mind_extension) == 0 and len(difference[0][-1][0][1]) != 0:
            print("Callback from row. Here's what was changed:")
            self.page_content = difference[0][-1][0][1]
            try:
                img_url_list = extract_image_from_content(self, self.page_content, record.id)
                try:
                    self.row.remove_callbacks(self.row_callback)
                    self.add_tags_to_row(img_url_list, False)
                except NoTagsFound as e:
                    print(e)
                    self.add_tags_to_row(None, False)
                    self.logging.info(e)
                except ValueError as e:
                    print(e)
                    self.add_tags_to_row(None, False)
                    self.logging.info(e)
                except Exception as e:
                    self.add_tags_to_row(None, False)
                    self.logging.info(e)
            except OnImageNotFound as e:
                print(e)
                self.add_tags_to_row(None, False)
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
        row = self.row
        self.logging.info("Add text Thread %s: starting", row.id)

        row.name = "Extract from " + url

        text_block = row.children.add_new(TextBlock)
        text_block.title = text

        row.person = self.client.current_user
        row.url = url
        self.logging.info("Add text Thread %s: finished", row.id)

    def add_image_thread(self, image_src, url=None, image_src_url=None, is_local=False):
        row = self.row
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
        self.analyze_image_thread([image_src], row, is_image_local=is_local)

    def add_tags_to_row(self, img_url_list, is_image_local):
        if img_url_list is None or len(img_url_list) == 0:
            self.logging.info("No image was found or no tags are available.")
            self.row.AITagsText = "no-tags-available"
        else:
            self.logging.info("Found {0} images.".format(len(img_url_list)))
            result = ""
            for img_url in img_url_list:
                self.logging.info("Adding tags to image {0}".format(img_url))
                tags = self.image_tagger.get_tags(img_url, is_image_local)
                self.logging.info("Tags from image {0} : {1}".format(img_url, tags))
                result = tags + "," + result
            self.row.AITagsText = result
            self.row.mind_extension = get_current_extension_name(self.request_platform)

    # sets the current platform making the request, so we know if content is added from phone or desktop
    def set_mind_extension(self, platform):
        self.request_platform = platform

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
