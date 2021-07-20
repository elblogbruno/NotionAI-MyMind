(() => {
	const usePromise = typeof browser !== "undefined";

	const { id, icon,  message, status, redirect , show_tags, block_title,block_attached_url,timeout } = window.naimm;

	const events = {};
	var tags = [];
	var tagCache = [];
	var tagSuggestionsCache = [];

	console.log("TIMEOUT: " + timeout)
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
		let { notificationTags, notificationTagSuggestions,notificationTagsLoading,notificationTagSuggestionsStorage,notificationInput,notificationTagsUpdateButton,notificationTagsDivButton,notificationTagsStorage,notificationTagsButtonParent,notificationTagsStatus } = createSuggestionsInput();
		let { notificationEdit, notificationEditButton,editInput1,editInput2,notificationEditStatus, notificationEditLoading, notificationEditInputDiv } = createEditMenu(block_title, block_attached_url);
		let { notificationTime, notificationNotionTimeOption, notificationTimeLoading,notificationAutoDestroyCheck,notificationTimeButton,notificationTimeInputDiv,notificationTimeStatus } = createTimeInput();
		
		notification.setAttribute("requesting", false);
		
		notificationWrap.appendChild(notificationTags);
		notificationWrap.appendChild(notificationTagsDivButton);
		notificationWrap.appendChild(notificationEdit);
		notificationWrap.appendChild(notificationTime);

		notificationWrap.appendChild(notificationTagSuggestions);
		
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
						console.log(newTag);
						tag = createNewTagObject(tagCache,newTag);
						console.log("New tag " + tag);	
						addTag(tag);
						
						showSuggestions();
						previousValue = "";
						notificationInput.value = "";
						notification.removeAttribute("mouse");
					}
				}
			}
		});

		createListener("suggestion-click", notificationTagSuggestionsStorage, "click", event => {
			const value = event.target.dataset.value;

			if (value) {
				console.log(value);
				tag = createNewTagObject(tagCache,value);
				console.log("New tag " + tag);	
				addTag(tag);
				
				showSuggestions();
				notificationInput.focus();
				notificationInput.value = "";
				notification.removeAttribute("mouse");
			}
		});

		createListener("click", notificationIcon, "click", event => {

			//if the user clicks on the icon, show notificationEdit and notificationTime objects if they are not visible and they are not doing any requests. If they are visible, hide them.
		

			if (notificationEdit.getAttribute("requesting") === "false" && notificationTime.getAttribute("requesting") === "false") 
			{
				if (notificationEdit.getAttribute("closing") === "false" && notificationTime.getAttribute("closing") === "false")
				{
					notificationEdit.setAttribute("closing", true);
					notificationTime.setAttribute("closing", true);
				}else{
					notificationEdit.setAttribute("closing", false);
					notificationTime.setAttribute("closing", false);
				}
			}

		});
		
		createListener("click", notificationTagsUpdateButton, "click", event => {
			updateTags(tags);
		});

		createListener("click", notificationEditButton, "click", event => {
			modifyTitleUrl(editInput1.value,editInput2.value);
		});
		
		createListener("click", notificationTimeButton, "click", event => {
			addReminder(notificationNotionTimeOption,notificationAutoDestroyCheck);
		});

		window.setTimeout(() => {
			notificationInput.focus();

			createListener("focus", notificationInput, "focus", event => {
				console.log("Focus event from notifiaction timeout");
				notification.setAttribute("focus", true);
			});
		}, 100);

		createListener("keydown", notificationInput, "keydown", event => {
			console.log("Keydown event from notifiaction");
			notification.setAttribute("focus", true);
		});

		createListener("blur", notificationInput, "blur", event => {
			console.log("Blur event from notifiaction");
			notification.removeAttribute("focus");
			//createRemovalTimeout(timeout);
		});
		
		const getSuggestionsList = function() {
			function callback(response) {
				if (response.status_code == 200)
				{
					notification.setAttribute("requesting", false);
					console.log(response);
					for (var i = 0, len = response.extra_content.length; i < len; i++){
						tagCache.push(response.extra_content[i]);
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

			notification.setAttribute("requesting", true);
		}.bind(this);

		getSuggestionsList();

		const getSuggestions = function(value) {
			//var tags = [];
			tagSuggestionsCache = [];
			for (var i = 0, len = tagCache.length; i < len; i++){
				if (tagCache[i] != null){
					if (tagCache[i]['option_name'].toLowerCase().includes(value.toLowerCase())){
						tagSuggestionsCache.push(tagCache[i]);
					}
				}
			}

			if (tagSuggestionsCache) {
				showSuggestions(tagSuggestionsCache);
				return;
			}
		}.bind(this);

		const updateTags = function(tags) {
			console.log(tags.lenght)
			
			function callback(response) {
				notificationTagsLoading.setAttribute("loading", false);
				notificationTagsStatus.innerHTML = String(response['text_response']);
				setTimeout(function () {
					notificationTagsButtonParent.style.display = 'block';
					notificationTagsStatus.innerHTML = "";
					notificationTagsLoading.setAttribute("closing", true);	
					notification.setAttribute("mouse", false);
					notification.setAttribute("requesting", false);

					if (tags.length == 0){
						notificationTagsDivButton.style.display = 'none';
					}
				}, 2000);		
			};
			if (tags.length == null)
			{
				tags = [];
			}
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
			notification.setAttribute("requesting", true);
			
		}.bind(this);

		const removeTag = function(option_id) {
			if (Array.isArray(tags) && tags.length){
				var tag = tags.find(item => item.option_id === option_id);
				
				if (tag && tag.element) {
					const index = tags.indexOf(tag);
					const element = tag.element;

					tags.splice(index, 1);
					element.parentElement.removeChild(element);
				}
			}
            else{
				tags = [];
			}
				
		}.bind(this);

		const addTag = function(value) {
			console.log("Adding this tag to input " + value['option_name'])
			notificationTagsDivButton.style.display = 'block';

			const notificationTag = document.createElement("div");
			const notificationTagIcon = document.createElement("div");

			notificationTag.className = "naimm-notification-tag";
			notificationTag.style.backgroundColor = value['option_color'];
			notificationTag.innerText = value['option_name'];
			notificationTagIcon.className = "naimm-notification-tag-icon";

			notificationTag.appendChild(notificationTagIcon);
			notificationTagsStorage.appendChild(notificationTag);
			
			tags.push({ option_name: notificationTag.innerText, option_id: value['option_id'] ,option_color: value['option_color'] , element: notificationTag});

			createListener("click", notificationTag, "click", () => {
				console.log("Notification tag remove click event from notifiaction");
				removeTag(value['option_id']);
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
						notificationEdit.setAttribute("requesting", false);	
	

						editInput1.placeholder = String(response['block_title']);
						editInput2.placeholder = String(response['block_attached_url']);


						notification.setAttribute("mouse", false);
						notification.setAttribute("requesting", false);
					}, timeout);		
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
				notification.setAttribute("requesting", true);
				notificationEdit.setAttribute("requesting", true);	
			}
			
		}.bind(this);

		const addReminder = function(dropdown, auto_destroy) {
			if (dropdown.value == undefined){
				console.log("Undefined reminder");
			}
			{
				function callback(response) {
					console.log(response);
					notificationTimeLoading.setAttribute("loading", false);
					notificationTimeStatus.innerHTML = String(response['text_response']);
					setTimeout(function () {
						notificationTimeInputDiv.style.display = 'block';
						notificationTimeButton.style.display = 'block';
						notificationTimeStatus.innerHTML = "";
						
						notificationTime.setAttribute("closing", true);	
						notificationTime.setAttribute("requesting", false);

						notification.setAttribute("mouse", false);
						notification.setAttribute("requesting", false);
					}, timeout);		
				};
				var dic = JSON.parse(dropdown.value);

				var msg = {start_date: dic["start_date"], unit_value: dic["unit_value"], time_value: dic["time_value"], should_auto_destroy: auto_destroy.checked,block_id_add_reminder: redirect};
				
				console.log(msg);

				if (usePromise) {
					browser.runtime.sendMessage(msg).then(callback);
				} else {
					chrome.runtime.sendMessage(msg, callback);
				}

				notificationTimeStatus.innerHTML = "";
				notificationTimeInputDiv.style.display = 'none';
				notificationTimeButton.style.display = 'none';
				notificationTimeLoading.setAttribute("loading", true);
				notification.setAttribute("mouse",true);
				notification.setAttribute("requesting", true);
				notificationTime.setAttribute("requesting", true);
			}
		}.bind(this);

		const showSuggestions = function(data) {
			if (data && data.length) {
				const fragment = document.createDocumentFragment();

				data.forEach((item) => {
					const notificationTagSuggestion = document.createElement("div");
					console.log(item);
					notificationTagSuggestion.dataset.value = item['option_id'];
					notificationTagSuggestion.innerText = item['option_name'];
					notificationTagSuggestion.color = item['option_color']
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
		console.log("Text click event from notifiaction");
		if (redirect && redirect !== "undefined") {
			chrome.runtime.sendMessage({ openTab: redirect });
		}
		createRemovalTimeout(0, true);
	});

	createListener("mouseleave", notification, "mouseleave", event => {
		console.log("Mouse leave event from notifiaction");
		notification.removeAttribute("mouse");
		//createRemovalTimeout(timeout);
	});

	createListener("mouseenter", notification, "mouseenter", event => {
		console.log("Mouse enter event from notifiaction");
		notification.setAttribute("mouse", true);
	});

	const createRemovalTimeout = (amt, forceClose) => {
		if (window.naimm.id !== id) {
			removeListeners();
			return false;
		}

		setTimeout(() => {
			const doingRequest = notification.getAttribute("requesting");
			const isActive = notification.getAttribute("focus") || notification.getAttribute("mouse");
			const isClosing = notification.getAttribute("closing");

			console.log(isActive + " " + isClosing);

			if (forceClose || (!isActive && !isClosing && !doingRequest) || (isActive == null && isClosing == null)) {
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
		//createRemovalTimeout(0);
	}, timeout);
})();

function createNewTagObject(tagCache,tag_value)
{
	console.log(tagCache);
	
	for (var i = 0; i < tagCache.length; i++){
		console.log(tagCache[i]);
		if (tagCache[i]['option_id'] == tag_value)
			return { option_name: tagCache[i]['option_name'], option_id: tagCache[i]['option_id'] ,option_color: tagCache[i]['option_color'] }
	}

	var id = uuidv4();
	var color_list = ['#505558','#6B6F71','#695B55','#9F7445','#9F9048','#467870','#487088','#6C598F','#904D74','#9F5C58'];
	var color_item = color_list[Math.floor(Math.random() * color_list.length)];
	return { option_name: tag_value, option_id: id ,option_color: color_item }
	
}

function uuidv4() {
	return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
	  (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
	);
}

function createTimeInput(){
	console.log("Creating time menu");
	/*Timer menu*/
	const notificationTime = document.createElement("div");
	notificationTime.className = "naimm-notification-time";

	const notificationTimeTitle = document.createElement("p");
	notificationTimeTitle.innerHTML = "Set reminder";
	notificationTimeTitle.className = "naimm-time-title";

	const notificationTimeStorage = document.createElement("div");
	notificationTimeStorage.className = "naimm-timestorage";

	const notificationTimeLoading = document.createElement("img");
	notificationTimeLoading.id = "loading-time-icon";
	notificationTimeLoading.setAttribute("loading", false);

	const notificationTimeStatus = document.createElement("p");
	notificationTimeStatus.innerHTML = "";
	notificationTimeStatus.id = "naimm-time-status";

	const notificationTimeButton = document.createElement("button");
	notificationTimeButton.innerHTML = "Set Reminder";
	notificationTimeButton.className = "time_button";

	
	const notificationTimeInputDiv = document.createElement("div");
	notificationTimeInputDiv.className = "naimm-editinputdiv";

	var today = new Date();

	var date = today.getFullYear()+'-'+(today.getMonth()+1)+'-'+today.getDate();

	const notificationDateTimeInput = document.createElement("input");
	notificationDateTimeInput.type = "datetime-local";
	notificationDateTimeInput.min = date;
	notificationDateTimeInput.name = "time_input";
	notificationDateTimeInput.className = "time_input";
	notificationDateTimeInput.onchange = function(){
		handleChangeDateInput(this.value,notificationNotionTimeOption);
	 }

	const label = document.createElement("label");
	label.className = "container";
	label.innerHTML = "Autodestroy?";

	const notificationNotionTimeOption = document.createElement("select");
	notificationNotionTimeOption.className = "select_option";

	const notificationAutoDestroyCheck = document.createElement("input");
	notificationAutoDestroyCheck.type = "checkbox";
	notificationAutoDestroyCheck.className = "should_auto_destroy";
	notificationAutoDestroyCheck.checked = "checked";

	label.appendChild(notificationAutoDestroyCheck);
    
	notificationTimeInputDiv.appendChild(notificationDateTimeInput);
	notificationTimeInputDiv.appendChild(notificationNotionTimeOption);
	notificationTimeInputDiv.appendChild(label);
	
	notificationTimeStorage.appendChild(notificationTimeInputDiv);
	notificationTimeStorage.appendChild(notificationTimeLoading);
	notificationTimeStorage.appendChild(notificationTimeStatus);
	

	notificationTime.appendChild(notificationTimeTitle);
	notificationTime.appendChild(notificationTimeStorage);
	notificationTime.appendChild(notificationTimeButton);
	notificationTime.setAttribute("closing", true);
	notificationTime.setAttribute("requesting", false);
	

	return {notificationTime,notificationNotionTimeOption,notificationTimeLoading,notificationAutoDestroyCheck,notificationTimeButton,notificationTimeInputDiv,notificationTimeStatus};
}


function handleChangeDateInput(e, notificationNotionTimeOption){
	const today = new Date();

	console.log(today);

	const inputDate = new Date(e);
	console.log(e);
	console.log(inputDate);
	// To calculate the time difference of two dates
	var Difference_In_Time = inputDate.getTime() - today.getTime();
	
	// To calculate the no. of days between two dates
	var Difference_In_Days = Difference_In_Time / (1000 * 3600 * 24);

	console.log(Difference_In_Days);

	notificationNotionTimeOption.innerHTML = " ";

	var time_options = ["At time of event", "5 minutes before", "10 minutes before", "15 minutes before", "30 minutes before", "1 hour before", "2 hours before","On day of event (9:00 AM)", "1 day before (9:00 AM)"]
	var time_unit = ["minute", "minute","minute","minute","minute","hour","hour","day","day"]
	var time_values = [0,5,10,15,30,1,2,0,1]
	

	if (Difference_In_Days > 2){
		time_options.push("2 day before (9:00 AM)");
		time_unit.push("day");
		time_values.push(2);
		// if (Difference_In_Days > 7){
		// 	options.push("1 week before (9:00 AM)");
		// }
	}

	for(var i = 0; i < time_options.length; i++) 
	{
		var opt = time_options[i];
		var unit = time_unit[i];
		var value = time_values[i];

		var dic = { 'start_date': e, 'unit_value': unit, 'time_value': value }

		var el = document.createElement("option");
		el.textContent = opt;
		el.value = JSON.stringify(dic);

		notificationNotionTimeOption.appendChild(el);
	}
}

function createSuggestionsInput()
{
	/*Suggestions*/

	const notificationTags = document.createElement("div");
	notificationTags.className = "naimm-notification-tags";

	const notificationTagsStorage = document.createElement("div");
	notificationTagsStorage.className = "naimm-tagstorage";

	const notificationInput = document.createElement("input");
	notificationInput.type = "text";
	notificationInput.placeholder = chrome.i18n.getMessage("add_tags_placeholder");


	const notificationTagsUpdateButton = document.createElement("button");
	notificationTagsUpdateButton.className = "naimm-tags-update-button";
	notificationTagsUpdateButton.innerHTML = "Update Tags";

	const notificationTagsDivButton = document.createElement("div");
	notificationTagsDivButton.className = "naimm-notification-tags-button-div";
	
	notificationTagsDivButton.style.display = 'none';

	const notificationTagSuggestions = document.createElement("div");
	notificationTagSuggestions.className = "naimm-notification-suggestions";

	const notificationTagSuggestionsTitle = document.createElement("p");
	notificationTagSuggestionsTitle.className = "naimm-notification-suggestions-title";
	notificationTagSuggestionsTitle.innerText = chrome.i18n.getMessage("tag_title");

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

	notificationTagSuggestions.appendChild(notificationTagSuggestionsTitle);
	notificationTagSuggestions.appendChild(notificationTagSuggestionsStorage);


	notificationTags.appendChild(notificationTagsStorage);
	notificationTags.appendChild(notificationInput);

	return {notificationTags, notificationTagSuggestions,notificationTagsLoading,notificationTagSuggestionsStorage,notificationInput,notificationTagsUpdateButton, notificationTagsDivButton, notificationTagsStorage,notificationTagsButtonParent,notificationTagsStatus};
}

function createEditMenu(block_title, block_attached_url){
	/*Edit menu*/
		
	const notificationEdit = document.createElement("div");
	notificationEdit.className = "naimm-notification-edit";

	const notificationEditTitle = document.createElement("p");
	notificationEditTitle.innerHTML = chrome.i18n.getMessage("modify_block_title");
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
	notificationEditButton.innerHTML = chrome.i18n.getMessage("modify_block_button");
	notificationEditButton.className = "edit_button";

	notificationEdit.appendChild(notificationEditTitle);
	notificationEdit.appendChild(notificationEditStorage);
	notificationEdit.appendChild(notificationEditButton);
	
	notificationEdit.setAttribute("closing", true);
	notificationEdit.setAttribute("requesting", false);
	
	return { notificationEdit, notificationEditButton,editInput1,editInput2,notificationEditStatus, notificationEditLoading,notificationEditInputDiv };
}