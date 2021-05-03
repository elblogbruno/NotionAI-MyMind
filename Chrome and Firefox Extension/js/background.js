const usePromise = typeof browser !== "undefined";
const defaultTimeout = 6000;
var menuConfig = null;

if (usePromise){
  menuConfig = [
    {
      title: `${browser.i18n.getMessage("add_text")}: %s`,
      id: "naimm-add",
      contexts: [ "selection", "image", "video", "audio" ]
    },
    {
      title: browser.i18n.getMessage("open_mind"),
      id: "naimm-open-mind",
      contexts: [ "browser_action" ]
    },
    {
      title: browser.i18n.getMessage("open_server"),
      id: "naimm-open",
      contexts: [ "browser_action" ]
    },
    {
      title: browser.i18n.getMessage("refresh"),
      id: "naimm-collections-refresh",
      contexts: [ "browser_action" ]
    }
  ];
}else{
  menuConfig = [
    {
      title: `${chrome.i18n.getMessage("add_text")}: %s`,
      id: "naimm-add",
      contexts: [ "selection", "image", "video", "audio" ]
    },
    {
      title: chrome.i18n.getMessage("open_mind"),
      id: "naimm-open-mind",
      contexts: [ "browser_action" ]
    },
    {
      title: chrome.i18n.getMessage("open_server"),
      id: "naimm-open",
      contexts: [ "browser_action" ]
    },
    {
      title: chrome.i18n.getMessage("refresh"),
      id: "naimm-collections-refresh",
      contexts: [ "browser_action" ]
    }
  ];
}


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
chrome.runtime.onStartup.addListener(function() {
  check_for_update();
})

chrome.runtime.onInstalled.addListener(function(details){
  if(details.reason == "install"){
      console.log("This is a first install!");
      
      if(usePromise)
      {
        browser.runtime.openOptionsPage();
      }else{
        chrome.runtime.openOptionsPage();
      }
      
      openNewTab("https://github.com/elblogbruno/NotionAI-MyMind/wiki/Mind-Extension-Installation-Welcome-Page!");
     
  }else if(details.reason == "update"){
      var thisVersion = chrome.runtime.getManifest().version;
      console.log("Updated from " + details.previousVersion + " to " + thisVersion + "!");
      check_for_update();
      openNewTab("https://github.com/elblogbruno/NotionAI-MyMind/wiki/Extension-Changelog");
  }
});
// //when browser loads it gets the mind structure. Currently deprecated as it makes a lot of request to notion api.
// chrome.webNavigation.onCompleted.addListener(function(details) {
//   GetMindStructure();
// });

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

async function check_for_update()
{
  const urlParams = `check_update`;
  ApiRequest(urlParams,false,10000);
}

async function GetMindStructure(sendResponse = null) {
  const urlParams = `get_mind_structure`;
  ApiRequest(urlParams,false,2000,2000,sendResponse,save_name= "mind_structure")
}

async function AddUrlToMind(tab) {
  let struct = await getFromStorage("mind_structure");
  var url = tab.url;
  var title = tab.title;
  //const urlParams = `add_url_to_mind?url=${url}&title=${title}&collection_index=${collection_index}`;
  createCollectionHandler(
      () =>
        showCollectionPopup(String(struct) , (result) => ApiRequest(`add_url_to_mind?url=${url}&title=${title}&collection_index=${result}`))
    );
}
//Adds text to mind
async function AddTextToMind(info,tab) {
  var text = info.selectionText;
  var url = tab.url;
  //urlParams = `add_text_to_mind?url=${url}&collection_index=${collection_index}&text=${text}`;

  let struct = await getFromStorage("mind_structure");
  createCollectionHandler(
        () =>
          showCollectionPopup(String(struct) , (result) => ApiRequest(`add_text_to_mind?url=${url}&collection_index=${result}&text=${text}`))
      );
}

async function ProcessSelection(info,tab) {
  let struct = await getFromStorage("mind_structure");
  createCollectionHandler(
        () =>
          showCollectionPopup(String(struct) , (result) => addSelectionToMind(info,result))
      );  
}

async function addSelectionToMind(info,collection_index){
    var urlParams = "";

    var url = info["linkUrl"];
    switch (info["mediaType"]) {
      case 'image':
        var src = info["srcUrl"];
        var image_src_url =  info["pageUrl"];
        urlParams = `add_image_to_mind?collection_index=${collection_index}&url=${url}&image_src=${src}&image_src_url=${image_src_url}`;
        ApiRequest(urlParams);
        break;
      case 'video':
        var src = info["srcUrl"];
        var video_src_url =  info["pageUrl"];
        urlParams = `add_video_to_mind?collection_index=${collection_index}&url=${url}&video_src=${src}&video_src_url=${video_src_url}`;
        ApiRequest(urlParams);
        break;
      case 'audio':
        var src = info["srcUrl"];
        var page_url =  info["pageUrl"];
        var url = new URL("http://foo.bar/add_audio_to_mind");

        // If your expected result is "http://foo.bar/?x=1&y=2&x=42"
        url.searchParams.append('collection_index', collection_index);
        url.searchParams.append('url', page_url);
        url.searchParams.append('audio_src', src);
        
        ApiRequest(url);
        // urlParams = `add_audio_to_mind?collection_index=${collection_index}&url=${page_url}&audio_src=${src}`;

        break;
      default:
        break;
    }

   
}

