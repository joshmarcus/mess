//functions.js

function find_pos(obj) {
	// Originally from
	// http://www.quirksmode.org/js/findpos.html
	var curleft = curtop = 0;
	if (obj.offsetParent) {
		curleft = obj.offsetLeft
		curtop = obj.offsetTop
		while (obj = obj.offsetParent) {
			curleft += obj.offsetLeft
			curtop += obj.offsetTop
		}
	}
	return [curleft,curtop];
}

///////////////////////////////////////////////////////////////////////


function xmlHttp()
{
	var xmlHttp=null;
	try {
 		// Firefox, Opera 8.0+, Safari
 		xmlHttp = new XMLHttpRequest();
 	}
	catch (e) {
 		// Internet Explorer
		try {
  			xmlHttp = new ActiveXObject("Msxml2.XMLHTTP");
  		}
 		catch (e) {
  			xmlHttp = new ActiveXObject("Microsoft.XMLHTTP");
		}
		alert ("Browser does not support HTTP Request")
  		return
 	} 
 	
	return xmlHttp;
} // End function xmlHttp

////////////////////////////////////////////////////////////////////////

function xhr(query, element)
{
    ajaxRequest = xmlHttp();
	ajaxRequest.open("GET",query,true);

	ajaxRequest.onreadystatechange = function ()
	{
		if (ajaxRequest.readyState == 4 || ajaxRequest.status == 200 )
		{	   
	        var response = ajaxRequest.responseText
            document.getElementById(element).innerHTML = response;
 		}
	}
    ajaxRequest.send(null);
} // End function xhr


function no_enter(e)
{
     var key;

     if(window.event)
          key = window.event.keyCode;     //IE
     else
          key = e.which;     //firefox

     if(key == 13)
          return false;
     else
          return true;
}

///////////////////////////////////////////////////////////////////////

function show_message (id, m)
{
	p = find_pos (document.getElementById(id));
	px = (p[0] + 25) + "px";
	py = (p[1] + 25) + "px";
	
	var b = document.getElementById("message");
    b.style.left = px;
	b.style.top = py;
	b.style.visibility = "visible";
    b.style.position = 'absolute';
    b.style.width = 'auto';
    b.style.height = 'auto';
		
	var c = "<div style='font-size: 0.75em; color: red; text-align: right;' >Click to close</div>";
	m = m + c;
	b.innerHTML = m;
} //End function showMessage
/////////////////////////////////////////////////////////////////////////////

function hide_message ()
{
	var b = document.getElementById("message")
	b.style.visibility = "hidden";
	b.style.height = "0px";
	b.style.width = "0px";
} //End function hide_message
/////////////////////////////////////////////////////////////////////////////

function show_list (obj)
{
    var p = find_pos (obj);
	var px = (p[0] + 25) + "px";
	var py = (p[1] + 25) + "px";

    var l = document.getElementById("list");
    l.style.visibility = "visible";
    l.style.left = px;
    l.style.top = py;
    l.style.height = "auto";
	l.style.width = "300px";

} //End function show_list

/////////////////////////////////////////////////////////////////////////////

function hide_list ()
{
	var l = document.getElementById("list")
	l.style.visibility = "hidden";
	l.style.height = "0px";
	l.style.width = "0px";
    l.style.innerHTML = "";
} //End function hideList

////////////////////////////////////////////////////////////////////////////////

function reset_form ()
{
	if (confirm("Reset the form?"))
	{
		document.form.reset();
	}
} // End functioformn resetForm

//////////////////////////////////////////////////////////////////////////
