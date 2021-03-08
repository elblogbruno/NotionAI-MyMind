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
	},
  {
		title: "Refresh collections",
		id: "naimm-collections-refresh",
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
chrome.runtime.onInstalled.addListener(function(details){
  if(details.reason == "install"){
      console.log("This is a first install!");
      openNewTab("https://github.com/elblogbruno/NotionAI-MyMind/wiki/Mind-Extension-Installation-Welcome-Page!");
  }else if(details.reason == "update"){
      var thisVersion = chrome.runtime.getManifest().version;
      console.log("Updated from " + details.previousVersion + " to " + thisVersion + "!");
      openNewTab("https://github.com/elblogbruno/NotionAI-MyMind/wiki/Extension-Changelog");
  }
});

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
  else if (menuItemId === "naimm-collections-refresh") {
		GetMindStructure();
	}
});

async function GetMindStructure() {
  let mainUrl = await getFromStorage("serverIP");
  const req = new XMLHttpRequest();
  if(!isEmpty(mainUrl)){
    const baseUrl = mainUrl;

    const urlParams = `get_mind_structure`;
    req.open("GET", baseUrl+urlParams, true);

    req.onreadystatechange = function() { // Call a function when the state changes.
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            //var jsonData = JSON.parse(this.responseText);
            // return jsonData;
            browser.storage.local.set({ "struct" : this.responseText }, function() {
              if (browser.runtime.error) {
                console.log("Runtime error.");
              }
              console.log("Succesfully saved data");
            });
        } else if (this.status === 0) {
            switchResponse("-1");
        }
    }
    req.send();
  }else{
    switchResponse("-1");
  }
}

async function AddUrlToMind(tab) {
  let mainUrl = await getFromStorage("serverIP");
  
  if(!isEmpty(mainUrl)){
    const baseUrl = mainUrl;
    let struct = await getFromStorage("struct");
    
    createCollectionHandler(
      () =>
        showCollectionPopup(String(struct) , (result) => addUrlRequest(tab,baseUrl,result))
    );

  }else{
    switchResponse("-1");
  }
}
async function addUrlRequest(tab,baseUrl,collection_index)
{
    const req = new XMLHttpRequest();
    var url = tab.url;
    var title = tab.title;
    const urlParams = `add_url_to_mind?url=${url}&title=${title}&collection_index=${collection_index}`;
    req.open("GET", baseUrl+urlParams, true);
    req.onreadystatechange = function() { // Call a function when the state changes.
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            parseAndSwitchResponse(this.responseText);
        } else if (this.status === 0) {
            switchResponse("-1");
        }
    }
    req.send();
}

//Adds text to mind
async function AddTextToMind(info,tab) {
  let mainUrl = await getFromStorage("serverIP");
  if(!isEmpty(mainUrl)){
    const baseUrl = mainUrl;
    
    let struct = await getFromStorage("struct");
    
    createCollectionHandler(
      () =>
        showCollectionPopup(String(struct) , (result) => addTextRequest(info,tab,baseUrl,result))
    );

  }else{
    switchResponse("-1");
  }
}
async function addTextRequest(info,tab,baseUrl,collection_index){
  const req = new XMLHttpRequest();
  
  var text = info.selectionText;
  var url = tab.url;
  urlParams = `add_text_to_mind?url=${url}&collection_index=${collection_index}&text=${text}`;

  req.open("GET", baseUrl+urlParams, true);
  req.onreadystatechange = function() { // Call a function when the state changes.
      if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
          parseAndSwitchResponse(this.responseText);
      } else if (this.status === 0) {
          switchResponse("-1");
      }
  }
  req.send();
}

