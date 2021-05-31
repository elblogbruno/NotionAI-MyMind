import logging
from datetime import datetime

import werkzeug
from quart import Quart, render_template, request, send_file
from werkzeug.utils import secure_filename

import secrets
import sys

from notion_ai.custom_errors import OnServerNotConfigured
from server_utils.handle_options_data import process_formulary
from notion_ai.notion_ai import *
from notion.client import NotionClient
from server_utils.utils import ask_server_port, createFolder, allowed_file, is_a_sound_file, is_a_video_file, \
    SETTINGS_FOLDER,UPLOAD_FOLDER
from server_utils.check_update import *
from notion_ai.utils import create_json_response
import tempfile

dir_path = 'notion-ai-app.log'
if getattr(sys, 'frozen', False):
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'static')
    tmp = tempfile.mkdtemp()
    dir_path = os.path.join(tmp, 'notion-ai-app.log')
    app_quart = Quart(__name__, template_folder=template_folder, static_folder=static_folder)
else:
    app_quart = Quart(__name__)

app_quart.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

logging.basicConfig(filename=dir_path, filemode='w', format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# add the handler to the root logger
logging.getLogger('').addHandler(console)
logging.info("Log file will be saved to temporary path: {0}".format(dir_path))

notion_ai = None


@app_quart.route('/add_url_to_mind')
async def add_url_to_mind():
    try:
        url = request.args.get('url')
        title = request.args.get('title')
        collection_index = request.args.get('collection_index') if request.args.get('collection_index') else 0
        notion_ai.set_mind_extension(request)
        return str(notion_ai.add_url_to_database(url, title, int(collection_index)))
    except OnServerNotConfigured as e:
        logging.error(e)
        return str(create_json_response(notion_ai, status_code=e.status_code, port=port))


@app_quart.route('/add_text_to_mind')
async def add_text_to_mind():
    try:
        url = request.args.get('url')
        text = request.args.get('text')
        collection_index = request.args.get('collection_index') if request.args.get('collection_index') else 0
        notion_ai.set_mind_extension(request)

        return str(notion_ai.add_content_to_database(content_src=text, content_type='text', url=url,
                                                     collection_index=int(collection_index)))
    except OnServerNotConfigured as e:
        logging.error(e)
        return str(create_json_response(notion_ai, status_code=e.status_code, port=port))


@app_quart.route('/add_image_to_mind')
async def add_image_to_mind():
    try:
        url = request.args.get('url')
        image_src = request.args.get('image_src')
        image_src_url = request.args.get('image_src_url')
        collection_index = request.args.get('collection_index') if request.args.get('collection_index') else 0

        notion_ai.set_mind_extension(request)

        return str(notion_ai.add_content_to_database(content_src=image_src, content_type='image', url=url,
                                                     image_src_url=image_src_url,
                                                     collection_index=int(collection_index)))
    except OnServerNotConfigured as e:
        logging.error(e)
        return str(create_json_response(notion_ai, status_code=e.status_code, port=port))


@app_quart.route('/add_audio_to_mind')
async def add_audio_to_mind():
    try:
        url = request.args.get('url')
        audio_src = request.args.get('audio_src')
        collection_index = request.args.get('collection_index') if request.args.get('collection_index') else 0

        notion_ai.set_mind_extension(request)
        return str(notion_ai.add_content_to_database(content_src=audio_src, content_type='audio', url=url,
                                                     collection_index=int(collection_index)))
    except OnServerNotConfigured as e:
        logging.error(e)
        return str(create_json_response(notion_ai, status_code=e.status_code, port=port))


@app_quart.route('/add_video_to_mind')
async def add_video_to_mind():
    try:
        url = request.args.get('url')
        video_src = request.args.get('video_src')
        collection_index = request.args.get('collection_index') if request.args.get('collection_index') else 0

        notion_ai.set_mind_extension(request)
        return str(notion_ai.add_content_to_database(content_src=video_src, content_type='video', url=url,
                                                     collection_index=int(collection_index)))
    except OnServerNotConfigured as e:
        logging.error(e)
        return str(create_json_response(notion_ai, status_code=e.status_code, port=port))


@app_quart.route('/get_mind_structure')
async def get_mind_structure():
    try:
        return str(notion_ai.mind_structure.get_mind_structure(notion_ai))
    except OnServerNotConfigured as e:
        logging.error("Get mind structure " + str(e))
        return str(create_json_response(notion_ai, port=port))
    except AttributeError as e:
        logging.error("Get mind structure attribute error " + str(e))
        return str(create_json_response(notion_ai, error_sentence=str(e), port=port))


def toDate(dateString):
    return datetime.datetime.strptime(dateString, "%Y-%m-%d %H:%M").date()


@app_quart.route('/set_reminder_date_to_block')
async def set_reminder_date_to_block():
    id = request.args.get("id")

    # if there is a week beetwen start and end 1 week before option appears. ({'time': '09:00', 'unit': 'week', 'value': 1})

    start = request.args.get('start', default=datetime.today(), type=toDate)
    end = request.args.get('end', default=datetime.today(), type=toDate)
    unit = request.args.get('unit', default='minute')  # if unit is minute and value is 0 it means At Time of Event
    remind_value = request.args.get('remind_value',
                                    default=0)  # it can be 5 minutes 10 15 or 30.  Aswell as 1 2 hours or 1 2 days before

    return str(
        notion_ai.set_reminder_date_to_block(logging, id=id, start=start, end=end, unit=unit,
                                             remind_value=remind_value))


@app_quart.route('/modify_element_by_id')
async def modify_element_by_id():
    id = request.args.get('id')
    title = request.args.get('new_title')
    url = request.args.get('new_url')
    notion_ai.set_mind_extension(request)
    return str(notion_ai.modify_row_by_id(id, title, url))


@app_quart.route('/get_multi_select_tags')
async def get_multi_select_tags():
    try:
        collection_index = request.args.get('collection_index') if request.args.get('collection_index') else 0
        notion_ai.set_mind_extension(request)
        ai_tags = notion_ai.image_tagger.get_most_used_ai_tags(notion_ai=notion_ai,
                                                               collection_index=int(collection_index))
        return str(notion_ai.property_manager.multi_tag_manager.get_multi_select_tags(notion_ai,
                                                                                      append_tags=ai_tags))  # multi_select_tag_list
    except ValueError as e:
        logging.error(e)
        return str(create_json_response(notion_ai, error_sentence=str(e), status_code=401))
    except OnServerNotConfigured as e:
        logging.error(e)
        return str(create_json_response(notion_ai, status_code=e.status_code, port=port))


@app_quart.route('/update_multi_select_tags', methods=['POST'])
async def update_multi_select_tags():
    try:
        collection_index = request.headers["collection_index"]
        id = request.headers["id"]
        tags = await request.get_json()
        notion_ai.set_mind_extension(request)
        return str(
            notion_ai.property_manager.multi_tag_manager.update_multi_select_tags(notion_ai, id, tags,
                                                                                  collection_index))
    except ValueError as e:
        logging.error(e)
        return str(create_json_response(notion_ai, error_sentence=str(e), status_code=401))


@app_quart.route('/upload_file', methods=['POST'])
async def upload_file():
    try:
        status_code = 200
        # check if the post request has the file part
        request_files = await request.files

        notion_ai.set_mind_extension(request)

        collection_index = request.headers["collection_index"]

        if 'file' not in request_files:
            print('No file part')
            status_code = 400
            return str(create_json_response(notion_ai, status_code=status_code))

        file = request_files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            print('No selected file')
            status_code = 400
            return str(create_json_response(notion_ai, status_code=status_code))

        print(file.filename)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app_quart.config['UPLOAD_FOLDER'], filename))
            uri = os.path.join(app_quart.config['UPLOAD_FOLDER'], filename)

            if is_a_sound_file(filename):
                return str(notion_ai.add_content_to_database(content_src=uri, content_type='audio', collection_index= int(collection_index)))
            elif is_a_video_file(filename):
                return str(notion_ai.add_content_to_database(content_src=uri, content_type='video', collection_index= int(collection_index)))
            else:
                return str(notion_ai.add_content_to_database(content_src=uri, content_type='image', collection_index= int(collection_index)))
        else:
            print("This file is not allowed to be post")
            status_code = 400
            return str(create_json_response(notion_ai, status_code=status_code))
    except werkzeug.exceptions.BadRequestKeyError as e:
        logging.error(e)
        return str(create_json_response(notion_ai, error_sentence=str(e), port=port, status_code=status_code))
    except OnServerNotConfigured as e:
        logging.error(e)
        return str(create_json_response(notion_ai, status_code=e.status_code, port=port))


