function getAddresses(thisObj, e)
{    
    // List all addresses that match a pattern
	var addAddress = document.getElementById("addAddress");
	
	hideMessage ();
		     
	// Try to check for the key
	if (!e) var e = window.event;
	if (e.keyCode) keycode = e.keyCode;
	else if (e.which) keycode = e.which;
	
	if(keycode == 8 )
	{
		member.value = '';	
        document.getElementById("accountID").value = '';
        document.getElementById("memberID").value = '';
	}
	
    var query = "cashier?search=getAccounts&string=" + account.value;

	ajaxRequest = xmlHttp();
	ajaxRequest.open("GET",query,true);

	ajaxRequest.onreadystatechange = function ()
	{
		if (ajaxRequest.readyState == 4 || ajaxRequest.status == 200 )
		{
            showList (thisObj);	   
            var r = eval("(" + ajaxRequest.responseText + ")");
            var accounts = r['get_accounts'];
            responseString = "<div id='listCancel' >Cancel</div>";
 			for ( key in accounts )
            {
                responseString += "<div id='listChoice' onclick='setAccount(" +
                                key + ", \"" + accounts[key] +
                                "\"); getAccountMembers(event);'>" +
                                accounts[key] + "</div>";
            }
            document.getElementById("list").innerHTML = responseString;
 		}
	}
    ajaxRequest.send(null);

} //End function getAccount

