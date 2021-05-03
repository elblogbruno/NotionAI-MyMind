from datetime import datetime

from notion.client import NotionClient
from notion.block import ImageBlock, TextBlock, AudioBlock
from threading import Thread

from notion.collection import NotionDate
from translation.translation_manager import TranslationManager
from utils.custom_errors import OnImageNotFound, OnUrlNotValid, OnServerNotConfigured
from image_tagging.image_tagging import ImageTagging
from NotionAI.utils import create_json_response, web_clipper_request, extract_image_from_content, \
    get_current_extension_name, open_browser_at_start
from NotionAI.mind_structure import *
from NotionAI.property_manager.property_manager import PropertyManager
from utils.utils import SETTINGS_FOLDER, download_audio_from_url

import validators
import json


class NotionAI:
    def __init__(self, logging, port, static_folder):
        self.logging = logging
        self.static_folder = static_folder
        logging.info("Initiating NotionAI Class.")
        if os.path.isfile(
                SETTINGS_FOLDER + 'data.json'):  # If we have a data.json with credentials, we start with these credentials
            print("Initiating with a found config file.")
            logging.info("Initiating with a found config file.")
            self.loaded = self.run(logging)
        else:  # Instead it is  the first time running the server, so we open the server url.
            open_browser_at_start(self, port)

    def run(self, logging, email=None, password=None):
        self.loaded = False
        data = {}
        with open(SETTINGS_FOLDER + 'data.json') as json_file:
            data = json.load(json_file)
        try:
            self.logging = logging
            self.logging.info("Running NotionAI")
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

            self.image_tagger = ImageTagging(data, logging)  # we initialize the image tagger with our data.
            self.translation_manager = TranslationManager(logging, self.static_folder)  # we initialize the translation manager
            self.mind_structure = MindStructure(notion_ai=self, client=self.client, data=self.data,
                                                logging=self.logging)  # we initialize the structure of the mind manager.
            self.property_manager = PropertyManager(logging, self.client,self.mind_structure)  # we initialize the property manager.



            self.counter = 0

            self.times_to_retry = 5  # if no image is found initially, it will retry this many times

            self.collection_index = 0

            self.loaded = True

        except requests.exceptions.HTTPError as e:
            self.logging.info("Incorrect token V2 or email and password")
            raise OnServerNotConfigured(e)
        return self.loaded

    def add_url_to_database(self, url, title, collection_index=0):
        if url is None:
            self.statusCode = 500
            return create_json_response(self)
        else:
            if title is None:
                title = "No title found for the content"

            self.logging.info("Adding url to mind: {0} {1}".format(url.encode('utf8'), title.encode('utf8')))
            self.statusCode = 200  # at start we asume everything will go ok
            try:

                self.mind_structure.set_current_collection(collection_index)
                rowId = web_clipper_request(self, url, title, self.mind_structure.current_mind_id)

                thread = Thread(target=self._add_url_thread, args=(rowId,))
                thread.daemon = True  # Daemonize thread
                thread.start()  # Start the execution

                return create_json_response(self, rowId=rowId)

            except OnUrlNotValid as invalidUrl:
                self.logging.error(invalidUrl)
                print("URL Not Valid error: " + str(invalidUrl))
                self.statusCode = 500
                return create_json_response(self)
            except AttributeError as e:
                self.logging.error(e)
                print("Atribute error: " + str(e))
                self.statusCode = 404
                raise OnServerNotConfigured(e)
            except requests.exceptions.HTTPError as e:
                self.logging.error(e)
                print("Adding url: " + str(e))
                self.statusCode = 429

    def add_text_to_database(self, text, url, collection_index=0):
        self.statusCode = 200  # at start we asume everything will go ok
        try:
            if url == "" or text == "":
                self.statusCode = 500
                return create_json_response(self)
            else:
                self.logging.info("Adding text to mind: {0} {1}".format(url.encode('utf8'), text.encode('utf8')))
                self.mind_structure.set_current_collection(collection_index)

                row = self.mind_structure.collection.add_row()
                self.row = row

                row.name = "Extract from " + url
                row.url = url

                thread = Thread(target=self._add_text_thread, args=(text,))
                thread.daemon = True  # Daemonize thread
                thread.start()  # Start the execution

                return create_json_response(self, rowId=row.id)
        except requests.exceptions.HTTPError as invalidUrl:
            print(invalidUrl)
            self.logging.info(invalidUrl)
            self.statusCode = 500
            return create_json_response(self)
        except AttributeError as e:
            self.logging.error(e)
            print("Atribute error adding text: " + str(e))
            self.statusCode = 404
            raise OnServerNotConfigured(e)

    def add_image_to_database(self, image_src, url=None, image_src_url=None, collection_index=0):
        is_local = image_src_url is None and url is None

        if is_local:
            self.logging.info("Adding image to mind: {0} {1}".format(image_src.encode('utf8'),collection_index))
        else:
            self.logging.info("Adding image to mind: {0} {1} {2} {3}".format(image_src.encode('utf8'), url.encode('utf8'),
                                                                         image_src_url.encode('utf8'),collection_index))
        self.statusCode = 200  # at start we asume everything will go ok

        try:
            self.mind_structure.set_current_collection(collection_index)

            row = self.mind_structure.collection.add_row()
            self.row = row

            if is_local:
                row.name = "Image from phone"
            else:
                row.name = "Image from " + str(image_src_url)
                row.url = url

            thread = Thread(target=self._add_image_thread, args=(image_src, is_local,))
            thread.daemon = True  # Daemonize thread
            thread.start()  # Start the execution

            return create_json_response(self, rowId=row.id)

        except requests.exceptions.HTTPError as invalidUrl:
            self.logging.info(invalidUrl)
            self.statusCode = 500
            return create_json_response(self,custom_sentence=str(invalidUrl))
        except AttributeError as e:
            self.logging.info("Atribute error on image: " + str(e))
            self.statusCode = 404
            return create_json_response(self,custom_sentence=str(e))

    def add_audio_to_database(self, audio_src, url=None, collection_index=0):
        is_local = url is None

        if is_local:
            self.logging.info("Adding audio to mind: {0} {1}".format(audio_src.encode('utf8'), collection_index))
        else:
            self.logging.info(
                "Adding audio to mind: {0} {1} {2}".format(audio_src.encode('utf8'), url.encode('utf8'), collection_index))
        self.statusCode = 200  # at start we asume everything will go ok

        try:
            self.mind_structure.set_current_collection(collection_index)

            row = self.mind_structure.collection.add_row()
            self.row = row

            if is_local:
                row.name = "Audio from phone"
            else:
                row.name = "Audio from " + str(url)
                row.url = url

            thread = Thread(target=self._add_audio_thread, args=(audio_src, is_local,))
            thread.daemon = True  # Daemonize thread
            thread.start()  # Start the execution

            return create_json_response(self, rowId=row.id)

        except requests.exceptions.HTTPError as invalidUrl:
            self.logging.info(invalidUrl)
            self.statusCode = 500
            return create_json_response(self, custom_sentence=str(invalidUrl))
        except AttributeError as e:
            self.logging.error(e)
            self.statusCode = 404
            return create_json_response(self, custom_sentence=str(e))

    def modify_row_by_id(self, id, title, url):
        self.statusCode = 204  # at start we asume everything will go ok
        try:
            block = self.client.get_block(id)

            if url is None or title is None:
                return create_json_response(self, rowId=block.id, status_code=304)

            if title != "":
                block.title = title

            if url != "":
                valid = validators.url(url)
                if valid:
                    block.url = url
                else:
                    return create_json_response(self, rowId=block.id, status_code=400)

            return create_json_response(self, rowId=block.id)

        except OnUrlNotValid as invalidUrl:
            self.logging.info(invalidUrl)
            self.statusCode = 500
            return create_json_response(self)

        except AttributeError as e:
            self.logging.error(e)
            self.statusCode = 404
            raise OnServerNotConfigured(e)

    def _row_callback(self, record, difference):
        try:
            new = len(self.property_manager.get_properties(self.row, multi_tag_property=1)) == 0 and len(
                self.property_manager.get_properties(self.row, ai_tags_property=1)) == 0 and len(
                self.property_manager.get_properties(self.row, mind_extension_property=1)) == 0 and len(
                difference[0][-1][0][1]) != 0
            if new:
                print("Callback from row. Here's what was changed:")
                self.page_content = difference[0][-1][0][1]
                try:
                    self.row.remove_callbacks(self.row.id)

                    if hasattr(self, "img_url_list"):
                        self._add_tags_to_row(self.img_url_list, False)
                    else:
                        self.img_url_list = extract_image_from_content(self, self.page_content, record.id)
                        self._add_tags_to_row(self.img_url_list, False)

                except ValueError as e:
                    self._add_tags_to_row(None, False)
                    self.logging.info("Vaklue error: " + str(e))
                except Exception as e:
                    if hasattr(self, "img_url_list"):
                        self.img_url_list.pop(0)
                        self._add_tags_to_row(self.img_url_list, False)
                    else:
                        self._add_tags_to_row(None, False)
                    self.logging.info("Callback exception:" + str(e))
                except OnImageNotFound as e:
                    self._add_tags_to_row(None, False)
                    self.logging.error(e)
            else:
                self.logging.info("Thread adding url %s: finished", self.row.id)
        except AttributeError as e:
            self.logging.info("Row callback: " + str(e))

    def _add_url_thread(self, rowId):
        self.logging.info("Thread adding url %s: starting", rowId)
        self.page_content = None
        try:
            self.row = self.client.get_block(rowId)
            self.row.add_callback(self._row_callback, rowId)

            while self.page_content is None:
                self.row.refresh()

            ##self.logging.info("Thread %s: finishing", rowId)
        except requests.exceptions.HTTPError as e:
            print("Adding url thread: " + str(e))
            self.statusCode = 429
            self.logging.error(e)

    def _add_text_thread(self, text):
        try:
            row = self.row
            self.logging.info("Add text Thread %s: starting", row.id)

            text_block = row.children.add_new(TextBlock)
            text_block.title = text

            self.property_manager.update_properties(self.row, mind_extension_property=get_current_extension_name(self.request_platform))
            self.logging.info("Add text Thread %s: finished", row.id)
        except AttributeError as e:
            print("Add text thread: " + str(e))
            self.logging.error(e)

    def _add_image_thread(self, image_src, is_local=False):
        row = self.row
        self.logging.info("Image add Thread %s: starting", row.id)

        img_block = row.children.add_new(ImageBlock)

        if is_local:
            img_block.upload_file(image_src)
        else:
            img_block.source = image_src

        row.icon = img_block.source
        self._analyze_image_thread([image_src], row, is_image_local=is_local)

    def _add_audio_thread(self, audio_src, is_local=False):
        self.logging.info("Audio add Thread %s: starting", self.row.id)

        audio_block = self.row.children.add_new(AudioBlock)

        if is_local:
            audio_block.upload_file(audio_src)
        else:
            filename = download_audio_from_url(audio_src)
            audio_block.upload_file(filename)

        self.logging.info("Audio add Thread %s: finishing", self.row.id)

    def _add_tags_to_row(self, img_url_list, is_image_local):
        try:
            if img_url_list is None or len(img_url_list) == 0:
                self.logging.info("No image was found or no tags are available.")
                self.property_manager.update_properties(self.row, ai_tags_property="no-tags-available")
            else:
                self.logging.info("Found {0} images.".format(len(img_url_list)))
                result = []
                tags_string = "no-tags-available"

                for img_url in img_url_list:
                    self.logging.info("Adding tags to image {0}".format(img_url))
                    tags = self.image_tagger.get_tags(img_url, is_image_local)
                    self.logging.info("Tags from image {0} : {1}".format(img_url, tags))
                    result.append(tags)

                filtered_list = self.image_tagger.remove_duplicated_tags(result)  # removes duplicated tags
                if len(filtered_list) > 0:
                    tags_string = ",".join(filtered_list)  # converts the tags to a string

                self.logging.info("Tags from block {0}".format(tags_string))
                self.property_manager.update_properties(self.row, ai_tags_property=tags_string,
                                                        mind_extension_property=get_current_extension_name(
                                                            self.request_platform))

        except AttributeError as e:
            self.logging.info("Add tags to row: " + str(e))

    def _analyze_image_thread(self, image_src, row, is_image_local=False):
        try:
            self._add_tags_to_row(image_src, is_image_local)
            self.logging.info("Image tag Thread %s: finished", row.id)
        except ValueError as e:
            self.logging.error(e)
        except Exception as e:
            self.logging.error(e)
        except OnImageNotFound as e:
            self.logging.error(e)

    # sets the current platform making the request, so we know if content is added from phone or desktop
    def set_mind_extension(self, request):
        extension_platform_name = request.user_agent.platform
        if extension_platform_name is None:
            extension_platform_name = request.user_agent
        self.logging.info("Setting this mind extension user agent: {0}".format(str(extension_platform_name)))
        self.request_platform = str(extension_platform_name)

    def set_reminder_date_to_block(self, logging, id, start=None, end=None, unit=None, remind_value=None, self_destruction=False):
        logging.info("Setting reminder date for this block {0} {1} {2} {3} {4}".format(id,start,end,unit,remind_value))

        block = self.client.get_block(id)
        block.refresh()

        #start = datetime.strptime("2020-01-01 09:30", "%Y-%m-%d %H:%M")
        #end = datetime.strptime("2020-01-05 20:45", "%Y-%m-%d %H:%M")
        print(self.property_manager.get_properties(block,notion_date_property=1).reminder)
        if remind_value:
            reminder = {'unit': unit, 'value': remind_value}

        date = NotionDate(start=start, end=end, reminder=reminder)

        self.property_manager.update_properties(block=block,notion_date_property=date)
        return str(date.reminder)
