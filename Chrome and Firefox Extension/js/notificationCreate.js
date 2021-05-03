(() => {
	if (document.getElementById("naimm-notification")) return false;

	const notification = document.createElement("div");
	notification.setAttribute("id", "naimm-notification");

	document.body.appendChild(notification);
})();