@app_quart.route('/get_current_mind_url')
async def get_current_mind_url():
    try:
        return str(notion_ai.data['url'])
    except AttributeError as e:
        logging.error("get_current_mind_url atribute error" + str(e))
        return str(create_json_response(notion_ai, error_sentence=str(e), port=port))


@app_quart.route('/check_update')
async def check_update_api():
    return str(check_update(logging, app_quart.static_folder, notion_ai, port, return_response=True))


@app_quart.route('/log')
async def return_log_file():
    """Returns the log file of the server"""
    try:
        return await send_file(dir_path, as_attachment=True, attachment_filename='notion-ai-app.log')
    except Exception as e:
        return str(e)


@app_quart.route('/update_notion_tokenv2')
async def update_notion_tokenv2():
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
                changed = notion_ai.run()
                if changed:
                    return create_json_response(notion_ai, status_code=2)
                else:
                    return create_json_response(notion_ai, status_code=3)
            except requests.exceptions.HTTPError as e:
                logging.error("Incorrect token V2 from notion")
                return create_json_response(notion_ai, error_sentence=str(e), status_code=3)


@app_quart.route('/')
async def show_settings_home_menu():
    return await render_template("options.html")


@app_quart.route('/handle_data', methods=['POST'])
async def handle_data():
    data = await request.get_json()

    process_formulary(logging, data)

    use_email = data['email'] and data['password']

    if use_email:
        has_run = notion_ai.run(logging, email=data['email'], password=data['password'])
    else:
        has_run = notion_ai.run(logging)

    if has_run:
        return "200"
    else:
        return "500"


if __name__ == "__main__":
    secret = secrets.token_urlsafe(32)
    app_quart.secret_key = secret
    createFolder("settings")
    createFolder("uploads")
    check_update(logging, app_quart.static_folder)
    port = ask_server_port(logging)
    notion_ai = NotionAI(logging, port, app_quart.static_folder)
    app_quart.run(host="0.0.0.0", port=port, debug=True)
