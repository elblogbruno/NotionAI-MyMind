from threading import Thread

import validators
from notion.block import ImageBlock, TextBlock, AudioBlock, VideoBlock
from notion.client import NotionClient
from notion.collection import NotionDate

from background_worker.background_worker import Worker
from image_tagging.image_tagging import ImageTagging
from .custom_errors import OnImageNotFound, OnUrlNotValid, OnWebClipperError
from server_utils.utils import download_audio_from_url
from translation.translation_manager import TranslationManager
from .mind_structure import *
from .property_manager.property_manager import PropertyManager
from .utils import web_clipper_request, extract_image_from_content, \
    get_current_extension_name, open_browser_at_start
from background_worker.task.remove_task import RemoveTask


class NotionAI:
    def __init__(self, logging, port, static_folder):
        self.logging = logging
        self.static_folder = static_folder
        self.port = port
        logging.info("Initiating notion_ai Class.")
        if os.path.isfile(SETTINGS_FOLDER + 'data.json'):  # If we have a data.json with credentials, we start with these credentials
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
            self.logging.info("Running notion_ai")
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
            self.translation_manager = TranslationManager(logging,
                                                          self.static_folder)  # we initialize the translation manager
            self.mind_structure = MindStructure(notion_ai=self, client=self.client, data=self.data,
                                                logging=self.logging)  # we initialize the structure of the mind manager.
            self.property_manager = PropertyManager(logging, self.client,
                                                    self.mind_structure)  # we initialize the property manager.
            self.worker = Worker(client=self.client, notion_ai=self)

            self.counter = 0

            self.times_to_retry = 5  # if no image is found initially, it will retry this many times

            self.collection_index = 0

            self.loaded = True

        except requests.exceptions.HTTPError as e:
            self.logging.info("Incorrect token V2 or email and password")
            open_browser_at_start(self, self.port)
        return self.loaded

    def add_url_to_database(self, url, title, collection_index=0, debug=True):
        if url is None:
            return create_json_response(self, status_code=500)
        else:
            if title is None:
                title = "No title found for the content"

            self.logging.info("Adding url to mind: {0} {1}".format(url.encode('utf8'), title.encode('utf8')))
            self.status_code = 200  # at start we asume everything will go ok
            try:
                rowId = "df75a7c5c874496e878d4b31951db41a"
                self.mind_structure.set_current_collection(collection_index)
                if not debug:
                    rowId = web_clipper_request(self, url, title, self.mind_structure.current_mind_id, logging=self.logging)

                    thread = Thread(target=self._add_url_thread, args=(rowId,))
                    thread.daemon = True  # Daemonize thread
                    thread.start()  # Start the execution

                return create_json_response(self, rowId=rowId)
            except OnWebClipperError as e:
                self.logging.error("Web Clipper API error while adding url: " + str(e))
                return create_json_response(self, error_sentence=str(e))
            except OnUrlNotValid as invalidUrl:
                self.logging.error("URL Not Valid error while adding url: " + str(invalidUrl))
                return create_json_response(self, status_code=400, error_sentence=str(invalidUrl))
            except AttributeError as e:
                self.logging.error("Atribute error while adding url:" + str(e))
                self.status_code = 401
                if "views" in str(e):
                    return self.add_url_to_database(url=url, title=title, collection_index=collection_index)
                else:
                    raise OnServerNotConfigured(e)
            except requests.exceptions.HTTPError as e:
                self.logging.error("HTTP Error while adding url: " + str(e))
                self.status_code = e.response.status_code

    def add_content_to_database(self, content_src, content_type, url=None, image_src_url=None, collection_index=0):
        is_local = image_src_url is None and url is None

        if url == "" or content_src == "":
            self.status_code = 500
            return create_json_response(self)

        if is_local:
            self.logging.info(
                "Adding {0} to mind: {1} {2}".format(content_type, content_src.encode('utf8'), collection_index))
        elif image_src_url:
            self.logging.info(
                "Adding {0} to mind: {1} {2} {3} {4}".format(content_type, content_src.encode('utf8'),
                                                             url.encode('utf8'), image_src_url, collection_index))
        else:
            self.logging.info(
                "Adding {0} to mind: {1} {2} {3}".format(content_type, content_src.encode('utf8'), url.encode('utf8'),
                                                         collection_index))
        if content_type == 'video':
            if "blob" in content_src:
                content_src = url

        self.status_code = 200  # at start we asume everything will go ok

        try:
            collection = self.mind_structure.set_current_collection(collection_index)
            self.row = collection.add_row()

            self.property_manager.update_properties(self.row, mind_extension_property=get_current_extension_name(
                self.request_platform))

            if is_local:
                self.row.name = "{0} from phone".format(content_type.capitalize())
            else:
                self.row.name = "{0} from {1}".format(content_type.capitalize(), str(url))
                self.row.url = url

            if content_type == 'video':
                thread = Thread(target=self._add_video_thread, args=(content_src, is_local,))
            elif content_type == 'audio':
                thread = Thread(target=self._add_audio_thread, args=(content_src, is_local,))
            elif content_type == 'image':
                thread = Thread(target=self._add_image_thread, args=(content_src, image_src_url, is_local,))
            elif content_type == 'text':
                thread = Thread(target=self._add_text_thread, args=(content_src,))

            thread.daemon = True  # Daemonize thread
            thread.start()  # Start the execution

            return create_json_response(self, rowId=self.row.id)

        except requests.exceptions.HTTPError as e:
            self.logging.info(e)
            return create_json_response(self, error_sentence=str(e), status_code=e.response.status_code)
        except AttributeError as e:
            self.logging.error(e)
            if "views" in str(e):
                return self.add_content_to_database(content_src=content_src, content_type=content_type, url=url,
                                                    image_src_url=image_src_url, collection_index=collection_index)
            else:
                return create_json_response(self, error_sentence=str(e), status_code=-1)

    def modify_row_by_id(self, id, title, url):
        self.status_code = 204  # at start we asume everything will go ok
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

        except OnUrlNotValid as e:
            self.logging.info(e)
            return create_json_response(self, status_code=e.response.status_code)
        except AttributeError as e:
            self.logging.error(e)
            self.status_code = 401
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

                    self.property_manager.update_properties(self.row,
                                                            mind_extension_property=get_current_extension_name(
                                                                self.request_platform))
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
            self.status_code = e.response.status_code
            self.logging.error(e)

    def _add_text_thread(self, text):
        try:
            row = self.row
            self.logging.info("Add text Thread %s: starting", row.id)

            text_block = row.children.add_new(TextBlock)
            text_block.title = text

            self.logging.info("Add text Thread %s: finished", row.id)
        except AttributeError as e:
            print("Add text thread: " + str(e))
            self.status_code = e.response.status_code
            self.logging.error(e)

    def _add_image_thread(self, image_src, image_src_url=None, is_local=False):
        row = self.row
        self.logging.info("Image add Thread %s: starting", row.id)

        img_block = row.children.add_new(ImageBlock)

        if is_local:
            img_block.upload_file(image_src)
        else:
            img_block.source = image_src

        if image_src_url:
            row.url = image_src_url

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

    def _add_video_thread(self, video_src, is_local=False):
        self.logging.info("Video add Thread %s: starting", self.row.id)

        video_block = self.row.children.add_new(VideoBlock)

        if is_local:
            video_block.upload_file(video_src)
        else:
            # filename = download_audio_from_url(video_src)
            video_block.source = video_src
            # video_block.upload_file(filename)

        self.logging.info("Video add Thread %s: finishing", self.row.id)

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
                self.property_manager.update_properties(self.row, ai_tags_property=tags_string)

        except AttributeError as e:
            self.logging.info("Add tags to row error: " + str(e))

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

    def set_reminder_date_to_block(self, logging, id, start=None, unit=None, remind_value=None,
                                   self_destruction=False):
        logging.info("Setting reminder date for this block {0} {1} {2} {3}".format(id, start, unit, remind_value))

        block = self.client.get_block(id)

        if remind_value and start and unit:
            block.refresh()

            reminder = {'unit': unit, 'value': remind_value}

            date = NotionDate(start=start, reminder=reminder)

            self.property_manager.update_properties(block=block, notion_date_property=date)

            if self_destruction:
                self.logging("Block with id {0} will be auto destroyed at {1}".format(id, start))
                task = RemoveTask(id, start, self.client)
                self.worker.task_manager.add_task(task)
            else:
                self.logging("Block with id {0} will be reminded at {1}".format(id, start))

            return create_json_response(self, rowId=block.id, status_code=304)
        else:
            return create_json_response(self, rowId=block.id, status_code=305)