async function ApiRequest(urlParams,show_tags=true,bad_response_timeout=2000, timeout = defaultTimeout,sendResponse=null,save_name=""){
    let mainUrl = await getFromStorage("serverIP");
    const req = new XMLHttpRequest();
    if(!isEmpty(mainUrl)){
      const baseUrl = mainUrl;

      if(typeof urlParams == "object")
      {
        var url = urlParams.toString().replace("http://foo.bar/",baseUrl)
        req.open("GET", url, true);
      }else{
        req.open("GET", baseUrl+urlParams, true);
      }
      
      req.send();

      req.onreadystatechange = function() { // Call a function when the state changes.
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            parseAndSwitchResponse(this.responseText,show_tags,timeout=timeout);
            
            if(save_name != "")
            {
              console.log(this.responseText);
              chrome.storage.sync.set({ "mind_structure" : this.responseText }, function() {
                if (chrome.runtime.error) {
                  console.log("Runtime error.");
                }
                console.log("Succesfully saved data with name: " + save_name);
              });
            }
            
            if(sendResponse){
              var msg = { action: "success" , data: this.responseText};
              sendResponse(msg);
            }
            
        } else if (this.status === 0) {
            switchResponse("-1",timeout=bad_response_timeout);
            if(sendResponse){
              var msg = { action: 'error'};
              sendResponse(msg);
            }
        }
      }
    }else{
      switchResponse("-1",timeout=bad_response_timeout);
      if(sendResponse){
        var msg = { action: 'error'};
        sendResponse(msg);
      }
    }
}

function parseAndSwitchResponse(response_from_api,show_tags_menu,timeout=defaultTimeout){
  var myObj = JSON.parse(response_from_api);  
  console.log("Parsing this response " + myObj);
  switchResponse(String(myObj['status_code']), String(myObj['block_url']),String(myObj['status_text']),String(myObj['text_response']),String(myObj['block_title']),String(myObj['block_attached_url']),show_tags_menu,timeout);
}

function switchResponse(status_code,block_url,status_text,text_response,block_title = "none",block_attached_url = "none",show_tags_menu=true,timeout=defaultTimeout)
{
  if (status_code == '-1'){
    createLoadingHandler(
      () =>
        showLoading({
          loading: false
        })
    );
    if(usePromise){
      createHandler(
        () =>
          showNotification({
            message: browser.i18n.getMessage("server_error"),
            status: "error",
            redirect: "https://github.com/elblogbruno/NotionAI-MyMind/wiki/Common-Issues",
            show_tags: false,
            block_title: block_title,
            block_attached_url: block_attached_url,
            timeout: timeout,
          })
      );
    }else{
      createHandler(
        () =>
          showNotification({
            message: chrome.i18n.getMessage("server_error"),
            status: "error",
            redirect: "https://github.com/elblogbruno/NotionAI-MyMind/wiki/Common-Issues",
            show_tags: false,
            block_title: block_title,
            block_attached_url: block_attached_url,
            timeout: timeout,
          })
      );
    }
    
  }
  else if (status_code == '-3'){
    createLoadingHandler(
      () =>
        showLoading({
          loading: false
        })
    );
    if(usePromise){
      createHandler(
        () =>
          showNotification({
            message: browser.i18n.getMessage("please_refresh"),
            status: "error",
            redirect: "https://github.com/elblogbruno/NotionAI-MyMind/wiki/Common-Issues",
            show_tags: false,
            block_title: block_title,
            block_attached_url: block_attached_url,
            timeout: timeout,
          })
      );
    }else{
      createHandler(
        () =>
          showNotification({
            message: chrome.i18n.getMessage("please_refresh"),
            status: "error",
            redirect: "https://github.com/elblogbruno/NotionAI-MyMind/wiki/Common-Issues",
            show_tags: false,
            block_title: block_title,
            block_attached_url: block_attached_url,
            timeout: timeout,
          })
      );
    }
  }
  else{
    
    createLoadingHandler(
      () =>
        showLoading({
          loading: false
        })
    );

    createHandler(
      () =>
        showNotification({
          message: text_response,
          status: status_text,
          redirect: block_url,
          show_tags: show_tags_menu,
          block_title: block_title,
          block_attached_url: block_attached_url,
          timeout: timeout,
        })
    );
  }
}

chrome.cookies.onChanged.addListener(function(info) 
{
  if(info['cookie']['domain'] == ".notion.so" && info['cookie']['name']  == "token_v2")
  {
      var value = info['cookie']['value'];
      const urlParams = `update_notion_tokenv2?tokenv2=${value}`;
      ApiRequest(urlParams);
  }
});


