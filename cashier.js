//functions.js


function testStuff ()
{
	document.write("Hellllo");
}

function listType ( thisObj, e, type)
{
	hideMoney ();
	hideMessage ();
	
	document.getElementById("table").background = "#000000";
	
	var l = document.getElementById("list");
	
	var obj = document.getElementById("payLabel");
	
	var p = findPos (thisObj);
	var px = p[0] + "px";
	var py = p[1] + "px";
	
	
	l.style.visibility = "visible";
	l.style.position = "absolute";
	l.style.left = px;
	l.style.top = py;
	l.style.width = "200px";
	
	var url = "listTransType.php"
	var string = obj.value
	var query = url + "?ps=" + type;
	
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
 			l.innerHTML = ajaxRequest.responseText; 
 		}
	}
	ajaxRequest.send(null);
	
} // End function listType


///////////////////////////////////////////////////////////////////////

function listAccounts(thisObj, e)
{
	// List all accounts that match a pattern
	
	var aName = document.getElementById("aName")
	var fName = document.getElementById("fName")
	hideRing (aName);
	hideRing (fName);
	hideMessage ();
	
	p = findPos (thisObj);
	px = (p[0] + 25) + "px";
	py = (p[1] + 25) + "px";
	 
	l = document.getElementById("list");
	l.style.visibility = "visible";
	l.style.position = "absolute";
	l.style.left = px;
	l.style.top = py;
	l.style.width = "300px";	
	
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
	var string = aName.value
	var query = url + "?string=" + string;

	ajaxRequest = xmlHttp();
	ajaxRequest.open("GET",query,true);
	
	ajaxRequest.onreadystatechange = function ()
	{
		if (ajaxRequest.readyState == 4 || ajaxRequest.status == 200 )
		{
 			l.innerHTML = ajaxRequest.responseText; 
 		}
	}
	ajaxRequest.send(null);
	
} //End function getAccount

////////////////////////////////////////////////////////////////////////

function listMembers (e)
{
	// List all members that match a pattern

	var fName = document.getElementById("fName")
	hideRing (fName);
	hideMessage ();	
	
		p = findPos (fName);
		px = (p[0] + 25) + "px";
		py = (p[1] + 25) + "px";
		
		l = document.getElementById("list");
		l.style.visibility = "visible";
		l.style.position = "absolute";
		l.style.left = px;
		l.style.top = py;
		l.style.width = "300px";
		
			// Try to check for the key
		if (!e) var e = window.event;
		if (e.keyCode) keycode = e.keyCode;
		else if (e.which) keycode = e.which;
		
		if(keycode == 8 )
		{
			//document.getElementById("fName").value = '';	
			document.getElementById("mID").value = '';
		}
		
		var url = "autoMember.php"
		var string = document.getElementById("fName").value
		var aid = document.getElementById("aID").value
		var query = url + "?aID=" + aid + "&string=" + string;
		
		ajaxRequest = xmlHttp();
		ajaxRequest.open("GET",query,true);
		
		ajaxRequest.onreadystatechange = function ()
		{
			if (ajaxRequest.readyState == 4 || ajaxRequest.status == 200 )
			{
				l.innerHTML = ajaxRequest.responseText; 
			}
		}
		ajaxRequest.send(null);
	
} // End function listMembers

////////////////////////////////////////////////////////////////////////

function getMembers (e)
{
	// Get members that belong to an account
	var fName = document.getElementById("fName")
	
	hideRing (fName);
	hideMessage ();	
	
	if (!document.getElementById("aID").value)
	{
		showMessage ("fName", "Please select an account first." )
	} else
	{
		p = findPos (fName);
		px = (p[0] + 25) + "px";
		py = (p[1] + 25) + "px";
		
		l = document.getElementById("list");
		l.style.visibility = "visible";
		l.style.position = "absolute";
		l.style.left = px;
		l.style.top = py;
		l.style.width = "300px";
		
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
				l.innerHTML = ajaxRequest.responseText; 
			}
		}
		ajaxRequest.send(null);
	}
	
} // End function getMembers

////////////////////////////////////////////////////////////////////////////////

function setAccount (id, name)
{
	hideList ();
	hideMessage ();
	
	document.getElementById("aName").style.outline = "0px";	
	document.getElementById("aName").value = name;	
	document.getElementById("aID").value = id;
}
///////////////////////////////////////////////////////////////////////

