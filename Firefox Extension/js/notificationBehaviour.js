(() => {
	const usePromise = typeof browser !== "undefined";

	const { id, icon,  message, status, redirect , show_tags, block_title,block_attached_url } = window.naimm;

	const events = {};
	const tags = [];
	var tagCache = [];

	

	let previousValue = "";
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

	
	if (status === "success" && show_tags == 'true') 
	{
		
		const notificationTags = document.createElement("div");
		notificationTags.className = "naimm-notification-tags";

		const notificationTagsStorage = document.createElement("div");
		notificationTagsStorage.className = "naimm-tagstorage";

		const notificationInput = document.createElement("input");
		notificationInput.type = "text";
		notificationInput.placeholder = "Add tags";


		const notificationTagsUpdateButton = document.createElement("button");
		notificationTagsUpdateButton.className = "naimm-tags-update-button";
		notificationTagsUpdateButton.innerHTML = "Update Tags";

		const notificationTagsDivButton = document.createElement("div");
		notificationTagsDivButton.className = "naimm-notification-tags-button-div";
		
		notificationTagsDivButton.style.display = 'none';

		/*Suggestions*/
		const notificationTagSuggestions = document.createElement("div");
		notificationTagSuggestions.className = "naimm-notification-suggestions";

		const notificationTagSuggestionsTitle = document.createElement("p");
		notificationTagSuggestionsTitle.className = "naimm-notification-suggestions-title";
		notificationTagSuggestionsTitle.innerText = "Tag Suggestions";

		const notificationTagSuggestionsStorage = document.createElement("div");
		notificationTagSuggestionsStorage.className = "naimm-notification-suggestions-storage";


		const notificationTagsLoading = document.createElement("img");
		notificationTagsLoading.id = "loading-edit-icon"
		notificationTagsLoading.setAttribute("loading", false);

		const notificationTagsStatus = document.createElement("p");
		notificationTagsStatus.innerHTML = "";
		notificationTagsStatus.id = "naimm-edit-status";

		const notificationTagsButtonParent = document.createElement("div");
		notificationTagsButtonParent.appendChild(notificationTagsUpdateButton)

		const notificationTagsLoadingStatusDiv = document.createElement("div");
		notificationTagsLoadingStatusDiv.appendChild(notificationTagsLoading);
		notificationTagsLoadingStatusDiv.appendChild(notificationTagsStatus);

		notificationTagsDivButton.appendChild(notificationTagsButtonParent);
		notificationTagsDivButton.appendChild(notificationTagsLoadingStatusDiv);
		

		/*Edit menu*/
		
		const notificationEdit = document.createElement("div");
		notificationEdit.className = "naimm-notification-edit";

		const notificationEditTitle = document.createElement("p");
		notificationEditTitle.innerHTML = "Modify Block";
		notificationEditTitle.className = "naimm-edit-title";

		const notificationEditStorage = document.createElement("div");
		notificationEditStorage.className = "naimm-editstorage";

		const editInput1 = document.createElement("input");
		editInput1.type = "text";
		editInput1.placeholder = block_title;

		const editInput2 = document.createElement("input");
		editInput2.type = "text";
		editInput2.placeholder = block_attached_url;

		editInput1.style.visibility = 'visible';
		editInput2.style.visibility = 'visible';

		const notificationEditInputDiv= document.createElement("div");
		notificationEditInputDiv.className = "naimm-editinputdiv";

		notificationEditInputDiv.appendChild(editInput1);
		notificationEditInputDiv.appendChild(editInput2);

		const notificationEditLoading = document.createElement("img");
		notificationEditLoading.id = "loading-edit-icon"
		notificationEditLoading.setAttribute("loading", false);

		const notificationEditStatus = document.createElement("p");
		notificationEditStatus.innerHTML = "";
		notificationEditStatus.id = "naimm-edit-status";

		notificationEditStorage.appendChild(notificationEditInputDiv);
		notificationEditStorage.appendChild(notificationEditLoading);
		notificationEditStorage.appendChild(notificationEditStatus);

		const notificationEditButton = document.createElement("button");
		notificationEditButton.innerHTML = "Modify";
		notificationEditButton.className = "edit_button";

		notificationEdit.appendChild(notificationEditTitle);
		notificationEdit.appendChild(notificationEditStorage);
		notificationEdit.appendChild(notificationEditButton);
		
		notificationEdit.setAttribute("closing", true);

		createListener("keyup", notificationInput, "keyup", event => {
			const value = event.target.value.trim();

			if (value === "") {
				if (["Backspace", "Delete"].includes(event.key)) {
					if (tags.length) {
						const last = tags[tags.length - 1];
						removeTag(last.option_id);
					}
				}
				showSuggestions();
			} else {
				if (event.key !== "Enter") {
					if (value !== previousValue) {
						getSuggestions(value);
					}
				}
			}

			previousValue = value;

			if (["ArrowDown", "ArrowUp", "Enter"].includes(event.key)) {
				event.preventDefault();

				const suggestions = Array.from(notificationTagSuggestionsStorage.children);
				const active = suggestions.findIndex(item => item.hasAttribute("focus"));
				const activeItem = active != -1 && suggestions[active];

				if (event.key === "ArrowDown") {
					if (activeItem) {
						const newItem = suggestions[active + 1];

						if (newItem) {
							newItem.setAttribute("focus", true);
							activeItem.removeAttribute("focus");
						}
					} else {
						const newItem = suggestions[0];

						if (newItem) {
							newItem.setAttribute("focus", true);
						}
					}
				}

				if (event.key === "ArrowUp") {
					if (activeItem) {
						const newItem = suggestions[active - 1];

						if (newItem) {
							newItem.setAttribute("focus", true);
							activeItem.removeAttribute("focus");
						}
					}
				}

				if (event.key === "Enter") {
					const itemValue = activeItem && activeItem.dataset.value;
					const newTag = itemValue || value;

					if (newTag) {
						addTag(newTag);
						showSuggestions();
						previousValue = "";
						notificationInput.value = "";
						notification.removeAttribute("mouse");
					}
				}
			}
		});

		notificationTags.appendChild(notificationTagsStorage);
		notificationTags.appendChild(notificationInput);
		
		notificationWrap.appendChild(notificationTags);
		notificationWrap.appendChild(notificationTagsDivButton);
		notificationWrap.appendChild(notificationEdit);

		notificationTagSuggestions.appendChild(notificationTagSuggestionsTitle);
		notificationTagSuggestions.appendChild(notificationTagSuggestionsStorage);
		notificationWrap.appendChild(notificationTagSuggestions);

		createListener("suggestion-click", notificationTagSuggestionsStorage, "click", event => {
			const value = event.target.dataset.value;

			if (value) {
				addTag(value);
				showSuggestions();
				notificationInput.focus();
				notificationInput.value = "";
				notification.removeAttribute("mouse");
			}
		});

		createListener("click", notificationIcon, "click", event => {
			if(notificationEdit.getAttribute("closing") == 'true')
			{
				notificationEdit.setAttribute("closing", false);
			}else{
				notificationEdit.setAttribute("closing", true);
			}
		});
		
		createListener("click", notificationTagsUpdateButton, "click", event => {
			updateTags(tags);
		});

		createListener("click", notificationEditButton, "click", event => {
			modifyTitleUrl(editInput1.value,editInput2.value);
		});
		
		window.setTimeout(() => {
			notificationInput.focus();

			createListener("focus", notificationInput, "focus", event => {
				notification.setAttribute("focus", true);
			});
		}, 100);

		createListener("keydown", notificationInput, "keydown", event => {
			notification.setAttribute("focus", true);
		});

		createListener("blur", notificationInput, "blur", event => {
			notification.removeAttribute("focus");
			//createRemovalTimeout(4000);
		});
		
		const getSuggestionsList = function() {
			function callback(response) {
				if (response.status_code == 200){
					console.log(response);
					for (var i = 0, len = response.extra_content.length; i < len; i++){
						tagCache.push(response.extra_content[i].option_name);
					}
				}else{
					console.log(response);
				}
				
				return;
			};

			const config = { getMultiSelectTags: 'done' };

			if (usePromise) {
				browser.runtime.sendMessage(config).then(callback);
			} else {
				chrome.runtime.sendMessage(config, callback);
			}
		}.bind(this);

		getSuggestionsList();

		const getSuggestions = function(value) {
			var tags = [];
			for (var i = 0, len = tagCache.length; i < len; i++){
				if (tagCache[i].toLowerCase().includes(value.toLowerCase())){
					tags.push(tagCache[i]);
				}
			}

			if (tags) {
				showSuggestions(tags);
				return;
			}
		}.bind(this);

		const updateTags = function(tags) {
			if (0 === tags.lenght){
				notificationEdit.setAttribute("closing", true);	
			}else{
				function callback(response) {
					notificationTagsLoading.setAttribute("loading", false);
					notificationTagsStatus.innerHTML = String(response['text_response']);
					setTimeout(function () {
						notificationTagsButtonParent.style.display = 'block';
						notificationTagsStatus.innerHTML = "";
						notificationTagsLoading.setAttribute("closing", true);	
						notification.setAttribute("mouse", false);
					}, 2000);		
				};

				var msg = { updateMultiSelectTags: tags,block_id: redirect};
				console.log(msg);

				if (usePromise) {
					browser.runtime.sendMessage(msg).then(callback);
				} else {
					chrome.runtime.sendMessage(msg, callback);
				}

				notificationInput.value = "";
				notificationTagsButtonParent.style.display = 'none';
				notificationTagsLoading.setAttribute("loading", true);
				notification.setAttribute("mouse",true);
			}
		}.bind(this);

		const removeTag = function(option_id) {
			
			const tag = tags.find(item => item.option_id === option_id);
			
			if (tag && tag.element) {
				const index = tags.indexOf(tag);
				const element = tag.element;

				tags.splice(index, 1);
				element.parentElement.removeChild(element);
			}
			console.log(tags.length);
			if (tags.length == 0){
				notificationTagsDivButton.style.display = 'none';
			}
		}.bind(this);

		const addTag = function(value, response) {
			notificationTagsDivButton.style.display = 'block';

			const notificationTag = document.createElement("div");
			const notificationTagIcon = document.createElement("div");

			notificationTag.className = "naimm-notification-tag";
			notificationTag.innerText = value;

			notificationTagIcon.className = "naimm-notification-tag-icon";

			notificationTag.appendChild(notificationTagIcon);
			notificationTagsStorage.appendChild(notificationTag);
			var id = Math.random().toString(36).replace(/[^a-z]+/g, '').substr(0, 5);
			tags.push({ option_name: notificationTag.innerText, option_id: id , element: notificationTag});

			createListener("click", notificationTag, "click", () => {
				removeTag(id);
			});
		}.bind(this);

		const modifyTitleUrl = function(title,url) {
			if ((!title || 0 === title.lenght) && (!url || 0 === url.lenght)){
				notificationEdit.setAttribute("closing", true);	
			}else{
				function callback(response) {
					console.log(response);
					notificationEditLoading.setAttribute("loading", false);
					notificationEditStatus.innerHTML = String(response['text_response']);
					setTimeout(function () {
						notificationEditInputDiv.style.display = 'block';
						notificationEditStatus.innerHTML = "";
						notificationEdit.setAttribute("closing", true);	
	
						editInput1.placeholder = String(response['block_title']);
						editInput2.placeholder = String(response['block_attached_url']);
						notification.setAttribute("mouse", false);
					}, 4000);		
				};
				
				var msg = { new_title: title, new_url: url ,block_id_modify: redirect};
				
				console.log(msg);

				if (usePromise) {
					browser.runtime.sendMessage(msg).then(callback);
				} else {
					chrome.runtime.sendMessage(msg, callback);
				}
	
				notificationEditStatus.innerHTML = "";
				editInput1.value = "";
				editInput2.value = "";
				notificationEditInputDiv.style.display = 'none';
				notificationEditLoading.setAttribute("loading", true);
				notification.setAttribute("mouse",true);
			}
			
		}.bind(this);

		const showSuggestions = function(data) {
			if (data && data.length) {
				const fragment = document.createDocumentFragment();

				data.forEach((item) => {
					const notificationTagSuggestion = document.createElement("div");

					notificationTagSuggestion.dataset.value = item;
					notificationTagSuggestion.innerText = item;
					notificationTagSuggestion.className = "naimm-notification-suggestion";

					fragment.appendChild(notificationTagSuggestion);
				});

				notificationTagSuggestionsStorage.innerHTML = "";
				notificationTagSuggestionsStorage.appendChild(fragment);
				notificationTagSuggestions.style.display = "block";
			} else {
				notificationTagSuggestionsStorage.innerHTML = "";
				notificationTagSuggestions.style.display = "none";
			}
		}.bind(this);
	}

	notification.innerHTML = "";
	notification.appendChild(notificationWrap);

	createListener("click", notificationText, "click", event => {
		if (redirect && redirect !== "undefined") {
			chrome.runtime.sendMessage({ openTab: redirect });
		}

		createRemovalTimeout(0, true);
	});

	createListener("mouseleave", notification, "mouseleave", event => {
		//alert("Mouse leaving: " + notification.getAttribute("mouse"));
		if (notification.getAttribute("mouse") == 'false'){
			notification.removeAttribute("mouse");
			createRemovalTimeout(4000);
		}
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
	}, 9000);
})();