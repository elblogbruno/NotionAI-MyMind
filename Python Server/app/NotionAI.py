from notion.client import NotionClient
from notion.block import ImageBlock,EmbedBlock,BookmarkBlock,VideoBlock,TweetBlock,TextBlock

import validators
import os
from utils import crawl, fix_list
from custom_errors import OnImageNotFound,OnUrlNotValid,EmbedableContentNotFound,NoTagsFound
from website_types import *
import requests
import json
from ClarifaiAI import *
from uuid import uuid1
from random import choice
from time import sleep
class NotionAI:
    def __init__(self):
        print("Init NotionAI")
        if os.path.isfile('data.json'):
            print("Initiating with a found config file.")
            options = {}
            with open('data.json') as json_file:
                options = json.load(json_file)
                
            self.client = NotionClient(token_v2=options['token'])
            mind_page = self.client.get_block(options['url'])
            self.mind_id = mind_page.id
            
            self.options = options
            self.clarifai = ClarifaiAI(options['clarifai_key'])
            
            cv = self.client.get_collection_view(self.options['url'])
            self.collection = cv.collection
            print("Running notionAI with " + str(self.options))
        else:
            print("You should go to the homepage and set the config.")
    
    def run(self):
        # Obtain the `token_v2` value by inspecting your browser cookies on a logged-in session on Notion.so
        options = {}
        with open('data.json') as json_file:
            options = json.load(json_file)
            
        self.client = NotionClient(token_v2=options['token'])
        mind_page = self.client.get_block(options['url'])
        self.mind_id = mind_page.id
        self.options = options
        self.clarifai = ClarifaiAI(options['clarifai_key'])

        cv = self.client.get_collection_view(self.options['url'])
        self.collection = cv.collection
        print("Running notionAI with " + str(self.options))
    
    def add_url_to_database(self, url,title):
        print("The url is " +url)
        
        self.statusCode = 200 #at start we asume everything will go ok
        try:  
            rowId = self.web_clipper_request(url,title)
            row = self.client.get_block(rowId)
            try:
                page_content = self.get_content_from_row(row)
                img_url = self.extract_image_from_content(page_content)
                try:
                    tags = self.clarifai.getTags(img_url)
                    print(tags)
                    row.AITagsText = tags
                    self.add_new_multi_select_value("AITags",tags)
                except NoTagsFound as e:
                    print(e)
                except ValueError as e:
                    print(e)
            except OnImageNotFound as e:
                print(e)
        except OnUrlNotValid as invalidUrl:
            print(invalidUrl)
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
        return url

    def get_content_from_row(self,row):
        row.refresh()
        content = row.get('content')
        if content is None:
            sleep(0.5)
            print("No content available yet")
            return self.get_content_from_row(row)
        else:
            return content
    
    def web_clipper_request(self,url,title):

        cookies = {
            'token_v2': self.options['token'],
        }

        headers = {
            'Content-Type': 'application/json',
        }
 
        data_t = '{"type":"block","blockId":"","property":"P#~d","items":[{"url":"https://gladysassistant.com/en/integrations/","title":"Deconstruyendo SMOOTH CRIMINAL (Michael Jackson) | ShaunTrack"}],"from":"chrome"}'

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
            response = requests.post('https://www.notion.so/api/v3/addWebClipperURLs', headers=headers, cookies=cookies, data=data)
            response_text = response.text
            json_response = json.loads(response_text)
            print(json_response)
            rowId = json_response['createdBlockIds'][0]
            return rowId
        else:
            raise OnUrlNotValid   

    # def get_embedable_from_url(self,url,row):
    #     url_embed_info = []
    #     bookmark = row.children.add_new(BookmarkBlock)
    #     try:
    #         bookmark.set_new_link(url)
    #         row.icon = bookmark.bookmark_icon
    #         url_embed_info = [bookmark.title, bookmark.description,bookmark.bookmark_icon,bookmark.bookmark_cover]
    #         print(url_embed_info)
    #         if len(url_embed_info) == 0:
    #             raise EmbedableContentNotFound("Could not embed this url and get info",self)
    #         else:
    #             if "youtube" in url:
    #                 video = row.children.add_new(VideoBlock, width=1000)
    #                 video.set_source_url(url)
    #                 print(video)
    #                 row.icon = video.display_source 
    #             elif "twitter" in url:
    #                 twitter = row.children.add_new(TweetBlock)
    #                 twitter.set_source_url(url)
    #                 row.icon = twitter.display_source 
    #     except requests.exceptions.HTTPError as invalidUrl:
    #         print(invalidUrl)
    #         self.statusCode = 500

    #     if len(url_embed_info) == 0 or url_embed_info == None:
    #         raise EmbedableContentNotFound("Could not embed this url and get info",self)
    #     else:
    #         return url_embed_info

    # def get_url_cover(self,embedable_content):
    #     is_well_formed = False
    #     if len(embedable_content) > 2:
    #         if embedable_content[3] != None:
    #             is_well_formed = validators.url(embedable_content[3])
    #             if is_well_formed:
    #                 cover_url = embedable_content[3]
    #             else:
    #                 raise OnImageUrlNotValid("Thumbnail Image URL not valid" ,self)
    #         else:
    #             raise OnImageNotFound("Thumbnail Image URL not found. Value is None" ,self)
    #     else:
    #         raise OnImageNotFound("There are no image url array on the embedable array!",self) 
    #     return cover_url   

    # def get_url_icon(self,embedable_content):
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
        cv = self.client.get_collection_view(self.options['url'])
        row = cv.collection.add_row()
        self.row = row
        try:
            #embedable_content = self.get_embedable_from_url(url,row)
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
            self.statusCode = 500
    
    def add_image_to_database(self,url, image_src,image_src_url):
        print("The Image is " + image_src + " context: "+ image_src_url)
        self.statusCode = 200 #at start we asume everything will go ok
        cv = self.client.get_collection_view(self.options['url'])
        row = cv.collection.add_row()
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
                tags = self.clarifai.getTags(image_src)
                print(tags)
                row.AITagsText = tags
                self.add_new_multi_select_value("AITags",tags)
            except NoTagsFound as e:
                print(e)
            except ValueError as e:
                print(e)
        except requests.exceptions.HTTPError as invalidUrl:
            print(invalidUrl)
            self.statusCode = 500
    def add_image_to_database_by_post(self, image_src):
        print("The Image is " + image_src)
        self.statusCode = 200 #at start we asume everything will go ok
        cv = self.client.get_collection_view(self.options['url'])
        row = cv.collection.add_row()
        self.row = row

        try:
            row.name = "Image from " + image_src
            row.url = image_src
            img_block  = row.children.add_new(ImageBlock)
            img_block.upload_file(image_src)
            row.icon = img_block.source 
            row.person = self.client.current_user
            try:
                tags = self.clarifai.getTags(img_block.source)
                print(tags)
                row.AITagsText = tags
                self.add_new_multi_select_value("AITags",tags)
            except NoTagsFound as e:
                print(e)
            except ValueError as e:
                print(e)
        except requests.exceptions.HTTPError as invalidUrl:
            print(invalidUrl)
            self.statusCode = 500