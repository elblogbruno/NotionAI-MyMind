# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.2]

### Breaking changes
- Notion API has changed. Maybe you get this error: "400 error on get_block() call",the fix is in here https://github.com/jamalex/notion-py/issues/292 but you need to modify manually the library. Meanwhile I am waiting for the library owner to update it.
- If you make a lot of request to notion API, means adding lot of content in a short amount of time, you may get now a 429 error(Too Many Requests). I may look into finding a solution or workaround to this, but it is a problem on notion's not my repo or @jamalex notion-py repo.

### Added 

- Added collections! Now you can have different collections or databases, so you can add the content to the collection you choose. More info here as you need to change your current notion setup:  https://github.com/elblogbruno/NotionAI-MyMind/wiki/Notion-AI-My-Mind-Collections

-Android app has updated to allow the new collections!

### Fixed

- Added more exceptions for error handling.
- Added notification for Notion's recent API change that limits api requests.

## [2.0.1]

### Added 

- Added function to modify a row title and url by its id, this is a base for developing ideas on #8.
- Now it looks at all images available on the content added so we can get more information and AI tag every image.
- Click to open added content works for url's, texts and images now.
- When you add content, it tracks if it was added from your phone or desktop. You need to add a new text atribute called "mind_extension". You can use this to filter by elements added from phone or desktop.
### Fixed

- Fixed error #9
- Fixed error no output provided when url or title was none adding a url.
- Fixed error when on some websites where tagged as image not found when images were found.
- Moved utils function to a util file.

## [2.0]

### Added 

- Added server as a .exe program on windows so it is easier as ever to run Notion AI My Mind in simple clicks.
- Server url is opened automatically on the browser, so you don't get lost if you don't know what the server url is.


### Fixed

- No port was returned at first run of the server.
- Refactored python directory, organized with folders.

## [1.9]

### Added 

- Faster and more reliable thanks to switching to an async based server with Quart. 
- Added json responses on server with built-in responses that would be translated to other languages. When requesting to the API, it returns the same text and status code on chrome, firefox and android/ios platforms.
- Updated app to work with these changes.
- When clicking on the message box, you can go to the url of the added content and see it.

### Fixed

- Refactored code, made it easier for example to implement in the near future a way to translate to different languages, and removed unused code.
- No message was shown when trying to add something witouth having entered credentials.

## [1.8]

### Added 

- Added initial Android and Ios App based on flutter. You can download from Play Store here: https://play.google.com/store/apps/details?id=com.elblogbruno.notion_ai_my_mind
- Disclaimer : I won't be releasing the app on the Apple App Store, as I don't have an Apple Developer Account either Mac OS based computer.

### Fixed

- Fixed server issues to be able to add images by posting, so I could add local images from phone.

## [1.7]

### Added 

- You can log in with email and password. (You need to enable a password on notion website settings.) For security, each time you reload the server you need to log in again. This is because email and password is not saved anywhere. You hear correctly.
- New revamped design and logic of the extension. Now its nicer, and shows always, even adding frome context menu. If you liked it, be careful with this update, you'll love it. 

### Fixed

- Fixed server issues adding callback capabilities. Before some websites images were not added due to timeouts.

[2.0.2]: https://github.com/elblogbruno/NotionAI-MyMind/releases/tag/2.0.2
[2.0.1]: https://github.com/elblogbruno/NotionAI-MyMind/releases/tag/2.0.1
[2.0]: https://github.com/elblogbruno/NotionAI-MyMind/releases/tag/2.0
[1.9]: https://github.com/elblogbruno/NotionAI-MyMind/releases/tag/1.9
[1.8]: https://github.com/elblogbruno/NotionAI-MyMind/releases/tag/1.8
[1.7]: https://github.com/elblogbruno/NotionAI-MyMind/releases/tag/1.7
