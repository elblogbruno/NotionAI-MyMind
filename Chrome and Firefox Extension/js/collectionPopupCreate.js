(() => {
	if (document.getElementById("collection-notification")) return false;

	const notification = document.createElement("div");
	notification.setAttribute("id", "collection-notification");

	document.body.appendChild(notification);
})();