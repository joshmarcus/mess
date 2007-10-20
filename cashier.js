//functions.js


function testStuff ()
{
	document.write("Hellllo");
}

function listType ( thisObj, e, type)
{
	
	document.getElementById("table").background = "#000000";
	
	var listBox = document.getElementById("listType");
	
	var obj = document.getElementById("payLabel");
	
	var p = findPos (thisObj);
	var px = p[0] + "px";
	var py = p[1] + "px";
	
	var url = "listTransType.php"
	var string = obj.value
	var query = url + "?ps=" + type;
	
	listBox.style.visibility = "visible";
	listBox.style.position = "absolute";
	listBox.style.left = px;
	listBox.style.top = py;
	listBox.style.width = "200px";
	
		// Try to check for the key
	if (!e) var e = window.event;
	if (e.keyCode) keycode = e.keyCode;
	else if (e.which) keycode = e.which;
	
	ajaxRequest = xmlHttp();
	ajaxRequest.open("GET",query,true);
	
	ajaxRequest.onreadystatechange = function ()
	{
		if (ajaxRequest.readyState == 4 || ajaxRequest.status == 200)
		{ 
 			listBox.innerHTML = ajaxRequest.responseText; 
 		}
	}
	ajaxRequest.send(null);
	
} // End function getTransType


///////////////////////////////////////////////////////////////////////

function listAccounts(thisObj, e)
{
	// List all accounts that match a pattern
	
	p = findPos (thisObj);
	px = (p[0] + 25) + "px";
	py = (p[1] + 25) + "px";
	 
	listBox = document.getElementById("listNames");
	listBox.style.visibility = "visible";
	listBox.style.position = "absolute";
	listBox.style.left = px;
	listBox.style.top = py;
	listBox.style.width = "300px";	
	
	// Try to check for the key
	if (!e) var e = window.event;
	if (e.keyCode) keycode = e.keyCode;
	else if (e.which) keycode = e.which;
	
	if(keycode == 8 )
	{
		document.getElementById("fName").value = '';	
		document.getElementById("mID").value = '';
		document.getElementById("aID").value = '';
	}
	
	var url = "autoAccount.php"
	var string = document.getElementById("aName").value
	var query = url + "?string=" + string;

	ajaxRequest = xmlHttp();
	ajaxRequest.open("GET",query,true);
	
	ajaxRequest.onreadystatechange = function ()
	{
		if (ajaxRequest.readyState == 4 || ajaxRequest.status == 200 )
		{
 			listBox.innerHTML = ajaxRequest.responseText; 
 		}
	}
	ajaxRequest.send(null);
	
} //End function getAccount

////////////////////////////////////////////////////////////////////////


function listMembers (e)
{
	// List all members that match a pattern
	
	p = findPos (document.getElementById("fName"));
	px = (p[0] + 25) + "px";
	py = (p[1] + 25) + "px";
	
	listBox = document.getElementById("listMembers");
	listBox.style.visibility = "visible";
	listBox.style.position = "absolute";
	listBox.style.left = px;
	listBox.style.top = py;
	listBox.style.width = "300px";
	
		// Try to check for the key
	if (!e) var e = window.event;
	if (e.keyCode) keycode = e.keyCode;
	else if (e.which) keycode = e.which;
	
	if(keycode == 8 )
	{
		document.getElementById("fName").value = '';	
		document.getElementById("mID").value = '';
	}
	
	var url = "autoMember.php"
	var string = document.getElementById("fName").value
	var aid = document.getElementById("aID").value
	var query = url + "?aID=" + aid + "&string=" + string;
	
	//document.getElementById("listNames").innerHTML=query;
	//document.getElementById("listNames").innerHTML=query;

	ajaxRequest = xmlHttp();
	ajaxRequest.open("GET",query,true);
	
	ajaxRequest.onreadystatechange = function ()
	{
		if (ajaxRequest.readyState == 4 || ajaxRequest.status == 200 )
		{
 			listBox.innerHTML = ajaxRequest.responseText; 
 		}
	}
	ajaxRequest.send(null);
	
} // End function listMembers

////////////////////////////////////////////////////////////////////////

