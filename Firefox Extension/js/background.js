const CONTEXT_MENU_ID = "MY_CONTEXT_MENU";
const CONTEXT_MENU_ID_COOKIE = "MY_CONTEXT_MENU";

function getword(info,tab) {
  if (info.menuItemId !== CONTEXT_MENU_ID) {
    return;
  }
  const req = new XMLHttpRequest();
  browser.storage.local.get("serverIP", function(items) {
    if (!chrome.runtime.error) {
      ip = items["serverIP"];
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
      
      req.open("GET", baseUrl+urlParams, true);
      req.send();
  
      req.onreadystatechange = function() { // Call a function when the state changes.
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            console.log("Got response 200!");
            switchResponse(this.responseText);
        } else if (this.readyState === XMLHttpRequest.DONE && this.status === 0) {
          switchResponse("-1");
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


function switchResponse(response){
  switch (response) {
    case '200':
      alert("Added to your mind")
      break;
    case '409':
      alert("Could be added to your mind, but with no thumbnail!")
      break;
    case '500':
      alert("This url is invalid")
      break;
    case '-1':
      alert("Error during accessing server. Make sure the ip/port are corrects, and the server is running.");
      break;
    default:
      break;
  }
}


browser.cookies.onChanged.addListener(function(info) 
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
