from notion.client import NotionClient
from notion.block import ImageBlock,EmbedBlock,BookmarkBlock,VideoBlock,TweetBlock,TextBlock

import validators

from flask import *
from utils import crawl, fix_list
from custom_errors import OnImageNotFound,OnImageUrlNotValid,EmbedableContentNotFound
from website_types import *
import requests
app = Flask(__name__)


class NotionAI:
    def __init__(self, config, app):
        # Obtain the `token_v2` value by inspecting your browser cookies on a logged-in session on Notion.so
        self.client = NotionClient(token_v2=config['token'])
        self.options = options
        self.statusCode = 200 #at start we asume everything will go ok
    def add_url_to_database(self, url):
        print("The url is " +url)
        

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
    
options = {
    'url': "https://www.notion.so/glassear/d4e43dbfe7244e0a83f18e14506e74ae?v=2b6755006a15418c978d5067180baae0",
    'token': "5574622b5cd318cf4107d1e088041e1c2482be80a5889c12fa8264641836e14d785d528a0cea0a82b9904251019795029dfa4e6fab65d518d7d905f9854ba2fdbed19c2df98f5d68cf918a8d9afd"
}

notion = NotionAI(options, app)


@app.route('/add_url_to_mind')
def add_url_to_mind():
    url = request.args.get('url')
    notion.add_url_to_database(url)
    print(str(notion.statusCode))
    return str(notion.statusCode)

@app.route('/add_text_to_mind')
def add_text_to_mind():
    url = request.args.get('url')
    text = request.args.get('text')
    notion.add_text_to_database(str(text),str(url))
    print(str(notion.statusCode))
    return str(notion.statusCode)

@app.route('/add_image_to_mind')
def add_image_to_mind():
    url = request.args.get('url')
    image_src = request.args.get('image_src')
    image_src_url = request.args.get('image_src_url')
    
    # notion.add_text_to_database(str(url),str(text))
    # print(str(notion.statusCode))
    return str(notion.statusCode)

@app.route('/add_video_to_mind')
def add_video_to_mind():
    url = request.args.get('url')
    video_src = request.args.get('video_src')
    video_src_url = request.args.get('video_src_url')

    # notion.add_text_to_database(str(url),str(text))
    # print(str(notion.statusCode))
    return str(notion.statusCode)

@app.route('/add_audio_to_mind')
def add_audio_to_mind():
    url = request.args.get('url')
    audio_src = request.args.get('audio_src')
    audio_src_url = request.args.get('audio_src_url')

    # notion.add_text_to_database(str(url),str(text))
    # print(str(notion.statusCode))
    return str(notion.statusCode)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
