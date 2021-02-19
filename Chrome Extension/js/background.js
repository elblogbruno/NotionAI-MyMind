const usePromise = typeof browser !== "undefined";

const menuConfig = [
	{
		title: "Add to my mind: %s",
		id: "naimm-add",
		contexts: [ "selection", "image", "video", "audio" ]
	},
	{
		title: "Open my mind",
		id: "naimm-open-mind",
		contexts: [ "browser_action" ]
	},
  {
		title: "Open server",
		id: "naimm-open",
		contexts: [ "browser_action" ]
	}
];

if (usePromise) {
	browser.contextMenus.removeAll().then(() => {
		menuConfig.forEach(config => browser.contextMenus.create(config));
	});
} else {
	chrome.contextMenus.removeAll(() => {
		menuConfig.forEach(config => chrome.contextMenus.create(config));
	});
}


/**
 * Observers
 */

// Browser Action
chrome.browserAction.onClicked.addListener((tab) => {
  AddUrlToMind(tab);
});

// Context Menu
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
	const { menuItemId, linkUrl, selectionText, pageUrl } = info;

	if (menuItemId === "naimm-add") {
		if (selectionText && !linkUrl) {
			// Used to support multi-line selections
			saveSelection({pageUrl},tab);
		} else {
			ProcessSelection(info,tab);
		}
	}
	else if (menuItemId === "naimm-open") {
		openServer();
	}
  else if (menuItemId === "naimm-open-mind") {
		openMindUrl();
	}
});

async function AddUrlToMind(tab) {
  let mainUrl = await getFromStorage("serverIP");
  const req = new XMLHttpRequest();
  if(!isEmpty(mainUrl)){
    const baseUrl = mainUrl;

    var url = tab.url;
    var title = tab.title;
    const urlParams = `add_url_to_mind?url=${url}&title=${title}`;
    req.open("GET", baseUrl+urlParams, true);

    req.onreadystatechange = function() { // Call a function when the state changes.
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            parseAndSwitchResponse(this.responseText);
        } else if (this.status === 0) {
            switchResponse("-1");
        }
    }
    req.send();
  }else{
    switchResponse("-1");
  }
}

async function AddTextToMind(info,tab) {
  let mainUrl = await getFromStorage("serverIP");
  const req = new XMLHttpRequest();
  if(!isEmpty(mainUrl)){
    const baseUrl = mainUrl;

    var text = info.selectionText;
    var url = tab.url;
    urlParams = `add_text_to_mind?url=${url}&text=${text}`;

    req.open("GET", baseUrl+urlParams, true);

    req.onreadystatechange = function() { // Call a function when the state changes.
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            parseAndSwitchResponse(this.responseText);
        } else if (this.status === 0) {
            switchResponse("-1");
        }
    }
    req.send();
  }else{
    switchResponse("-1");
  }
}

async function ProcessSelection(info,tab) {
  let mainUrl = await getFromStorage("serverIP");
  const req = new XMLHttpRequest();
  if(!isEmpty(mainUrl)){
      const baseUrl = mainUrl;
      var urlParams = "";

      var url = info["linkUrl"];
      switch (info["mediaType"]) {
        case 'image':
          var src = info["srcUrl"];
          var image_src_url =  info["pageUrl"];
          urlParams = `add_image_to_mind?url=${url}&image_src=${src}&image_src_url=${image_src_url}`;
          break;
        case 'video':
          var src = info["srcUrl"];
          var video_src_url =  info["pageUrl"];
          urlParams = `add_video_to_mind?url=${url}&video_src=${src}&video_src_url=${video_src_url}`;
          break;
        case 'audio':
          var src = info["srcUrl"];
          var image_src_url =  info["pageUrl"];
          urlParams = `add_audio_to_mind?url=${url}&audio_src=${src}&audio_src_url=${audio_src_url}`;
          break;
        default:
          break;
      }
      alert(baseUrl+urlParams);
      req.open("GET", baseUrl+urlParams, true);
      req.send();
  
      req.onreadystatechange = function() { // Call a function when the state changes.
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            parseAndSwitchResponse(this.responseText);
        } else if (this.status === 0) {
            switchResponse("-1");
        }
      }
  }else{
    switchResponse("-1");
  }
}

function parseAndSwitchResponse(response_from_api){
  var myObj = JSON.parse(response_from_api);  
  switchResponse(String(myObj['status_code']), String(myObj['block_url']),String(myObj['status_text']),String(myObj['text_response']));
}

