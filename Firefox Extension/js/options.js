function saveSettings() {
  var ip = document.getElementById("serverip").value;
  if(ValidURL(ip)){
    
    var res = ip.charAt(ip.length-1);
    if (res != "/"){
      ip = ip+"/";
    }
    
    browser.storage.local.set({ "serverIP" : ip }, function() {
      if (chrome.runtime.error) {
        console.log("Runtime error.");
      }
      alert("Settings were successfully saved! " + ip);
    });
  }else{
    alert("Please make sure you enter a correct url.")
  }
}

function restore_options() {
  browser.storage.local.get("serverIP", function(items) {
    if (!browser.runtime.error) {
      console.log(items["serverIP"]);
      document.getElementById("ip_status").innerHTML  = items["serverIP"];
    }
  });
  cookies_utils.getTokenFromCookie();
}

function ValidURL(str) {
  var regex = /(http|https):\/\/(\w+:{0,1}\w*)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%!\-\/]))?/;
  if(!regex .test(str)) {

    return false;
  } else {
    return true;
  }
}


document.addEventListener('DOMContentLoaded', function() {
  restore_options();
  document.getElementById('save').onclick = saveSettings;
}, true);

class cookies_utils {

  static getTokenFromCookie(){
    cookies_utils.getCookies("https://www.notion.so/", "token_v2", function(id) {
       document.getElementById("token_info").innerHTML  = id
    });
  }
  
  static getCookies(domain, name, callback) {
    browser.cookies.get({"url": domain, "name": name}, function(cookie) {
        if(callback) {
            callback(cookie.value);
        }
    });
  }

}