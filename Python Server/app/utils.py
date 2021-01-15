import os
import json


def ask_server_port(logging):
    if os.path.isfile('port.json'):
        print("Initiating with a found port.json file.")
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
            'port' : port
        }
        with open('port.json', 'w') as outfile:
            json.dump(options, outfile)
        logging.info("Port saved succesfully!")