function setMember (id, name)
{
	hideList ();
	hideMessage ();

	//document.getElementById("fName").style.outline = "0px";	
	document.getElementById("fName").value = name;	
	document.getElementById("mID").value = id;
}

function setOtherMember (id, name)
{
	
	hideList ();
	hideMessage ();
	
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
	list = document.getElementById("list");
	list.style.visibility = "hidden";
	list.style.height = "0px";
	list.style.width = "0px";
	
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

	if (!aID.value)
	{
		showRing (aName);
		m = m + "No account selected!<br />";
	}
	
	if (!mID.value)
	{
		showRing (fName);
		m = m + "No member selected!<br />";
	}
	
	if (!pay.value && !payAmt.value && !saleAmt.value)
	{		
		moneyBox ();
		m  = m + "No Purchase or Payment Information!<br />";
	}
	
	if (!sale.value && !sale.value)
	{
		showRing (saleAmt);
		m  = m + "No Purchase Amount!<br />";
	}
		
	if (pay.value && !payAmt.value)
	{
		showRing (payAmt);
		m  = m + "No Payment Amount!<br />";
	}
	 
	if (!pay.value && payAmt.value)
	{
		showRing (payAmt);
		m  = m + "No Payment Type!<br />";
	}
	 
	if(m)
	{
		//message.
		var h = "<span style='font-size: 1.25em' \
				>Corrections Needed!</span><br />";
		m = h + m
		showMessage ("note", m)
	} else (!m)
	{
		//~ m = "<div style='font-size: 1.0em; \
			//~ text-align: center;'>Please Confirm Transactions</div><br />";
		
		m = m + "<table style ='width: 100%;' >";
		m = m + "<tr><th style ='width: 10%;'> \
				Account:</th> \
				<td style ='width: 40%;'><span style='font-size: 1.75em;'>";
		m = m + aName.value + "</span></td>";
		
		m = m + "<th style ='width: 10%;'> \
				Member:</th > \
				<td style ='width: 40%;'><span style='font-size: 1.75em;'>";
		m = m + fName.value + "</span></td></tr>";
		
		m = m + "<tr><th style ='width: 10%;'>Purchase:</th> \
				<td style ='width: 20%;' ><span style='font-size: 1.75em;'>";
		m = m + saleAmt.value + "</span></td>";
		
		m = m + "<th style ='width: 10%;'>Note</th> \
				<td style ='width: 60%;'><span style='font-size: 1.75em;'>";
		m = m + note.value + "</span></td>"
		
		m = m + "<tr>";
		m = m + "<th style ='width: 10%;'>Payment</th> \
				<td style ='width: 20%;'><span style='font-size: 1.75em;'>";
		m = m + payAmt.value + "</span></td></tr>";
		
		m = m + "<th style ='width: 10%;'>Ref:</th> \
				<td ><span style='font-size: 1.75em;'>";
		m = m + ref.value + "</span></td></tr>";
		m = m + "</table>";
		  
		showMessage ("form", m);
	}
	
} 

function showRing(r)
{
	r.style.outline = "solid red 1.5px";
	r.style.outlineOffset = "2px";
	r.style.MozOutlineRadius = "30px";
}

////////////////////////////////////////////////////////////////////////

function hideBox (box)
{
	box.style.visibility = "hidden";
	box.style.height = "0px";
	box.style.width = "0px";
} //End function hideBox
////////////////////////////////////////////////////////////////////////////////

function hideList ()
{
	var b = document.getElementById("list")
	b.style.visibility = "hidden";
	b.style.height = "0px";
	b.style.width = "0px";
} //End function hideList
////////////////////////////////////////////////////////////////////////////////

function hideMoney ()
{
	var b = document.getElementById("money")
	b.style.visibility = "hidden";
	b.style.height = "0px";
	b.style.width = "0px";
} //End function hideList
////////////////////////////////////////////////////////////////////////////////

function hideHint ()
{
	var b = document.getElementById("hint")
	b.style.visibility = "hidden";
	b.style.height = "0px";
	b.style.width = "0px";
} //End function hideList
////////////////////////////////////////////////////////////////////////////////

function hideRing(r)
{
	r.style.outline = "0px";
}

function setNote (id, name)
{
	var oldNote = "";
	var note = document.getElementById("note");
	if (note.value)
	{
		oldNote =  "; " + note.value;
	}
	var newNote = "(#" + id + ")" + name + oldNote;
	document.getElementById("note").value = newNote;
	
} //End function setNote