function getMembers (e)
{
	//hideBox (document.getElementById("message"))
	// Get members that belong to an account
	
	p = findPos (document.getElementById("fName"));
	px = (p[0] + 25) + "px";
	py = (p[1] + 25) + "px";
	
	listBox = document.getElementById("listMembers");
	listBox.style.visibility = "visible";
	listBox.style.position = "absolute";
	listBox.style.left = px;
	listBox.style.top = py;
	listBox.style.width = "300px";
	
	var url = "autoMember.php"
	var aid = document.getElementById("aID").value
	var query = url + "?aID=" + aid;
	
	//document.getElementById("listNames").innerHTML=query;
	//document.getElementById("listNames").innerHTML=query;

	ajaxRequest = xmlHttp();
	ajaxRequest.open("GET",query,true);
	
	ajaxRequest.onreadystatechange = function ()
	{
		if (ajaxRequest.readyState == 4 || ajaxRequest.status == 200 )
		{
 			listBox.innerHTML = ajaxRequest.responseText; 
 		}
	}
	ajaxRequest.send(null);
	
} // End function getMembers

////////////////////////////////////////////////////////////////////////////////

function setAccount (id, name)
{
	hideBox (document.getElementById("listNames"));
	hideBox (document.getElementById("listMembers"));
	
	document.getElementById("aName").style.outline = "0px";	
	document.getElementById("aName").value = name;	
	document.getElementById("aID").value = id;
}
///////////////////////////////////////////////////////////////////////

function setMember (id, name)
{
	hideBox(document.getElementById("message"));
	hideBox(document.getElementById("listMembers"));

	document.getElementById("fName").style.outline = "0px";	
	document.getElementById("fName").value = name;	
	document.getElementById("mID").value = id;
}

function setOtherMember (id, name)
{
	
	//close and hide the member list
	hideBox (document.getElementById("listMembers"))
	
	p = findPos (document.getElementById("fName"));
	px = (p[0] + 25) + "px";
	py = (p[1] + 25) + "px";
	
	var aName = document.getElementById("aName").value;
	
	var b = document.getElementById("message");
	b.style.visibility = "visible";
	b.style.position = "absolute";
	b.style.left = px;
	b.style.top = py;
	b.style.width = "auto";
	b.style.height = "auto";
	b.style.padding = "20px";
	b.style.background = "#cc9999";
	b.style.color = "#003333";
	b.style.border = "solid red 1px";
	b.style.MozBorderRadiusTopright = "0px";
	b.style.MozBorderRadiusTopright = "15px";
	b.style.MozBorderRadiusBottomleft = "15px";
	b.style.MozBorderRadiusBottomright = "30px";
	b.style.fontSize = "1.5em";
	b.style.textAlign =  "center";

	var message = "Which member from "
				  + " <span style='color: red;'>"
				  +aName + "<br /></span>"
				  + " is authorizing this transaction by "
				  + "<br /><span style='color: red;'>"
				  + name + "</span>?";
	
	var url = "confirmMember.php"
	var aid = document.getElementById("aID").value
	var query = url + "?aID=" + aid + "&id=" + id + "&name=" + name;
	
	ajaxRequest = xmlHttp();
	ajaxRequest.open("GET",query,true);
	
	ajaxRequest.onreadystatechange = function ()
	{
		if (ajaxRequest.readyState == 4 || ajaxRequest.status == 200 )
		{
 			b.innerHTML = message + ajaxRequest.responseText; 
 		}
	}
	ajaxRequest.send(null);
	
} // End function setOtherMember 


/////////////////////////////////////////////////////////////////////////////////

function setType (ps, type, tName)
{
	acObject = document.getElementById("listType");
	acObject.style.visibility = "hidden";
	acObject.style.height = "0px";
	acObject.style.width = "0px";
	
	document.getElementById("payLabel").style.outline = "0px";
	document.getElementById("saleLabel").style.outline = "0px";	
	
	switch (ps)
	{
	case 's': document.getElementById("saleLabel").innerHTML = tName;
        	  document.getElementById("sale").value = type;
		  document.getElementById("TEST").innerHTML = type;
	break;
	case 'p': document.getElementById("payLabel").innerHTML = tName;
		  document.getElementById("pay").value = type;
	break;
	case 'a': document.getElementById("tName").innerHTML = tName;
		  document.getElementById("xType").value = type;
	break;
	}
}

