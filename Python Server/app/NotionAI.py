from notion.client import NotionClient
from notion.block import ImageBlock,EmbedBlock,BookmarkBlock,VideoBlock,TweetBlock,TextBlock

import validators
import os

from utils import crawl, fix_list
from custom_errors import OnImageNotFound,OnUrlNotValid,EmbedableContentNotFound,NoTagsFound,OnTokenV2NotValid
from website_types import *

import requests
import json

from ClarifaiAI import *
from uuid import uuid1
from random import choice
from time import sleep

class NotionAI:
    def __init__(self,logging):
        print("Init NotionAI")
        if os.path.isfile('data.json'):
            print("Initiating with a found config file.")
            logging.info("Initiating with a found config file.")
            self.logging = logging
            loaded = self.run()
        else:
            print("You should go to the homepage and set the config.")
            logging.info("You should go to the homepage and set the config.")
    
    def run(self):
        # Obtain the `token_v2` value by inspecting your browser cookies on a logged-in session on Notion.so
        loaded = False
        options = {}
        with open('data.json') as json_file:
            options = json.load(json_file)
        try:
            self.client = NotionClient(token_v2=options['token'])
            mind_page = self.client.get_block(options['url'])
            self.mind_id = mind_page.id
            
            self.options = options
            self.clarifai = ClarifaiAI(options['clarifai_key'])
            
            cv = self.client.get_collection_view(self.options['url'])

            self.collection = cv.collection
            print("Running notionAI with " + str(self.options))
            self.logging.info("Running notionAI with " + str(self.options))
            loaded = True
        except requests.exceptions.HTTPError:
            print("Incorrect token V2 from notion")
            self.logging.info("Incorrect token V2 from notion")
        return loaded
    
    def add_url_to_database(self, url,title):
        print("The url is " +url)
        
        self.statusCode = 200 #at start we asume everything will go ok
        try:  
            rowId = self.web_clipper_request(url,title)
            row = self.client.get_block(rowId)
            try:
                page_content = self.get_content_from_row(row,0)
                img_url = self.extract_image_from_content(page_content)
                try:
                    tags = self.clarifai.get_tags(img_url)
                    print(tags)
                    self.logging.info(tags)
                    row.AITagsText = tags
                    self.add_new_multi_select_value("AITags",tags)
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
        except OnUrlNotValid as invalidUrl:
            print(invalidUrl)
            self.logging.info(invalidUrl)
            self.statusCode = 500

    def add_new_multi_select_value(self,prop, value, color=None):
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

        collection_schema = self.collection.get("schema")
        prop_schema = next(
            (v for k, v in collection_schema.items() if v["name"] == prop), None
        )
        if not prop_schema:
            raise ValueError(
                '{} property does not exist on the collection!'.format(prop)
            )
        if prop_schema["type"] != "multi_select":
            raise ValueError('{} is not a multi select property!'.format(prop))
        
        if "options" not in prop_schema: 
            prop_schema["options"] = []
        
        dupe = next(
            (o for o in prop_schema["options"] if o["value"] == value), None
        )
        if dupe:
            raise ValueError(f'"{value}" already exists in the schema!')

        prop_schema["options"].append(
            {"id": str(uuid1()), "value": value, "color": color}
        )
        self.collection.set("schema", collection_schema)         
    
    def extract_image_from_content(self,page_content):
        url = " "
        for element in page_content:
            im = self.client.get_block(element)
            block_type = im.get('type')
            if block_type == 'image':
                url = im.source
                break
        if url == " ":
            raise OnImageNotFound("Thumbnail Image URL not found. Value is None" ,self)
        else:
            print(url)
            self.logging.info(url)
        return url

    def get_content_from_row(self,row,n):
        row.refresh()
        content = row.get('content')
        if content is None and n < 15:
            sleep(0.25)
            print("No content available yet " +str(n))
            self.logging.info("No content available yet " +str(n))
            return self.get_content_from_row(row,n+1)
        else:
            if content is None:
                raise EmbedableContentNotFound("This url had no image to tag, but was added to your mind.",self)
            else:
                return content
    
    def web_clipper_request(self,url,title):

        cookies = {
            'token_v2': self.options['token'],
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
                "from" : "chrome"
            } 
            data = json.dumps(data_dict)

            print (data)
            self.logging.info(data)
            response = requests.post('https://www.notion.so/api/v3/addWebClipperURLs', headers=headers, cookies=cookies, data=data)
            response_text = response.text
            json_response = json.loads(response_text)
            print(json_response)
            self.logging.info(json_response)
            rowId = json_response['createdBlockIds'][0]
            return rowId
        else:
            raise OnUrlNotValid   

    def get_url_icon(self,embedable_content):
        is_well_formed = False
        if len(embedable_content) > 2:
            is_well_formed = validators.url(embedable_content[2])
            if is_well_formed:
                icon_url = embedable_content[2]
            else:
                raise OnImageUrlNotValid
        else:
            raise OnImageNotFound 
        return icon_url   
            
    def add_text_to_database(self, text,url):
        print("The text is " + text + " context: "+ url)
        self.statusCode = 200 #at start we asume everything will go ok
        row = self.collection.add_row()
        self.row = row
        try:
            if url == "" or text == "":
                self.statusCode = 409
            else:
                row.name = "Extract from " + url
                text_block = row.children.add_new(TextBlock)
                text_block.title  = text
                row.person = self.client.current_user
                row.url = url
        except requests.exceptions.HTTPError as invalidUrl:
            print(invalidUrl)
            self.logging.info(invalidUrl)
            self.statusCode = 500
    
    def add_image_to_database(self,url, image_src,image_src_url):
        print("The Image is " + image_src + " context: "+ image_src_url)
        self.statusCode = 200 #at start we asume everything will go ok
        #cv = self.client.get_collection_view(self.options['url'])
        row = self.collection.add_row()
        self.row = row

        try:
            row.name = "Image from " + image_src_url
            row.url = image_src_url
            img_block  = row.children.add_new(ImageBlock)
            img_block.source = image_src
            #img_block.upload_file("C:/Users/elblo/Desktop/slide.jpg")
            row.icon = img_block.source 
            row.person = self.client.current_user
            try:
                tags = self.clarifai.get_tags(image_src)
                print(tags)
                self.logging.info(tags)
                row.AITagsText = tags
                self.add_new_multi_select_value("AITags",tags)
            except NoTagsFound as e:
                print(e)
                self.logging.info(e)
            except ValueError as e:
                print(e)
                self.logging.info(e)
            except Exception as e:
                print(e)
                self.logging.info(e)
        except requests.exceptions.HTTPError as invalidUrl:
            print(invalidUrl)
            self.logging.info(invalidUrl)
            self.statusCode = 500
    
    def add_image_to_database_by_post(self, image_src):
        print("The Image is " + image_src)
        self.statusCode = 200 #at start we asume everything will go ok
        #cv = self.client.get_collection_view(self.options['url'])
        row = self.collection.add_row()
        self.row = row

        try:
            row.name = "Image from " + image_src
            row.url = image_src
            img_block  = row.children.add_new(ImageBlock)
            img_block.upload_file(image_src)
            row.icon = img_block.source 
            row.person = self.client.current_user
            try:
                tags = self.clarifai.get_tags(img_block.source)
                print(tags)
                row.AITagsText = tags
                self.add_new_multi_select_value("AITags",tags)
            except NoTagsFound as e:
                print(e)
                self.logging.info(e)
            except ValueError as e:
                print(e)
                self.logging.info(e)
            except Exception as e:
                print(e)
                self.logging.info(e)
        except requests.exceptions.HTTPError as invalidUrl:
            print(invalidUrl)
            self.logging.info(invalidUrl)
            self.statusCode = 500