// Runtime Message
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    const {action, updateMultiSelectTags,getMultiSelectTags, openTab, new_url, new_title,block_id,block_id_modify} = request;

    if (action == 'refresh_collections')
    {
      GetMindStructure(sendResponse);
    }
    else if(block_id_modify)
    {
      ModifyTitleUrlRequest(new_title,new_url,block_id_modify,sendResponse);
    }
    else if (openTab) 
    {
      openNewTab(openTab);
    }

    chrome.storage.sync.get("collection_index", function(items) {
      if (!chrome.runtime.error) {
        collection_index = items["collection_index"];
        if (updateMultiSelectTags) {
          UpdateMultiSelectTags(request,block_id,collection_index, sendResponse);
        }
        else if(getMultiSelectTags)
        {
          GetMultiSelectTags(collection_index,sendResponse);
        }
        
      }else{
        console.log("error");
      }
    });
    
    
    return true;
});

async function GetMultiSelectTags(collection_index,replyToApp){
  const req = new XMLHttpRequest();
  let baseUrl = await getFromStorage("serverIP");
  if(!isEmpty(baseUrl)){
    urlParams = `get_multi_select_tags?collection_index=${collection_index}`;

    req.open("GET", baseUrl+urlParams, true);
    req.onreadystatechange = function() { // Call a function when the state changes.
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            var myObj = JSON.parse(this.responseText);
            replyToApp(myObj);
        } else if (this.status === 0) {
            switchResponse("-1");
        }
    }
    req.send();
  }else{
    switchResponse("-1");
  }
}

async function ModifyTitleUrlRequest(newTitle,newUrl,id,replyToApp){
  const req = new XMLHttpRequest();
  let baseUrl = await getFromStorage("serverIP");
  if(!isEmpty(baseUrl)){
    urlParams = `modify_element_by_id?id=${id}&new_title=${newTitle}&new_url=${newUrl}`;
    req.open("GET", baseUrl+urlParams, true);
    
    req.onreadystatechange = function() { // Call a function when the state changes.
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            var myObj = JSON.parse(this.responseText);
            replyToApp(myObj);
        } else if (this.status === 0) {
            switchResponse("-1");
        }
    }
    req.send();
  }else{
    switchResponse("-1");
  }
}

// Add Tag to an Item
async function UpdateMultiSelectTags(data,block_id,collection_index, replyToApp) {
	try {
    let baseUrl = await getFromStorage("serverIP");
    if(!isEmpty(baseUrl)){

      const response = await fetch(
        `${baseUrl}update_multi_select_tags`,
        {
          method: "POST",
          headers: {
            "collection_index": `${collection_index}`,
            "id": `${block_id}`,
            "Content-Type": "application/json",
          },
          referrer: "no-referrer",
          body: JSON.stringify(data.updateMultiSelectTags)
        }
      );

      const json = await response.json();

      replyToApp(json);
      
    }else{
      switchResponse("-1");
    }
	} catch (err) {
		console.log("Oh no, somethings wrong", err);
	}
}
// undefined
function createCollectionHandler(callback) {
  chrome.tabs.insertCSS({
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
  console.log(structure);
  if (structure != null){
    try {
    
      var jsonData = JSON.parse(structure);

      if(jsonData.extra_content.length > 0){
        props = {
          structure,
        }

        function callback() {
          chrome.tabs.executeScript({file: 'js/collectionPopupBehaviour.js'},
          function (result) {
            chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
              if (request.action === 'done') {
                  sendResponse({ action: 'hide_collections_menu' });
      
                  createLoadingHandler(
                    () =>
                      showLoading({
                        loading: true
                      })
                  );

                  callback_from_caller(request.result_index);
      
                  chrome.runtime.onMessage.removeListener(arguments.callee);
      
                  chrome.storage.sync.set({ "collection_index" : request.result_index }, function() {
                    if (chrome.runtime.error) {
                      console.log("Runtime error.");
                    }
                    console.log("Succesfully saved data");
                  });
                  
                  
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
            ${Object.entries(props).map(([key, value]) => `window.caimm.${key} = '${value}';`).join('')}
          `
        };

        if (usePromise) {
          browser.tabs.executeScript(config).then(callback);
        } else {
          chrome.tabs.executeScript(config, callback);
        }
      }else{
        switchResponse("-3");
      }
    }catch(error){
      switchResponse("-3");
    }

  }else{
    switchResponse("-3");
  }
}

function createLoadingHandler(callback) {
  chrome.tabs.insertCSS({
    file: "css/loading.css",
  });

  const config = { file: "js/loadingCreate.js" };

  if (usePromise) {
    browser.tabs.executeScript(config).then(callback);
  } else {
    chrome.tabs.executeScript(config, callback);
  }
}

function showLoading({ loading }) {
	const props = {
		loading
	}

	function callback() {
    chrome.tabs.executeScript({ file: "js/loadingBehaviour.js" });
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

function showNotification({ status, message, redirect,show_tags,block_title,block_attached_url,timeout, icon = 'icon.png' }) {
	console.log(timeout);
  const props = {
		icon: chrome.runtime.getURL(`icon/${icon}`),
		message,
		status,
		redirect,
    show_tags,
    block_title,
    block_attached_url,
    timeout
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

/*Other utils functions*/
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