///////////////////////////////////////////////////////////////////////

function validate ()
{	
	var m = '';
	
	var aID = document.getElementById("aID");
	var aName = document.getElementById("aName");
	var mID = document.getElementById("mID");
	var fName = document.getElementById("fName");
	
	var sale = document.getElementById("sale");
	var saleAmt = document.getElementById("saleAmt");
	var pay = document.getElementById("pay");
	var payAmt = document.getElementById("payAmt");
	
	var ref = document.getElementById("ref");
	var note = document.getElementById("note");

	function moneyBox ()
	{
		p = findPos (document.getElementById("payLabel"));
		px = (p[0] + 10) + "px";
		py = (p[1] - 5) + "px";
		
		var money = document.getElementById("money");
		money.style.position = "absolute";
		money.style.left = px;
		money.style.top = py;
		money.style.width = "220px";
		money.style.height = "65px";
		money.style.outline = "solid red 1.5px";
		money.style.outlineOffset = "2px";
		money.style.MozOutlineRadius = "30px";
	}

	if (!aID.value && !mID.value && !saleAmt)
	{
		aName.style.outline = "solid red 1.5px";
		aName.style.outlineOffset = "2px";
		aName.style.MozOutlineRadius = "30px";
		
		m = "No account selected!<br />";
	}
	
	if (!mID.value)
	{
		fName.style.outline = "solid red 1.5px";
		fName.style.outlineOffset = "2px";
		fName.style.MozOutlineRadius = "30px";
		
		m = "No member selected!<br />";
	}
	
	if (!saleAmt.value && !payAmt.vaule && !pay.value)
	{
		/*
		saleAmt.style.outline = "solid red 1.5px";
		saleAmt.style.outlineOffset = "2px";
		saleAmt.style.MozOutlineRadius = "30px";
		
		payLabel.style.outline = "solid red 1.5px";
		payLabel.outlineOffset = "2px";
		payLabel.MozOutlineRadius = "30px";
		
		payAmt.style.outline = "solid red 1.5px";
		payAmt.style.outlineOffset = "2px";
		payAmt.style.MozOutlineRadius = "30px";
		*/
		
		moneyBox ();
		m  = m + "No Sale or Payment Informaion!<br />";
	}
	
	if(m)
	{
		p = findPos (document.getElementById("note"));
		px = (p[0] + 25) + "px";
		py = (p[1] + 25) + "px";
	
	var b = document.getElementById("message");
	b.style.visibility = "visible";
	b.style.position = "absolute";
	b.style.left = px;
	b.style.top = py;
	b.style.width = "auto";
	b.style.height = "auto";
	b.style.padding = "20px";
	b.style.background = "#cc9999";
	b.style.color = "#003333";
	b.style.border = "solid red 1px";
	b.style.MozBorderRadiusTopright = "0px";
	b.style.MozBorderRadiusTopright = "15px";
	b.style.MozBorderRadiusBottomleft = "15px";
	b.style.MozBorderRadiusBottomright = "30px";
	b.style.fontSize = "1.5em";
	b.style.textAlign =  "center";

		//message.
		var h = "<span style='font-size: 1.25em'>Corrections Needed!</span><br />";
		var c = "<div style='color: red; text-align: right;' >Click to close</div>";
		m = h + m + c
		b.innerHTML = m;
	}
	
} 

////////////////////////////////////////////////////////////////////////

function hideBox (box)
{
	box.style.visibility = "hidden";
	box.style.height = "0px";
	box.style.width = "0px";
} //End function hideBox
////////////////////////////////////////////////////////////////////////////////

function setNote (id, name)
{
	var oldNote;
	var note = document.getElementById("note");
	if (note.value)
	{
		oldNote =  "; " + note.value;
	}
	var newNote = "(#" + id + ")" + name + oldNote;
	document.getElementById("note").value = newNote;
	
} //End function setNote
