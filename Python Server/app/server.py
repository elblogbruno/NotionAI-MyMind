import os
import logging

from flask import send_from_directory
from flask import render_template
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename

import json
import secrets

from utils import ask_server_port, save_options, save_data
from NotionAI import *

import time
from threading import Thread


UPLOAD_FOLDER = '../app/uploads/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

notion = NotionAI(logging)


@app.route('/add_url_to_mind')
def add_url_to_mind():
    url = request.args.get('url')
    title = request.args.get('title')
    thread = Thread(target=notion.add_url_to_database, args=(url, title))
    thread.daemon = True
    thread.start()
    return "200"


@app.route('/add_text_to_mind')
def add_text_to_mind():
    url = request.args.get('url')
    text = request.args.get('text')
    thread = Thread(target=notion.add_text_to_database, args=(str(text), str(url)))
    thread.daemon = True
    thread.start()
    return "200"


@app.route('/add_image_to_mind')
def add_image_to_mind():
    url = request.args.get('url')
    image_src = request.args.get('image_src')
    image_src_url = request.args.get('image_src_url')
    thread = Thread(target=notion.add_image_to_database, args=(str(url), str(image_src), str(image_src_url)))
    thread.daemon = True
    thread.start()
    return "200"


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
            thread = Thread(target=notion.add_image_to_database_by_post, args=(os.path.join(app.config['UPLOAD_FOLDER'], filename)))
            thread.daemon = True
            thread.start()
            #notion.add_image_to_database_by_post(os.path.join(app.config['UPLOAD_FOLDER'], filename))
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


@app.route('/update_notion_tokenv2')
def update_notion_tokenv2():
    token_from_extension = request.args.get('tokenv2')
    changed = False
    with open('data.json') as json_file:
        options = json.load(json_file)

        if token_from_extension != options['token']:
            try:
                options['token'] = token_from_extension

                client = NotionClient(token_v2=options['token'])  # if can't make a client out of the token, it is not
                # a correct one.

                a_file = open("data.json", "w")
                json.dump(options, a_file)
                a_file.close()

                logging.info("Token v2 changed to {}".format(token_from_extension))
                changed = notion.run()
            except requests.exceptions.HTTPError:
                logging.info("Incorrect token V2 from notion")
    return str(changed)


@app.route('/')
def show_settings_home_menu():
    return render_template("options.html")


@app.route('/handle_data', methods=['POST'])
def handle_data():
    notion_url = request.form['notion_url']
    notion_token = request.form['notion_token']

    if request.form['clarifai_key']:
        clarifai_key = request.form['clarifai_key']
        save_data(logging, url=notion_url, token=notion_token, clarifai_key=clarifai_key)
        use_clarifai = True
    else:
        save_data(logging, url=notion_url, token=notion_token)
        use_clarifai = False

    delete_after_tagging = request.form.getlist('delete_after_tagging')

    save_options(logging, use_clarifai=use_clarifai, delete_after_tagging=delete_after_tagging)

    has_run = notion.run(logging)

    if has_run:
        return render_template("thank_you.html")
    else:
        return render_template("error.html")


if __name__ == "__main__":
    secret = secrets.token_urlsafe(32)
    app.secret_key = secret
    #port = ask_server_port(logging)
    app.run(host="0.0.0.0", port=int("5000"), debug=True)
