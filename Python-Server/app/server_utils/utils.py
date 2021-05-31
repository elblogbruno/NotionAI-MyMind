import json
import requests  # to get image from the web
import shutil  # to save it locally
import uuid
import webbrowser
import os, re

path = "/proc/self/cgroup"

DEFAULT_COLOR = "#505558"
UPLOAD_FOLDER = os.getcwd()+'/uploads/'
SETTINGS_FOLDER = os.getcwd()+'/settings/'

ALLOWED_EXTENSIONS = set(
    ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'webp', 'mp3', 'wav', 'ogg', 'mp4', 'mov', 'avi', 'm4v', '3gp'])
ALLOWED_AUDIO_EXTENSIONS = set(['mp3', 'wav', 'ogg'])
ALLOWED_VIDEO_EXTENSIONS = set(['mp4', 'mov', 'avi', 'm4v', '3gp'])


def get_path_file(filename):
    import os
    import sys
    from os import chdir
    from os.path import join
    from os.path import dirname
    from os import environ

    if hasattr(sys, '_MEIPASS'):
        # PyInstaller >= 1.6
        chdir(sys._MEIPASS)
        filename = join(sys._MEIPASS, filename)
    elif '_MEIPASS2' in environ:
        # PyInstaller < 1.6 (tested on 1.5 only)
        chdir(environ['_MEIPASS2'])
        filename = join(environ['_MEIPASS2'], filename)
    # else:
    #     chdir(dirname(sys.argv[0]))
    #     filename = join(dirname(sys.argv[0]), filename)

    return filename


def is_docker():
    if not os.path.isfile(path): return False
    with open(path) as f:
        for line in f:
            if re.match("\d+:[\w=]+:/docker(-[ce]e)?/\w+", line):
                return True
        return False


def ask_server_port(logging):
    if is_docker():
        print("running on docker")
        return int("5000")
    else:
        filename = SETTINGS_FOLDER + 'port.json'
        if os.path.isfile(filename):
            logging.info("Initiating with a found port.json file.")

            with open(filename, 'r') as json_file:
                options = json.load(json_file)
                logging.info("Using {} port".format(options['port']))
            return options['port']

        else:
            print("Asking initially for a port.")

            logging.info("Asking initially for a port.")

            port = input("Which port you'd like to run the server on: ")

            logging.info("Using {} port".format(port))

            options = {
                'port': port
            }

            with open(filename, 'w') as outfile:
                json.dump(options, outfile)

            logging.info("Port saved succesfully!")

            return options['port']


def save_tagging_options(logging, **kwargs):
    logging.info("Saving options.")

    data = {}
    for key, value in kwargs.items():
        if key == "confidence_treshold":
            data[key] = value
        elif isinstance(value, bool):
            data[key] = value
        else:
            data[key] = True if len(value) > 0 else False

    with open(SETTINGS_FOLDER + 'tagging_options.json', 'w') as outfile:
        json.dump(data, outfile)

    logging.info("Options saved succesfully!")


def save_options(logging, **kwargs):
    logging.info("Saving options.")

    data = {}
    for key, value in kwargs.items():
        data[key] = value

    with open(SETTINGS_FOLDER + 'options.json', 'w') as outfile:
        json.dump(data, outfile)

    logging.info("Options saved succesfully!")


def save_properties_name(logging, **kwargs):
    logging.info("Saving properties.")
    data = {}

    for key, value in kwargs.items():
        data[key] = value

    with open(SETTINGS_FOLDER + 'properties.json', 'w') as outfile:
        json.dump(data, outfile)

    logging.info("Properties saved succesfully!")


def save_data(logging, **kwargs):
    logging.info("Saving data.")
    data = {}

    for key, value in kwargs.items():
        data[key] = value

    with open(SETTINGS_FOLDER + 'data.json', 'w') as outfile:
        json.dump(data, outfile)

    logging.info("Data saved succesfully!")


def append_data(logging, **kwargs):
    logging.info("Appending data.")
    with open(SETTINGS_FOLDER + "data.json", "r+") as file:
        current_data = json.load(file)
        data = {}
        for key, value in kwargs.items():
            data[key] = value
        current_data.update(data)
        file.seek(0)
        json.dump(current_data, file)
    logging.info("Appending data succesfully!")


def download_audio_from_url(audio_url):
    print("Downloading this {} audio".format(audio_url))
    filename = "./uploads/" + str(uuid.uuid4())
    if 'mp3' in audio_url:
        filename = filename + ".mp3"
    elif 'wav' in audio_url:
        filename = filename + ".wav"
    elif 'ogg' in audio_url:
        filename = filename + ".ogg"

    # Open the url audio, set stream to True, this will return the stream content.
    r = requests.get(audio_url, stream=True)

    # Check if the audio was retrieved successfully
    if r.status_code == 200:
        # Set decode_content value to True, otherwise the downloaded audio file's size will be zero.
        r.raw.decode_content = True

        # Open a local file with wb ( write binary ) permission.
        with open(filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

        print('Audio sucessfully Downloaded: ', filename)
    else:
        print('Audio Couldn\'t be retreived')
    return filename


def download_image_from_url(image_url):
    filename = UPLOAD_FOLDER + str(uuid.uuid4())

    if 'png' in image_url:
        filename = filename + ".png"
    elif 'jpg' in image_url:
        filename = filename + ".jpg"
    elif 'gif' in image_url:
        filename = filename + ".gif"

    print("Downloading this {} image".format(image_url))

    # Open the url image, set stream to True, this will return the stream content.
    r = requests.get(image_url, stream=True)

    # Check if the image was retrieved successfully
    if r.status_code == 200:
        # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
        r.raw.decode_content = True

        # Open a local file with wb ( write binary ) permission.
        with open(filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

        print('Image sucessfully Downloaded: ', filename)
    else:
        print('Image Couldn\'t be retreived')
    return filename


def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print('Error: Creating directory. ' + directory)


def open_website(final_url):
    webbrowser.open(final_url)


def get_file_extension(filename):
    return filename.rsplit('.', 1)[1].lower()


def is_a_video_file(filename):
    extension = get_file_extension(filename)
    return extension in ALLOWED_VIDEO_EXTENSIONS


def is_a_sound_file(filename):
    extension = get_file_extension(filename)
    return extension in ALLOWED_AUDIO_EXTENSIONS


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
