//functions.js

function find_pos(obj)
{
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
		alert ("Browser does not support XML HTTP Request")
  		return
 	} 
 	
	return xmlHttp;
} // End function xmlHttp

////////////////////////////////////////////////////////////////////////

function xhr(query, element)
{
    var ajaxRequest = xmlHttp();
	ajaxRequest.open("GET",query,true);

	ajaxRequest.onreadystatechange = function ()
	{
		if (ajaxRequest.readyState == 4)
        {
            if (ajaxRequest.status == 200 || ajaxRequest.status == 304 )
	        {	   
	            var response = ajaxRequest.responseText
                document.getElementById(element).innerHTML = response;
 		    }
        }
	}
    ajaxRequest.send(null);
} // End function xhr

/////////////////////////////////////////////////////////////////////////////

//function is_available(element, do_it)
//{
//    var timeout;
//    var do_it;
//    function not_available()
//    {
//        if ( !document.getElementById('element'))
//        {
//            //alert(document.getElementById('element'))
//            timeout = setTimeout("not_available()", 0);
//        }
//        else
//        {
//            //alert("do it" + document.getElementById('element'));
//            do_it;
//        }
//
//    }
//    clearTimeout(timeout)
//} //End function is_available


/////////////////////////////////////////////////////////////////////////////


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

// Some functions take an object, while some functions take an ID and 
// use getElementById to find the object themselves...  --Paul 8/5/08

function show_message (id, m)
{
	p = find_pos (document.getElementById(id));
	px = (p[0] + 25) + "px";
	py = (p[1] + 25) + "px";
	
	var b = document.getElementById("message");
    b.style.left = px;
	b.style.top = py;
    b.style.position = 'absolute';
    b.style.width = 'auto';
    b.style.height = 'auto';
		
	var c = "<div style='font-size: 0.75em; color: red; text-align: right;' >Click to close</div>";
	m = m + c;
	b.innerHTML = m;
    b.style.display = 'inline';
    b.onclick = hide_message;

} //End function show_message
/////////////////////////////////////////////////////////////////////////////

function hide_message ()
{
	document.getElementById("message").style.display = "none";   
} //End function hide_message

/////////////////////////////////////////////////////////////////////////////

function show_list (obj)
{
    var p = find_pos (obj);
	var px = (p[0] + 25) + "px";
	var py = (p[1] + 25) + "px";

    var l = document.getElementById("list");
    l.style.left = px;
    l.style.top = py;
    l.style.height = "auto";
    l.style.display = 'inline';

} //End function show_list

/////////////////////////////////////////////////////////////////////////////

function hide_list()
{
	document.getElementById("list").style.display = "none";        
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
