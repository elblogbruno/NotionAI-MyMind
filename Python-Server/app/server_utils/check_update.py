import requests
from server_utils.utils import open_website,get_path_file
from notion_ai.utils import create_json_response
import configparser
from os.path import join


def replace_version(version):
    '''Replace version in file with new version'''
    config = configparser.ConfigParser()
    config.read('static/version.cfg')
    config['version']['server_version'] = version


def get_version(static_folder):
    print(static_folder)
    config = configparser.ConfigParser()
    config.read(get_path_file('static/version.cfg'))
    return config['version']['server_version']


def check_update(logging, static_folder, notion=None, port=None, return_response=False):
    api_url = "https://api.github.com/repos/elblogbruno/NotionAI-MyMind/releases/latest"
    response = requests.get(api_url)

    json_response = response.json()
    try:
        curr_version = get_version(static_folder)
        new_version = json_response['tag_name']
        print("Checking server update...")
        print("Current version {0} - New Version Found {1}".format(curr_version, new_version))
        if new_version == curr_version or curr_version > new_version:
            print("Server is up to date")
            if return_response:
                url = "https://github.com/elblogbruno/NotionAI-MyMind/releases/tag/{0}".format(curr_version)
                return create_json_response(notion, port=port, status_code=0, custom_url=url)
        else:
            print("New version available: " + new_version)
            url = "https://github.com/elblogbruno/NotionAI-MyMind/releases/tag/{0}".format(new_version)
            if return_response:
                return create_json_response(notion, port=port, status_code=1, custom_url=url)
            else:
                open_website(url)
    except KeyError as e:
        logging.error("Key error checking for update, maybe file does not exist? " + str(e))
    except requests.exceptions.HTTPError as e:
        logging.error("HTTP Error checking for update, maybe github is down or you don't have any internet?" + str(e))
