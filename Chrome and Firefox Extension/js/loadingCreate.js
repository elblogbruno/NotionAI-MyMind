(() => {
	if (document.getElementById("naimm-loading-div")) return false;

	const notification = document.createElement("div");
	notification.setAttribute("id", "naimm-loading-div");
	
	loadingObject = document.createElement("div");
	loadingObject.id = 'naimm-loading';

	notification.appendChild(loadingObject);

	document.body.appendChild(notification);
})();