(() => {
	const usePromise = typeof browser !== "undefined";

	const { structure } = window.caimm;

	var jsonData = JSON.parse(structure);
	
	console.log("json data " + jsonData);
	
	const notification = document.getElementById("collection-notification");

	notification.removeAttribute("closing");
	if (status && status !== "undefined") notification.setAttribute("status", status);

	const notificationWrap = document.createElement("div");
	notificationWrap.className = "collection-notification-wrap";

	const notificationInner = document.createElement("div");
	notificationInner.className = "collection-notification-inner";

	const collectionButtonsSettings = document.createElement("div");
	collectionButtonsSettings.className = "collection-buttons-settings";

	

	var closeButton = document.createElement("button");
	closeButton.className = 'btn-settings';

	collectionButtonsSettings.appendChild(closeButton);

	closeButton.innerText = chrome.i18n.getMessage("close");
	closeButton.onclick	= function(){ 
		SetCollectionMenuStatus(notification,true);
	};

	var reloadButton = document.createElement("button");
	reloadButton.className = 'btn-settings';
	
	collectionButtonsSettings.appendChild(reloadButton);
	reloadButton.innerText = chrome.i18n.getMessage("refresh");
	reloadButton.onclick	= function()
	{ 
		var msg = { action: 'refresh_collections'};
		chrome.runtime.sendMessage(msg, function(response) {
			SetButtonsMenuStatus(buttonInner,false);

			if (response.action === 'error') {
				console.log("Error refreshing the collections.");	
				SetButtonsMenuStatus(buttonInner,true);
				SetCollectionMenuStatus(notification,true);
			}else if(response.action === 'success')
			{
				var jsonData = JSON.parse(response.data);
				createButtonArray(jsonData,buttonInner,notification);
				SetButtonsMenuStatus(buttonInner,true);
			}
		});
	};

	const buttonInner = document.createElement("div");
	buttonInner.className = "collection-button-div";	
	SetButtonsMenuStatus(buttonInner,true);
	SetCollectionMenuStatus(notification,false);
	
	createButtonArray(jsonData,buttonInner,notification);

	notificationInner.append(buttonInner);
	notificationWrap.appendChild(notificationInner);


	notification.innerHTML = "";
	notification.appendChild(notificationWrap);
	notification.appendChild(collectionButtonsSettings);
	
	setTimeout(() => {
		if (jsonData.extra_content.length == 1){
			var msg = { action: 'done', result_index: 0 };

			chrome.runtime.sendMessage(msg, function(response) {
					if (response.action === 'next') {
						setTimeout(() => {
							SetCollectionMenuStatus(notification,true);
						}, 4000);
					}
			});
		}
	}, 2000);
})();

function createButtonArray(jsonData,buttonInner,notification)
{
	console.log("Creating button array!");
	
	if(buttonInner.childElementCount > 0) //we clear in case there are already buttons in there.
	{
		buttonInner.innerHTML = '';
	}

	for (let index = 0; index < jsonData.extra_content.length; index++) 
	{
		const element = jsonData.extra_content[index];

		var container = document.createElement("div");
		container.className = 'container-image';

		var btn = document.createElement("button");
		btn.className = 'btn-collection';

		var img = document.createElement("img");
		img.src = element.collection_cover
		img.className = 'btn-img';

		container.appendChild(btn);
		
		var containerText = document.createElement("div");

        var t = document.createElement("div");
		t.innerHTML = element.collection_name
		t.className = 'centered';

		containerText.appendChild(img);
		containerText.appendChild(t);
		

		btn.appendChild(containerText);

		btn.onclick	= function(){ 
			var msg = { action: 'done', result_index: index};

			chrome.runtime.sendMessage(msg, function(response) {
				if (response.action === 'hide_collections_menu') {
					SetCollectionMenuStatus(notification,true);
					notification.parentElement.removeChild(notification);
				}
			});
		};
		
        buttonInner.appendChild(container);
	}
}

function SetCollectionMenuStatus(notification,status)
{
	console.log("Hiding collections? " + status);	
	notification.setAttribute("hide", status);	
}

function SetButtonsMenuStatus(buttonInner, status)
{
	console.log("Hiding Buttons? " + status);	
	buttonInner.setAttribute("show", status);
}