//functions.js


function testStuff () {
	document.write("Hellllo");
}

function findPos(obj) {
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


function xmlHttp() {
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

function noEnter(e)
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
