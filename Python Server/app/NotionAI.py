from notion.client import NotionClient
from notion.block import ImageBlock,EmbedBlock,BookmarkBlock,VideoBlock,TweetBlock,TextBlock

import validators

from utils import crawl, fix_list
from custom_errors import OnImageNotFound,OnImageUrlNotValid,EmbedableContentNotFound
from website_types import *
import requests

class NotionAI:
    def __init__(self):
        print("Init NotionAI")
    def run(self,options):
        # Obtain the `token_v2` value by inspecting your browser cookies on a logged-in session on Notion.so
        self.client = NotionClient(token_v2=options['token'])
        self.options = options
        print("Running notionAI with " + str(self.options))
    def add_url_to_database(self, url):
        print("The url is " +url)
        
        self.statusCode = 200 #at start we asume everything will go ok
        cv = self.client.get_collection_view(self.options['url'])
        row = cv.collection.add_row()
        self.row = row

        try:
            embedable_content = self.get_embedable_from_url(url,row)

            row.name = embedable_content[0]
            text_block = row.children.add_new(TextBlock)
            text_block.title  = embedable_content[1]
            row.person = self.client.current_user
            row.url = url
            # embed = row.children.add_new(EmbedBlock)
            # embed.set_source_url("https://learningequality.org")
            cover_url = " "
            try:
                cover_url = self.get_url_cover(embedable_content)
                img_block = row.children.add_new(ImageBlock)
                print(cover_url)
                img_block.source = cover_url
                #img_block.upload_file("C:/Users/elblo/Desktop/slide.jpg")
                row.icon = img_block.source 
                #TO-DO PROCESS IMAGE LIKE THIS AND SET TAGS
                # try:
                #     row.tags = image_processing.getTags(cover_url)
                # except NoTagsFound as e:
                #     pass
                
            except OnImageNotFound as e:
                print(e)
            except OnImageUrlNotValid as e:
                print(e)
            
            
        except EmbedableContentNotFound as e:
            print(e)
            pass
             
    def get_embedable_from_url(self,url,row):
        url_embed_info = []
        bookmark = row.children.add_new(BookmarkBlock)
        try:
            bookmark.set_new_link(url)
            row.icon = bookmark.bookmark_icon
            url_embed_info = [bookmark.title, bookmark.description,bookmark.bookmark_icon,bookmark.bookmark_cover]
            print(url_embed_info)
            if len(url_embed_info) == 0:
                raise EmbedableContentNotFound("Could not embed this url and get info",self)
            else:
                if "youtube" in url:
                    video = row.children.add_new(VideoBlock, width=1000)
                    video.set_source_url(url)
                    print(video)
                    row.icon = video.display_source 
                elif "twitter" in url:
                    twitter = row.children.add_new(TweetBlock)
                    twitter.set_source_url(url)
                    row.icon = twitter.display_source 
        except requests.exceptions.HTTPError as invalidUrl:
            print(invalidUrl)
            self.statusCode = 500

        if len(url_embed_info) == 0 or url_embed_info == None:
            raise EmbedableContentNotFound("Could not embed this url and get info",self)
        else:
            return url_embed_info

    def get_url_cover(self,embedable_content):
        is_well_formed = False
        if len(embedable_content) > 2:
            if embedable_content[3] != None:
                is_well_formed = validators.url(embedable_content[3])
                if is_well_formed:
                    cover_url = embedable_content[3]
                else:
                    raise OnImageUrlNotValid("Thumbnail Image URL not valid" ,self)
            else:
                raise OnImageNotFound("Thumbnail Image URL not found. Value is None" ,self)
        else:
            raise OnImageNotFound("There are no image url array on the embedable array!",self) 
        return cover_url   

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
        cv = self.client.get_collection_view(self.options['url'])
        row = cv.collection.add_row()
        self.row = row

        try:
            #embedable_content = self.get_embedable_from_url(url,row)
            row.name = "Extract from " + url
            text_block = row.children.add_new(TextBlock)
            text_block.title  = text
            row.person = self.client.current_user
            row.url = url
        except requests.exceptions.HTTPError as invalidUrl:
            print(invalidUrl)
            self.statusCode = 500