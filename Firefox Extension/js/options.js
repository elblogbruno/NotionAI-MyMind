function saveSettings() {
  var ip = document.getElementById("serverip").value;
  browser.storage.local.set({ "serverIP" : ip }, function() {
    if (browser.runtime.error) {
      console.log("Runtime error.");
    }
    alert("Settings were successfully saved !" + ip);
  });
}

function restore_options() {
  browser.storage.local.get("serverIP", function(items) {
    if (!browser.runtime.error) {
      console.log(items["serverIP"]);
      document.getElementById("ip_status").innerHTML  = items["serverIP"];
    }
  });
  getTokenFromCookie();
}

function getTokenFromCookie(){
  getCookies("https://www.notion.so/", "token_v2", function(id) {
     document.getElementById("token_info").innerHTML  = id
  });
}

function getCookies(domain, name, callback) {
  browser.cookies.get({"url": domain, "name": name}, function(cookie) {
      if(callback) {
          callback(cookie.value);
      }
  });
}

document.addEventListener('DOMContentLoaded', function() {
  restore_options();
  document.getElementById('save').onclick = saveSettings;
}, true);