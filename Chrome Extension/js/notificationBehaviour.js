(() => {
	const usePromise = typeof browser !== "undefined";

	const { id, icon,  message, status, redirect } = window.naimm;

	const events = {};

	const createListener = (id, target, name, callback) => {
		events[id] = {
			target,
			name,
			callback: target.addEventListener(name, callback)
		}
	};

	const notification = document.getElementById("naimm-notification");

	notification.removeAttribute("closing");
	if (status && status !== "undefined") notification.setAttribute("status", status);

	const notificationWrap = document.createElement("div");
	notificationWrap.className = "naimm-notification-wrap";

	const notificationInner = document.createElement("div");
	notificationInner.className = "naimm-notification-inner";

	const notificationIcon = document.createElement("img");
	notificationIcon.src = icon;

	const notificationText = document.createElement("span");
	notificationText.innerText = message;

	notificationInner.appendChild(notificationIcon);
	notificationInner.appendChild(notificationText);
	notificationWrap.appendChild(notificationInner);


	notification.innerHTML = "";
	notification.appendChild(notificationWrap);

	createListener("click", notificationInner, "click", event => {
		if (redirect && redirect !== "undefined") {
			chrome.runtime.sendMessage({redirect: redirect});
		}

		createRemovalTimeout(0, true);
	});

	createListener("mouseleave", notification, "mouseleave", event => {
		notification.removeAttribute("mouse");
		createRemovalTimeout(4000);
	});

	createListener("mouseenter", notification, "mouseenter", event => {
		notification.setAttribute("mouse", true);
	});

	const createRemovalTimeout = (amt, forceClose) => {
		if (window.naimm.id !== id) {
			removeListeners();
			return false;
		}

		setTimeout(() => {
			const isActive = notification.getAttribute("focus") || notification.getAttribute("mouse");
			const isClosing = notification.getAttribute("closing");

			if (forceClose || (!isActive && !isClosing)) {
				notification.addEventListener("animationend", () => {
					if (window.naimm.id === id) notification.parentElement.removeChild(notification);
				});

				notification.setAttribute("closing", true);
			}
		}, amt);
	};

	const removeListeners = () => {
		Object.values(events).forEach(({ target, name, callback }) => target.removeEventListener(name, callback));
	};

	setTimeout(() => {
		createRemovalTimeout(0);
	}, 4000);
})();
