# NotionAI MyMind
![Alt Text](doc/header_gif_joined_updated.gif)

This repo uses AI and the wonderful Notion to enable you to add anything on the web to your "Mind" and forget about everything else.

## Table of Contents
- [Project Philosophy](#project-philosophy)
    - [Examples](#examples)
- [Installing](#installing)
    - [Browser Extension](#extensions)
    - [Prerequisites](#prerequisites)
    - [Love to try it?](#love-to-try-it)
        - [Docker-Compose](#docker-compose)
- [Common Issues](#common-issues)
- [Roadmap](#roadmap)

## Project Philosophy.

The idea is to have an extension on the browser, and app on android and Ios, allowing you to add whatever you find on the web in your "Mind".
Also, adding image and article tagging capabilities thanks to AI, so you can simply search on your "Mind" for what you remember.

Right now, there's a working Python Local Server, that receives all the data from the extension and the app, and publishes it to Notion. So it is 100% open source and fully private!
### Extensions
### Chromium users
https://chrome.google.com/webstore/detail/notion-ai-my-mind/eaheecglpekjjlegffodbfhbhdmnjaph?hl=es&authuser=0 the chromium browsers such as google chrome or microsoft edge can install the extension from the store!
### Firefox users
https://addons.mozilla.org/en-US/firefox/addon/notion-ai-my-mind/ firefox users can install the extension from the store!
### Android and Ios users

Users can install the android app from android store
https://play.google.com/store/apps/details?id=com.elblogbruno.notion_ai_my_mind

I won't be releasing the app on the Apple App Store, as I don't have an Apple Developer Account either Mac OS based computer.
Meanwhile, you can clone the flutter project and build the app yourself.

## Examples.

Adding text to your mind         |  Adding images to your mind |  Adding websites to your mind
:--- | :---: | ---:
![](doc/add_text.gif)  |  ![](doc/add_image.gif) |  ![](doc/add_website.gif)


## Installing

### Prerequisites

Right now there is no official way of accessing the Notion API but there is a little work-around to get your credentials.
You need to have an account on [Notion.so](https://notion.so/) and need to be logged in your browser.

### Getting your credentials

On to the chrome extension settings, you can get your needed token_v2! It is necessary for the Python server. (Hidden in the photo for obvious reasons)         |  For AI Tagging you need to create a free account at [Clarifai](https://www.clarifai.com/) and create an Application named whatever you want and get the API key.(*)
:-------------------------:|:-------------------------:
![](/doc/getting_cookie.png)  |  ![](/doc/clarifai.png)

TokenV2 is updated automatically when it changes (it occurs when you log out of notion or it expires), so Notion AI My Mind should always work. ☻ You can also change it manually of course.

*If you enter a clarifai api key, clarifai will be used. (Clarifai is cloud base, non gpu dependant, image is tagged on clarifai's servers) if you leave it blank it will use local tensorflow (will use cores of your server but image will be processed locally)

### Love to try it?

To install the python server, fire up your linux distributed machine and run this command.
```
wget https://raw.githubusercontent.com/elblogbruno/NotionAI-MyMind/master/setup.sh && sudo sh setup.sh
```
That's it.

The installation script will:
- Download the repo and install the server, then follow steps 4 to 7 down here:

Instead, you can follow the steps down here:

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
python server.py \\Python 3.5 or up needed.
```
- Step 4. Create Notion Database.
It must have this properties selected and add more properties if you want, but the selected ones must exist. (AITagsText (text) and URL (url property)) 
![Notion Screen](/doc/notion-database-howto.jpg)

- Step 5. Go to your servers IP and fill the data needed (Token, Notion Database URL and clarifai api key).

![Options Screen](/doc/options_python.png)

- Step 6. Load the extension on your chromium Browser or download from chrome or firefox [store](#extensions)

![Extension Screen](/doc/extension_howto.png)

- Step 7. Change the config of your extension to your local server IP.
![Settings Screen](/doc/settings_howto.png)

- Step 8. ENJOY!

## Docker-Compose
You can run the server on docker container. Change the [SERVER_PORT] variable with the desired port to run the server with. Then simply call `docker-compose up -d`.

```yaml
version: '3.4'

services:
  app:
    image: elblogbruno/notion-ai-mymind:latest
    ports:
      - [SERVER_PORT]:5000
```
      
When a new update is available, you can call :

```
docker-compose stop notionai-mymind
docker-compose up -d notionai-mymind
```

## Roadmap
- You can check the roadmap here: https://github.com/elblogbruno/NotionAI-MyMind/projects/1
