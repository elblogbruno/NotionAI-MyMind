import os
from flask import send_from_directory
from flask import render_template
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
import json
import secrets
from NotionAI import *


UPLOAD_FOLDER = 'C:/Users/elblo/Desktop/Proyectos/NotionAI-MyMind/Python Server/app/uploads/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

notion = NotionAI()

@app.route('/add_url_to_mind')
def add_url_to_mind():
    url = request.args.get('url')
    title = request.args.get('title')
    notion.add_url_to_database(url,title)
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
    
    notion.add_image_to_database(str(url),str(image_src),str(image_src_url))
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

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            notion.add_image_to_database_by_post(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return "File Uploaded Succesfully"

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
    secret = secrets.token_urlsafe(32)
    app.secret_key = secret
    app.run(host="0.0.0.0", port=80)
