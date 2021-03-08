(() => {
	const usePromise = typeof browser !== "undefined";

	const { structure } = window.caimm;

	var jsonData = structure;

	const notification = document.getElementById("collection-notification");

	notification.removeAttribute("closing");
	if (status && status !== "undefined") notification.setAttribute("status", status);

	const notificationWrap = document.createElement("div");
	notificationWrap.className = "collection-notification-wrap";

	const notificationInner = document.createElement("div");
	notificationInner.className = "collection-notification-inner";

	const notificationText = document.createElement("span");

	if (jsonData.structure.length == 1){
		notificationText.innerText = "Only one available. Will be default:";
	}else{
		notificationText.innerText = "Available collections:";
	}
	
	
	notificationInner.appendChild(notificationText);
	
	const buttonInner = document.createElement("div");
	buttonInner.className = "collection-button-div";
	var index1 = 0;

	for (let index = 0; index < jsonData.structure.length; index++) 
	{
		const element = jsonData.structure[index];
		var btn = document.createElement("button");
        var t = document.createTextNode(element.collection_name);
        btn.appendChild(t);

		btn.onclick	= function(){ 
			index1 = index;
			var msg = { action: 'done', result: index };
			chrome.runtime.sendMessage(msg, function(response) {
				if (response.action === 'next') {
					notification.setAttribute("closing", true);
				}
			});
		};
		
        buttonInner.appendChild(btn);
	}

	
	
	notificationInner.append(buttonInner);
	notificationWrap.appendChild(notificationInner);


	notification.innerHTML = "";
	notification.appendChild(notificationWrap);
	
	setTimeout(() => {
		if (jsonData.structure.length == 1){
			var msg = { action: 'done', result: 0 };
			chrome.runtime.sendMessage(msg, function(response) {
					if (response.action === 'next') {
						notification.setAttribute("closing", true);
					}
			});
		}
	}, 2000);
})();
