
window.onload = initAll;
var xhr = false;
function initAll() {
	if (window.XMLHttpRequest) {
		xhr = new XMLHttpRequest();
	}
	else {
		if (window.ActiveXObject) {
			try {
				xhr = new ActiveXObject("Microsoft.XMLHTTP");
			}
			catch (e) { }
		}
	}

	if (!xhr) {
		alert("Sorry, but I couldn't create an XMLHttpRequest");
	}
	update_status()
}


function update_status() {
	xhr.open("GET", "/query_status", true);
	xhr.onreadystatechange = show_update;
	xhr.send(null);


}

function show_update() {
	if (xhr.readyState == 4) {
		if (xhr.status == 200) {
			var outMsg = xhr.responseText;
			if (outMsg == "None") {
				window.location.reload()
			}
			else {
				setTimeout("update_status()", 1 * 1000);
			}
		}
		else {
			var outMsg = "Error: " + xhr.status;
		}
		document.getElementById("query_status").innerHTML = outMsg;
	}

}
