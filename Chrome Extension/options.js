function saveSettings() {
  var ip = document.getElementById("serverip").value;
  chrome.storage.sync.set({ "serverIP" : ip }, function() {
    if (chrome.runtime.error) {
      console.log("Runtime error.");
    }
    alert("Settings were successfully saved !" + ip);
  });
}
function restore_options() {
  chrome.storage.sync.get("serverIP", function(items) {
    if (!chrome.runtime.error) {
      console.log(items["serverIP"]);
      document.getElementById("ip_status").innerHTML  = items["serverIP"];
    }
  });
}

document.addEventListener('DOMContentLoaded', function() {
  restore_options();
  document.getElementById('save').onclick = saveSettings;
}, true);