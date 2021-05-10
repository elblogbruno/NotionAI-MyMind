import logging

import werkzeug
from quart import Quart, render_template, flash, request, jsonify, send_file
from werkzeug.utils import secure_filename

import secrets
import sys

from NotionAI.NotionAI import *
from notion.client import NotionClient
from utils.utils import ask_server_port, save_tagging_options, save_options, save_data, createFolder, \
    save_properties_name, allowed_file, get_file_extension, is_a_sound_file
from utils.check_update import *
from NotionAI.utils import create_json_response
import tempfile

UPLOAD_FOLDER = '../app/uploads/'


dir_path = 'notion-ai-app.log'
if getattr(sys, 'frozen', False):
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'static')
    tmp = tempfile.mkdtemp()
    dir_path = os.path.join(tmp, 'notion-ai-app.log')
    app = Quart(__name__, template_folder=template_folder, static_folder=static_folder)
else:
    app = Quart(__name__)

print(dir_path)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
logging.basicConfig(filename=dir_path, filemode='w', format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# add the handler to the root logger
logging.getLogger('').addHandler(console)

notion = None


@app.route('/add_url_to_mind')
async def add_url_to_mind():
    try:
        url = request.args.get('url')
        title = request.args.get('title')
        collection_index = request.args.get('collection_index') if request.args.get('collection_index') else 0
        notion.set_mind_extension(request)
        return str(notion.add_url_to_database(url, title, int(collection_index)))
    except OnServerNotConfigured as e:
        logging.error(e)
        return str(create_json_response(notion, port=port))


@app.route('/add_text_to_mind')
async def add_text_to_mind():
    try:
        url = request.args.get('url')
        text = request.args.get('text')
        collection_index = request.args.get('collection_index') if request.args.get('collection_index') else 0
        notion.set_mind_extension(request)

        if len(request.args) > 4:
            l = request.args.to_dict()
            addition_list = list(l)[3:]
            addition = '&'.join(str(text) for text in addition_list)
            text = text + "&" + addition

        return str(notion.add_text_to_database(text, url, int(collection_index)))
    except OnServerNotConfigured as e:
        logging.error(e)
        return str(create_json_response(notion, port=port))


@app.route('/add_image_to_mind')
async def add_image_to_mind():
    try:
        url = request.args.get('url')
        image_src = request.args.get('image_src')
        image_src_url = request.args.get('image_src_url')
        collection_index = request.args.get('collection_index') if request.args.get('collection_index') else 0

        notion.set_mind_extension(request)
        return str(notion.add_image_to_database(image_src, url, image_src_url, int(collection_index)))
    except OnServerNotConfigured as e:
        logging.error(e)
        return str(create_json_response(notion, port=port))

@app.route('/add_audio_to_mind')
async def add_audio_to_mind():
    try:
        url = request.args.get('url')
        audio_src = request.args.get('audio_src')
        collection_index = request.args.get('collection_index') if request.args.get('collection_index') else 0

        notion.set_mind_extension(request)
        return str(notion.add_audio_to_database(audio_src, url, int(collection_index)))
    except OnServerNotConfigured as e:
        logging.error(e)
        return str(create_json_response(notion, port=port))

@app.route('/get_mind_structure')
async def get_mind_structure():
    try:
        return str(notion.mind_structure.get_mind_structure(notion))
    except OnServerNotConfigured as e:
        logging.error("Get mind structure " + str(e))
        return str(create_json_response(notion, port=port))
    except AttributeError as e:
        logging.error("Get mind structure attribute error " + str(e))
        return str(create_json_response(notion, error_sentence=str(e), port=port))


def toDate(dateString):
    return datetime.datetime.strptime(dateString, "%Y-%m-%d %H:%M").date()


@app.route('/set_reminder_date_to_block')
async def set_reminder_date_to_block():
    id = request.args.get("id")

    # if there is a week beetwen start and end 1 week before option appears. ({'time': '09:00', 'unit': 'week', 'value': 1})

    start = request.args.get('start', default=datetime.today(), type=toDate)
    end = request.args.get('end', default=datetime.today(), type=toDate)
    unit = request.args.get('unit', default='minute')  # if unit is minute and value is 0 it means At Time of Event
    remind_value = request.args.get('remind_value',
                                    default=0)  # it can be 5 minutes 10 15 or 30.  Aswell as 1 2 hours or 1 2 days before

    return str(
        notion.set_reminder_date_to_block(logging, id=id, start=start, end=end, unit=unit, remind_value=remind_value))


@app.route('/modify_element_by_id')
async def modify_element_by_id():
    id = request.args.get('id')
    title = request.args.get('new_title')
    url = request.args.get('new_url')
    notion.set_mind_extension(request)
    return str(notion.modify_row_by_id(id, title, url))


@app.route('/get_multi_select_tags')
async def get_multi_select_tags():
    try:
        collection_index = request.args.get('collection_index') if request.args.get('collection_index') else 0
        notion.set_mind_extension(request)
        ai_tags = notion.image_tagger.get_most_used_ai_tags(notion_ai=notion, collection_index=int(collection_index))
        return str(notion.property_manager.multi_tag_manager.get_multi_select_tags(notion,
                                                                                   append_tags=ai_tags))  # multi_select_tag_list
    except ValueError as e:
        logging.error(e)
        return str(create_json_response(notion, error_sentence=str(e), status_code=401))
    except OnServerNotConfigured as e:
        logging.error(e)
        return str(create_json_response(notion, port=port))


@app.route('/update_multi_select_tags', methods=['POST'])
async def update_multi_select_tags():
    try:
        collection_index = request.headers["collection_index"]
        id = request.headers["id"]
        tags = await request.get_json()
        notion.set_mind_extension(request)
        return str(
            notion.property_manager.multi_tag_manager.update_multi_select_tags(notion, id, tags, collection_index))
    except ValueError as e:
        logging.error(e)
        return str(create_json_response(notion, error_sentence=str(e), status_code=401))


@app.route('/upload_file', methods=['POST'])
async def upload_file():
    createFolder("uploads")
    try:
        status_code = 200
        # check if the post request has the file part
        request_files = await request.files

        collection_index = request.headers["collection_index"]

        if 'file' not in request_files:
            print('No file part')
            status_code = 400
            return str(create_json_response(notion, status_code=status_code))

        file = request_files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            print('No selected file')
            status_code = 400
            return str(create_json_response(notion, status_code=status_code))

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            uri = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            if is_a_sound_file(filename):
                return str(notion.add_audio_to_database(uri, collection_index=int(collection_index)))
            else:
                return str(notion.add_image_to_database(uri, collection_index=int(collection_index)))
        else:
            print("This file is not allowed to be post")
            status_code = 400
            return str(create_json_response(notion, status_code=status_code))
    except werkzeug.exceptions.BadRequestKeyError as e:
        logging.error(e)
        return str(create_json_response(notion, error_sentence=str(e), port=port, status_code=status_code))
    except OnServerNotConfigured as e:
        logging.error(e)
        return str(create_json_response(notion, port=port))


@app.route('/get_current_mind_url')
async def get_current_mind_url():
    try:
        return str(notion.data['url'])
    except AttributeError as e:
        logging.error("get_current_mind_url atribute error" + str(e))
        return str(create_json_response(notion, error_sentence=str(e), port=port))

@app.route('/check_update')
async def check_update_api():
    return str(check_update(logging, app.static_folder, notion, port, return_response=True))


@app.route('/log')
async def return_log_file():
    """Returns the log file of the server"""
    try:
        return await send_file(dir_path, as_attachment=True, attachment_filename='notion-ai-app.log')
    except Exception as e:
        return str(e)


@app.route('/update_notion_tokenv2')
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
                changed = notion.run()
                if changed:
                    return create_json_response(notion, status_code=2)
                else:
                    return create_json_response(notion, status_code=3)
            except requests.exceptions.HTTPError as e:
                logging.error("Incorrect token V2 from notion")
                return create_json_response(notion, error_sentence=str(e), status_code=3)


@app.route('/')
async def show_settings_home_menu():
    return await render_template("options.html")



@app.route('/handle_data', methods=['POST'])
async def handle_data():
    data = await request.get_json()

    use_clarifai = process_data(logging, data)
    process_tagging_options(logging, data, use_clarifai)
    process_properties(logging, data)

    use_email = data['email'] and data['password']

    if use_email:
        has_run = notion.run(logging, email=data['email'], password=data['password'])
    else:
        has_run = notion.run(logging)

    if has_run:
        return "200"
    else:
        return "500"


def process_data(logging, data):
    notion_url = data['notion_url']

    notion_token = data['notion_token']

    if data['clarifai_key']:
        clarifai_key = data['clarifai_key']
        save_data(logging, url=notion_url, token=notion_token, clarifai_key=clarifai_key)
        use_clarifai = True
    else:
        save_data(logging, url=notion_url, token=notion_token)
        use_clarifai = False

    save_options(logging, language_code=data['language_code'])

    return use_clarifai


def process_tagging_options(logging, data, use_clarifai):
    if "delete_after_tagging" in data:
        delete_after_tagging = data['delete_after_tagging']
    else:
        delete_after_tagging = False

    confidence_treshold = 0.10
    if "confidence_treshold" in data:
        confidence_treshold = data['confidence_treshold']

    logging.info(
        "Current Tagging Options --> Delete after Tagging:  {0} ,Confidence Treshold: {1} , Use Clarifai: {2}".format(
            delete_after_tagging, confidence_treshold, use_clarifai))

    save_tagging_options(logging, use_clarifai=use_clarifai, delete_after_tagging=delete_after_tagging,
                         confidence_treshold=confidence_treshold)


def process_properties(logging, data):
    multi_tag_property = 'Tags'
    if data['multi_tag_property']:
        multi_tag_property = data['multi_tag_property']

    mind_extension_property = 'mind_extension'
    if data['mind_extension_property']:
        mind_extension_property = data['mind_extension_property']

    ai_tags_property = 'AITagsText'
    if data['ai_tags_property']:
        ai_tags_property = data['ai_tags_property']

    notion_date_property = 'reminder'
    if data['notion_date_property']:
        notion_date_property = data['notion_date_property']

    logging.info(
        "Current properties --> Multi Tag Property:  {0} , Mind extension Property: {1} , AI Tags Property: {2}, "
        "Notion Date Reminder Property: {3}".format(
            multi_tag_property, mind_extension_property, ai_tags_property, notion_date_property))

    save_properties_name(logging, multi_tag_property=multi_tag_property,
                         mind_extension_property=mind_extension_property, ai_tags_property=ai_tags_property,
                         notion_date_property=notion_date_property)


if __name__ == "__main__":
    secret = secrets.token_urlsafe(32)
    app.secret_key = secret
    createFolder("settings")
    createFolder("uploads")
    createFolder("./image_tagging/temp_image_folder")
    check_update(logging, app.static_folder)
    port = ask_server_port(logging)
    notion = NotionAI(logging, port, app.static_folder)
    app.run(host="0.0.0.0", port=port, debug=True)
