# NotionAI MyMind
![Alt Text](doc/header_gif.gif)

This repo uses AI and the wonderful Notion to enable you to add anything on the web to your "Mind" and forget about everything else.


### Project Philosophy.

The idea is to have an extension on the browser, and app on android and Ios, allowing you to add whatever you find on the web in your "Mind".
Also, adding image and article tagging capabilities thanks to AI, so you can simply search on your "Mind" for what you remember.

Right now, there's a working but work in progress Python Local Server, that receives all the data from the extension and the app, and publishes it to Notion. So it is 100% open source and fully private!

### Love to try it?

- Step 1. Simply clone this repo.
```
git clone https://github.com/elblogbruno/NotionAI-MyMind
```
- Step 2. Install requirements for python server.
```
cd NotionAI-MyMind && pip -r install requirements.txt
```
- Step 3. Run the server.
```
python main.py \\Python 3.5 or up needed.
```
- Step 4. Go to your servers IP and fill the data needed.
![Options Screen](/doc/options_python.png)

- Step 5. Load the extension on your chromium Browser.
![Options Screen](/doc/extension_howto.png)

- Step 6. Change the config of your extension to your local server IP.
![Options Screen](/doc/settings_howto.png)

- Step 7. ENJOY!


# TODO
- Finish flutter Android and Ios app
- Fix extension issues
- Develop extension for Firefox
- Develop the AI tagging part.

