(() => {
	const usePromise = typeof browser !== "undefined";

	const { loading } = window.naimm;

	const loadingDiv = document.getElementById("naimm-loading-div");

	if (loading)
	{
		console.log("Showing loading");
		loadingDiv.setAttribute("loading", true);
	}else{
		console.log("Hiding loading");
		loadingDiv.setAttribute("loading", false);
	}
	
})();