function switchResponse(status_code,block_url,status_text,text_response)
{
  if (status_code == '-1'){
    createHandler(
      () =>
        showNotification({
          message: "Error during accessing server. Make sure the ip/port are corrects, and the server is running.",
          status: "error",
          redirect: "https://github.com/elblogbruno/NotionAI-MyMind#love-to-try-it",
        })
    );
  }else{
    createHandler(
      () =>
        showNotification({
          message: text_response,
          status: status_text,
          redirect: block_url,
        })
    );
  }
}


chrome.cookies.onChanged.addListener(function(info) 
{
  if(info['cookie']['domain'] == ".notion.so" && info['cookie']['name']  == "token_v2")
  {
      chrome.storage.sync.get("serverIP", function(items) {
        if (!chrome.runtime.error) {
          ip = items["serverIP"];
          console.log(ip);
          const baseUrl = ip;
      
          var value = info['cookie']['value'];
          const urlParams = `update_notion_tokenv2?tokenv2=${value}`;
      
          req.open("GET", baseUrl+urlParams, true);

          req.onreadystatechange = function() { // Call a function when the state changes.
              if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
                  console.log("Got response 200!");
              }
          }

          req.send();
        }
      });
  }
});

chrome.runtime.onMessage.addListener(function(request, sender) {
    openNewTab(request.redirect);
});

// undefined
function createHandler(callback) {
    chrome.tabs.insertCSS({
      file: "css/notification.css",
    });

    const config = { file: "js/notificationCreate.js" };

    if (usePromise) {
      browser.tabs.executeScript(config).then(callback);
    } else {
      chrome.tabs.executeScript(config, callback);
    }
}

function showNotification({ status, message, redirect, icon = 'icon.png' }) {
	const props = {
		icon: chrome.runtime.getURL(`icon/${icon}`),
		message,
		status,
		redirect,
	}

	function callback() {
		chrome.tabs.executeScript({ file: "js/notificationBehaviour.js" });
	};

	const config = {
		code: `
			window.naimm = {};
			${Object.entries(props).map(([key, value]) => `window.naimm.${key} = "${value}";`).join('')}
		`
	};

	if (usePromise) {
		browser.tabs.executeScript(config).then(callback);
	} else {
		chrome.tabs.executeScript(config, callback);
	}
}

function openNewTab(url) {
	if (url) {
		chrome.tabs.create({ url });
	}
}

function saveSelection(extraData,tab) {
	const config = { file: "utils/get-selection.js" };
	chrome.tabs.executeScript(config, function(data) {
		let result = Object.assign(data[0], extraData);

		if (!result.selectionText) {
			return;
		};
		AddTextToMind(result,tab);
	});
}

function isEmpty(str) {
  return (!str || 0 === str.length);
}

async function GetMindUrl(){
  const req = new XMLHttpRequest();
  // var mainUrl = getServerUrl();
  let permission = await getFromStorage("serverIP");
  if(!isEmpty(permission)){
    const baseUrl = permission;
    const urlParams = `get_current_mind_url`;

    req.open("GET", baseUrl+urlParams, true);

    req.onreadystatechange = function() { // Call a function when the state changes.
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            return this.responseText;
        }
    }
    req.send();
  }
}

async function openMindUrl(){
  const req = new XMLHttpRequest();
  // var mainUrl = getServerUrl();
  let permission = await getFromStorage("serverIP");
  if(!isEmpty(permission)){
    const baseUrl = permission;
    const urlParams = `get_current_mind_url`;

    req.open("GET", baseUrl+urlParams, true);

    req.onreadystatechange = function() { // Call a function when the state changes.
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            openNewTab(this.responseText);
        } else if (this.readyState === XMLHttpRequest.DONE && this.status === 0) {
            switchResponse("-1");
        }
    }
    req.send();
  }else{
    switchResponse("-1");
  }
}

async function openServer(){
  let mainUrl = await getFromStorage("serverIP");
  if(!isEmpty(mainUrl)){
    openNewTab(mainUrl);
  }else{
    switchResponse("-1");
  }
}

async function getFromStorage(key) {
  if(usePromise){
    return new Promise((resolve, reject) => {
      browser.storage.sync.get(key, resolve);
    })
      .then(result => {
          if (key == null) return result;
          else return result[key];
      });
  }else{
    return new Promise((resolve, reject) => {
      chrome.storage.sync.get(key, resolve);
    })
      .then(result => {
          if (key == null) return result;
          else return result[key];
      });
  }
  
}