async function ProcessSelection(info,tab) {
  let mainUrl = await getFromStorage("serverIP");
  if(!isEmpty(mainUrl)){
      const baseUrl = mainUrl;

      let struct = await getFromStorage("struct");
    
      createCollectionHandler(
        () =>
          showCollectionPopup(String(struct) , (result) => addSelectionToMind(info,baseUrl,result))
      );
      
      
  }else{
    switchResponse("-1");
  }
}
async function addSelectionToMind(info,baseUrl,collection_index){
    const req = new XMLHttpRequest();
  
    var urlParams = "";

    var url = info["linkUrl"];
    switch (info["mediaType"]) {
      case 'image':
        var src = info["srcUrl"];
        var image_src_url =  info["pageUrl"];
        urlParams = `add_image_to_mind?collection_index=${collection_index}&url=${url}&image_src=${src}&image_src_url=${image_src_url}`;
        break;
      case 'video':
        var src = info["srcUrl"];
        var video_src_url =  info["pageUrl"];
        urlParams = `add_video_to_mind?collection_index=${collection_index}&url=${url}&video_src=${src}&video_src_url=${video_src_url}`;
        break;
      case 'audio':
        var src = info["srcUrl"];
        var image_src_url =  info["pageUrl"];
        urlParams = `add_audio_to_mind?collection_index=${collection_index}&url=${url}&audio_src=${src}&audio_src_url=${audio_src_url}`;
        break;
      default:
        break;
    }
    req.open("GET", baseUrl+urlParams, true);
    req.send();

    req.onreadystatechange = function() { // Call a function when the state changes.
      if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
          parseAndSwitchResponse(this.responseText);
      } else if (this.status === 0) {
          switchResponse("-1");
      }
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
          redirect: "https://github.com/elblogbruno/NotionAI-MyMind/wiki/Common-Issues",
        })
    );
  }
  else if (status_code == '-2'){
    createHandler(
      () =>
        showNotification({
          message: "Succesfully refreshed available collections.",
          status: "success",
          redirect: "https://github.com/elblogbruno/NotionAI-MyMind/wiki/Common-Issues",
        })
    );
  }
  else{
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



browser.cookies.onChanged.addListener(function(info) 
{
  if(info['cookie']['domain'] == ".notion.so" && info['cookie']['name']  == "token_v2")
  {
      browser.storage.local.get("serverIP", function(items) {
        if (!browser.runtime.error) {
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

browser.runtime.onMessage.addListener(function(request, sender) {
  if(Number.isInteger(request.index)){
    //alert(request.index);
  }else{
    openNewTab(request.redirect);
  }
});
// undefined
function createCollectionHandler(callback) {
  browser.tabs.insertCSS({
    file: "css/collection.css",
  });

  const config = { file: "js/collectionPopupCreate.js" };

  if (usePromise) {
    browser.tabs.executeScript(config).then(callback);
  } else {
    chrome.tabs.executeScript(config, callback);
  }
}
//We have a callback here from when user chooses a collection index, so we call the function that makes a request to the api with the index.
function showCollectionPopup(structure,callback_from_caller) {
  props = {
    structure,
	}

	function callback() {
    browser.tabs.executeScript({file: 'js/collectionPopupBehaviour.js'},
    function (result) {
      browser.runtime.onMessage.addListener(function(request, sender, sendResponse) {
        if (request.action === 'done') {
            console.log(request.result);
            sendResponse({ action: 'next', arg: 2 });
            callback_from_caller(request.result);
            browser.runtime.onMessage.removeListener(arguments.callee);
        }
        // uncomment this if code is also asynchronous
        return true;
      });
      
    }
    );
	};

	const config = {
		code: `
			window.caimm = {};
			${Object.entries(props).map(([key, value]) => `window.caimm.${key} = ${value};`).join('')}
		`
	};

	if (usePromise) {
		browser.tabs.executeScript(config).then(callback);
	} else {
		chrome.tabs.executeScript(config, callback);
	}
}

// undefined
function createHandler(callback) {
    browser.tabs.insertCSS({
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
		icon: browser.runtime.getURL(`icon/${icon}`),
		message,
		status,
		redirect,
	}

	function callback() {
		browser.tabs.executeScript({ file: "js/notificationBehaviour.js" });
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
		browser.tabs.create({ url });
	}
}

function saveSelection(extraData,tab) {
	const config = { file: "utils/get-selection.js" };
	browser.tabs.executeScript(config, function(data) {
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
    return new Promise((resolve, reject) => {
      browser.storage.local.get(key, resolve);
    })
      .then(result => {
          if (key == null) return result;
          else return result[key];
      });
}
