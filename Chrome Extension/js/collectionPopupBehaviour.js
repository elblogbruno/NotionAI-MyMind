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

	// const notificationText = document.createElement("span");

	// if (jsonData.structure.length == 1){
	// 	notificationText.innerText = "Only one available. Will be default:";
	// }else{
	// 	notificationText.innerText = "Available collections:";
	// }
	
	
	// notificationInner.appendChild(notificationText);
	
	const buttonInner = document.createElement("div");
	buttonInner.className = "collection-button-div";
	
	
	buttonInner.setAttribute("show", true);
	
	const notificationTagsLoadingAddingContent = document.createElement("img");
	notificationTagsLoadingAddingContent.id = "loading-edit-icon"
	notificationTagsLoadingAddingContent.setAttribute("loading", false);
	notificationInner.appendChild(notificationTagsLoadingAddingContent);

	for (let index = 0; index < jsonData.structure.length; index++) 
	{
		const element = jsonData.structure[index];

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
			var msg = { action: 'done', result: index };

			buttonInner.setAttribute("show", false);
			notificationTagsLoadingAddingContent.setAttribute("loading", true);
			

			chrome.runtime.sendMessage(msg, function(response) {
				if (response.action === 'next') {
					console.log(response.action);		
					setTimeout(() => {
						notificationTagsLoadingAddingContent.setAttribute("loading", false);
						notification.setAttribute("closing", true);
					}, 4000);
					
				}
			});
		};
		
        buttonInner.appendChild(container);
	}
	
	notificationInner.append(buttonInner);
	notificationWrap.appendChild(notificationInner);


	notification.innerHTML = "";
	notification.appendChild(notificationWrap);
	
	setTimeout(() => {
		if (jsonData.structure.length == 1){
			var msg = { action: 'done', result: 0 };
			
			buttonInner.setAttribute("show", false);
			notificationTagsLoadingAddingContent.setAttribute("loading", true);

			chrome.runtime.sendMessage(msg, function(response) {
					if (response.action === 'next') {
						setTimeout(() => {
							notificationTagsLoadingAddingContent.setAttribute("loading", false);
							notification.setAttribute("closing", true);
						}, 4000);
					}
			});
		}
	}, 2000);
})();
