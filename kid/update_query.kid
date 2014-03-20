<script type="text/javascript" language="Javascript">

function update_status() {
	xhr.open("GET", "/query_status/${query_id}", true);
	xhr.onreadystatechange = update;
	xhr.send(null);
	document.getElementById("query_status").innerHTML = ;
	setTimeout("update_status()",5 * 1000);
	if (xhr.readyState == 4) {
		if (xhr.status == 200) {
			var outMsg = xhr.responseText;
		}
		else {
			var outMsg = "Error: " + xhr.status;
		}
		document.getElementById("query_status").innerHTML = outMsg;
	}
}
</script>