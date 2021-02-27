import os
import json
import requests  # to get image from the web
import shutil  # to save it locally
import uuid

import os, re

path = "/proc/self/cgroup"


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
        if os.path.isfile('port.json'):
            logging.info("Initiating with a found port.json file.")

            with open('port.json') as json_file:
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

            with open('port.json', 'w') as outfile:
                json.dump(options, outfile)

            logging.info("Port saved succesfully!")

            return options['port']


def save_options(logging, **kwargs):
    logging.info("Saving options.")

    data = {}
    for key, value in kwargs.items():
        if isinstance(value, bool):
            data[key] = value
        else:
            data[key] = True if len(value) > 0 else False

    with open('options.json', 'w') as outfile:
        json.dump(data, outfile)

    logging.info("Options saved succesfully!")


def save_data(logging, **kwargs):
    logging.info("Saving data.")
    data = {}

    for key, value in kwargs.items():
        data[key] = value

    with open('data.json', 'w') as outfile:
        json.dump(data, outfile)

    logging.info("Data saved succesfully!")


def append_data(logging, **kwargs):
    logging.info("Appending data.")
    with open("data.json", "r+") as file:
        current_data = json.load(file)
        data = {}
        for key, value in kwargs.items():
            data[key] = value
        current_data.update(data)
        file.seek(0)
        json.dump(current_data, file)
    logging.info("Appending data succesfully!")


def download_image_from_url(image_url):
    print("Downloading this {} image".format(image_url))
    filename = "./image_tagging/temp_image_folder/" + str(uuid.uuid4())

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
