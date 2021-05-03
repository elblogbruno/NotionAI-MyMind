(() => {
	const selection = window.getSelection().toString();

	return { selectionText: selection }
})();