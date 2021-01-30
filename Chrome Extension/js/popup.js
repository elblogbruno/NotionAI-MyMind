
var ip;
document.addEventListener('DOMContentLoaded', function() {
    // var myVar = setTimeout(showPage, 2000);
    PopUp.showLoader();
    chrome.tabs.getSelected(null, function(tab) {
      const req = new XMLHttpRequest();


      chrome.storage.sync.get("serverIP", function(items) {
        if (!chrome.runtime.error) {
          ip = items["serverIP"];
          console.log(ip);
          const baseUrl = ip;
      
          var url = tab.url;
          var title = tab.title;
          const urlParams = `add_url_to_mind?url=${url}&title=${title}`;
      
          req.open("GET", baseUrl+urlParams, true);
          
          

          req.onreadystatechange = function() { // Call a function when the state changes.
              if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
                  console.log("Got response 200!");
                  PopUp.switchResponse(this.responseText);
              } else if (this.readyState === XMLHttpRequest.DONE && this.status === 0) {
                  PopUp.switchResponse(-1);
              }
          }

          req.send();
        }
      });
      
      
    });
}, true);


class PopUp {
  static switchResponse(response){
    switch (response) {
      case '200':
        PopUp.showPage("Added to your mind")
        break;
      case '409':
        PopUp.showPage("Could be added to your mind, but with no thumbnail!")
        break;
      case '500':
        PopUp.showPage("This url is invalid")
        break;
      case '-1':
        PopUp.showPage("Error during accessing server. Make sure the ip/port are corrects, and the server is running.");
        break;
      default:
        break;
    }
  }
  static  showPage(content) {
    document.getElementById("message-status").innerHTML  = content;
    document.getElementById("loader").style.display = "none";
    document.getElementById("awmt-notification").style.display = "block";
  }

  static  showLoader() {
    document.getElementById("loader").style.display = "block";
    document.getElementById("awmt-notification").style.display = "none";
  }
}