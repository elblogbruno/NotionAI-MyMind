from flask import *
import json
import os
import argparse
from NotionAI import *

app = Flask(__name__)
notion = NotionAI()

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

@app.route('/get_current_mind_url')
def get_current_mind_url():
    return str(notion.options['url'])


@app.route('/get_notion_token_v2')
def get_notion_token_v2():
    return str(notion.options['token'])

@app.route('/')
def show_settings_home_menu():
    return render_template("index.html")

@app.route('/handle_data', methods=['POST'])
def handle_data():
    notion_url = request.form['notion_url']
    notion_token = request.form['notion_token']
    clarifai_key = request.form['clarifai_key']
    
    options = {
        'url': notion_url,
        'token': notion_token,
        'clarifai_key': clarifai_key
    }
    with open('data.json', 'w') as outfile:
        json.dump(options, outfile)
    notion.run()
    print(notion.options)
    return """
    <h1>Notion AI My Mind</h1>
    <h2>Settings were succesfully saved.</h2>
    <p>This is a lovely program created by @elblogbruno.</p>
    <code>Flask is <em>awesome</em></code>
    """

@app.route("/about")
def about():
    return """
    <h1>Notion AI My Mind</h1>
    <p>This is a lovely program created by @elblogbruno.</p>
    <code>Flask is <em>awesome</em></code>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
