function listAccounts(thisObj, e)
{
	// List all accounts that match a pattern
	
	var account_name = document.getElementById("account_name")
	var member_name = document.getElementById("member_name")
	
    var p = findPos (thisObj);
	var px = (p[0] + 25) + "px";
	var py = (p[1] + 25) + "px";
	 
	var l = document.getElementById("list");
	l.style.visibility = "visible";
	l.style.position = "fixed";
	l.style.left = px;
	l.style.top = py;
	l.style.width = "300px";	
	
    // Try to check for the key
	if (!e) var e = window.event;
	if (e.keyCode) keycode = e.keyCode;
	else if (e.which) keycode = e.which;
	
	if(keycode == 8 )
	{
		//document.getElementById("account_id").value = '';
	}
	
	var url = "search"
	var string = document.getElementById("id_string").value
	var query = url + "?string=" + string;

	var ajaxRequest = xmlHttp();
	ajaxRequest.open("GET",query,true);
	
	ajaxRequest.onreadystatechange = function ()
	{
		if (ajaxRequest.readyState == 4 || ajaxRequest.status == 200 )
		{
            var r = eval("(" + ajaxRequest.responseText + ")");
            l.innerHTML = "<div id='listCancel' >Cancel</div>"
 			for ( i in r ) {
                l.innerHTML += "<div id='listChoice'>" + r[i] + "</div>";
            }
 		}
	}
	ajaxRequest.send(null);
	
} //End function getAccount

