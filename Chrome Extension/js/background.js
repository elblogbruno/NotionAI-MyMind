const CONTEXT_MENU_ID = "MY_CONTEXT_MENU";
function getword(info,tab) {
  if (info.menuItemId !== CONTEXT_MENU_ID) {
    return;
  }
  showLoader();
  const req = new XMLHttpRequest();
  chrome.storage.sync.get("serverIP", function(items) {
    if (!chrome.runtime.error) {
      ip = items["serverIP"];
      console.log(ip);
      const baseUrl = ip;
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
          var text = info.selectionText;
          url = tab.url;
          urlParams = `add_text_to_mind?url=${url}&text=${text}`;
          break;
      }
      //alert(baseUrl+urlParams);
      //console.log(baseUrl+urlParams);
      req.open("GET", baseUrl+urlParams, true);
      req.send();
  
      req.onreadystatechange = function() { // Call a function when the state changes.
          if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
              console.log("Got response 200!");
              console.log(this.responseText)
              switch (this.responseText) {
                case '200':
                  showPage("Added to your mind")
                  break;
                case '409':
                  showPage("Could not be added to your mind. (This content is invalid)")
                  break;
                case '500':
                  showPage("This url is invalid")
                  break;
                default:
                  break;
              }
          } else {
            showPage("Error during accessing server. Make sure the ip/port are corrects, and the server is running.");
          }
      }
    }
  
  });
}

chrome.contextMenus.create({
  title: "Add to my Mind: %s", 
  contexts:["all"], 
  id: CONTEXT_MENU_ID
});
chrome.contextMenus.onClicked.addListener(getword)

chrome.menus.create({
  id: "open-popup",
  title: "open popup",
  contexts: ["all"]
});

chrome.menus.onClicked.addListener(() => {
  browser.browserAction.openPopup();
});
function showPage(content) {


  document.getElementById("message-status").innerHTML  = content;
  document.getElementById("loader").style.display = "none";
  document.getElementById("awmt-notification").style.display = "block";
}

function showLoader() {
  // const i = document.createElement('iframe')
  
  // chrome.runtime.sendMessage({ open: true }, (response) => {
  //   i.src = response
  //   p.appendChild(i)
  // })

  // document.getElementById("loader").style.display = "block";
  // document.getElementById("awmt-notification").style.display = "none";
  chrome.browserAction.openPopup();
}