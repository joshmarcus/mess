function find_address(this_obj, e)
{    
    // List all addresses that match a pattern
	var address = document.getElementById("address");
	
	hide_message();
		     
	// Try to check for the key
	if (!e) var e = window.event;
	if (e.keyCode) keycode = e.keyCode;
	else if (e.which) keycode = e.which;
	
	if(keycode == 8 )
	{
		//member.value = '';	
        //document.getElementById("accountID").value = '';
        //document.getElementById("memberID").value = '';
	}
	
    var query = "search_for?search=address&string=" + address.value;

	ajaxRequest = xmlHttp();
	ajaxRequest.open("GET",query,true);

	ajaxRequest.onreadystatechange = function ()
	{
		if (ajaxRequest.readyState == 4 || ajaxRequest.status == 200 )
		{
            show_list(this_obj);
            document.getElementById("list").innerHTML = ajaxRequest.responseText;            
            var response = eval("(" + ajaxRequest.responseText + ")");
            rHtml = "<div id='list_cancel' >Cancel</div>";
 			for ( key in response )
            {
                rHtml += "<div id='list_choice' onclick='add_address("
                        + key + ", \"" + response[key] + "\");'>"
                        + response[key] + "</div>";
            }
            //document.getElementById("list").innerHTML = rHtml;
 		}
	}
    ajaxRequest.send(null);

} //End function getAccount

