var ip;
document.addEventListener('DOMContentLoaded', function() {
      // var myVar = setTimeout(showPage, 2000);
      showLoader();
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
          // req.setRequestHeader("Access-Control-Allow-Origin",baseUrl);
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
                        showPage("Could be added to your mind, but with no thumbnail!")
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
        
        
      });
  }, true);


 
  function showPage(content) {
    document.getElementById("message-status").innerHTML  = content;
    document.getElementById("loader").style.display = "none";
    document.getElementById("awmt-notification").style.display = "block";
  }

  function showLoader() {
    document.getElementById("loader").style.display = "block";
    document.getElementById("awmt-notification").style.display = "none";
  }