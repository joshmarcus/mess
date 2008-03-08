//functions.js

function get_accounts(thisObj, e)
{    
    // List all accounts that match a pattern
	var account_name = document.getElementById("account_name");
	var member_name = document.getElementById("member_name");
	
	//hide_ring (account);
	//hide_ring (member);
	hide_message ();
		     
	// Try to check for the key
	if (!e) var e = window.event;
	if (e.keyCode) keycode = e.keyCode;
	else if (e.which) keycode = e.which;
	
	if(keycode == 8 )
	{
		member_name.value = '';	
        document.getElementById("id_account").value = '';
        document.getElementById("id_member").value = '';
	}
	
    var query = "cashier?search=getAccounts&string=" + account_name.value;

	ajaxRequest = xmlHttp();
	ajaxRequest.open("GET",query,true);

	ajaxRequest.onreadystatechange = function ()
	{
		if (ajaxRequest.readyState == 4 || ajaxRequest.status == 200 )
		{
            show_list (thisObj);	   
            var r = eval("(" + ajaxRequest.responseText + ")");
            var accounts = r['get_accounts'];
            responseString = "<div id='list_cancel' >Cancel</div>";
 			for ( key in accounts )
            {
                responseString += "<div class=list_choice " +
                                "onclick='set_account(" +
                                key + ", \"" + accounts[key] +
                                "\"); get_account_members(event);'>" +
                                accounts[key] + "</div>";
            }
            document.getElementById("list").innerHTML = responseString;
 		}
	}
    ajaxRequest.send(null);

} //End function get_accounts

////////////////////////////////////////////////////////////////////////

function get_members(e)
{
	// List all members that match a pattern

    var member_name = document.getElementById('member_name')
    var id_member = document.getElementById('id_member')
    var id_account = document.getElementById('id_account')
	
    //hide_ring (member);
	hide_message ();	
	//show_list (member)

		// Try to check for the key
		if (!e) var e = window.event;
		if (e.keyCode) keycode = e.keyCode;
		else if (e.which) keycode = e.which;
		
		if(keycode == 8 )
		{
			//member.value = '';	
			id_member.value = '';
		}
		
		var query = "cashier?search=getMembers&accountID=" +
                    document.getElementById('id_account').value +
                    "&string=" + member_name.value;
    
    ajaxRequest = xmlHttp();
	ajaxRequest.open("GET",query,true);

	ajaxRequest.onreadystatechange = function ()
	{
		if (ajaxRequest.readyState == 4 || ajaxRequest.status == 200 )
		{	
            var r = eval("(" + ajaxRequest.responseText + ")");
            var account_members = r['account_members'];
            var other_members = r['get_members'];

            response_string = "<div id='list_cancel' >Cancel</div>";
 			for ( key in account_members )
            {
                response_string += "<div class=list_choice onclick=\"set_member(" +
                                key + ", \'" + account_members[key] +
                                "\');\">" + account_members[key] + "</div>";
            }

            response_string += "<div class=other_choice>" +
                            "------------------- Other Members ----------" +
                                "</div>";
            
            var num_other_members = 0;

            for ( key in other_members )
            {
                num_other_members++;
                var name = other_members[key];
                response_string += "<div class=other_choice " +
                                "onclick=\"set_other_member(" + key + ", \'" +
                                name + "\')\">" + name + "</div>";
            }
            if (num_other_members == 0)
            {
                responseString += "<div class=list_choices>" +
                                "----------- Sorry No Matches ---------" +
                                "</div>";
            }

            document.getElementById("list").innerHTML = response_string;
             		}
	}
    ajaxRequest.send(null);

} // End function getMembers

////////////////////////////////////////////////////////////////////////

function get_account_members (e)
{
	// Get members that belong to an account
	var member_name = document.getElementById('member_name')
    var id_account = document.getElementById('id_account')

    //hide_ring (thisObj);
	hide_message ();	
	
	if (!id_account.value)
	{
		show_message ("member_name", "Please select an account first." )
	} else
	{
        hide_list ();
       		
		var query = "cashier?search=accountMembers&accountID=" +
                    id_account.value;
		
        ajaxRequest = xmlHttp();
        ajaxRequest.open("GET",query,true);

        ajaxRequest.onreadystatechange = function ()
        {
            if (ajaxRequest.readyState == 4 || ajaxRequest.status == 200 )
            {
                show_list (member_name);	   
                var r = eval("(" + ajaxRequest.responseText + ")");
                var account_members = r['account_members'];
                response_string = "<div id='list_cancel' >Cancel</div>";
                for ( i in account_members )
                {
                    response_string += "<div class=list_choice " +
                                    "onclick='set_member(" + i +
                                    ", \"" + account_members[i] + "\");'>" +
                                    account_members[i] + "</div>";
                }
                document.getElementById('list').innerHTML = response_string;
            }
        }
        ajaxRequest.send(null);
	}
} // End function get_mccount_members

////////////////////////////////////////////////////////////////////////////////

function set_account (id_account, account_name)
{
	hide_list ();
	hide_message ();
	document.getElementById("account_name").value = account_name;	
	document.getElementById("id_account").value = id_account;
} // End function setAccount

///////////////////////////////////////////////////////////////////////

function set_member (id_member, member_name)
{      
	hide_list ();
	hide_message ();
	document.getElementById("member_name").value = member_name;
	document.getElementById("id_member").value = id_member;
}

function set_other_member (id, member)
{
	hide_list ();
	hide_message ();

    account_name = document.getElementById("account_name").value;
	member_name = document.getElementById("member_name").value;
	id_member = document.getElementById("id_member").value;
	
	p = find_pos (member);
	px = (p[0] + 25) + "px";
	py = (p[1] + 25) + "px";
	
	var m = document.getElementById("message");
	m.style.visibility = "visible";
	m.style.position = "absolute";
	m.style.left = px;
	m.style.top = py;
    m.style.width = "auto";
	m.style.height = "auto";
	m.style.textAlign =  "center";

	var message = "Which member from "
				  + " <span style='color: red;'>"
				  + account_name.value + "<br /></span>"
				  + " is authorizing this transaction by "
				  + "<br /><span style='color: red;'>"
				  + member_name + "</span>?";
	
	var query = "confirmMember.php"
    query += "?memberID=" + id_account + "&id=" + id + "&name=" + member;
	
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

function set_type (ps, type, tName)
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


function make_it_so()
{
m = "1. Further validate transaction with php. <br />\
	2. If it's all okie dokie insert into table"
	
	showMessage ("form", m)
}

function show_ring(r)
{
	r.style.outline = "solid red 1.5px";
	r.style.outlineOffset = "2px";
	r.style.MozOutlineRadius = "30px";
}

////////////////////////////////////////////////////////////////////////

function hide_box (box)
{
	box.style.visibility = "hidden";
	box.style.height = "0px";
	box.style.width = "0px";
} //End function hideBox
////////////////////////////////////////////////////////////////////////////////

function show_list (obj)
{
    var p = find_pos (obj);
	var px = (p[0] + 25) + "px";
	var py = (p[1] + 25) + "px";

    var l = document.getElementById("list");
    l.style.visibility = "visible";
    l.style.left = px;
    l.style.top = py;
}

function show_shadow ()
{
    var l = document.getElementById("list");
    var p = find_pos (l);
	var px = (p[0] + 15) + "px";
	var py = (p[1] + 15) + "px";

    var s = document.getElementById("listShadow");
	s.style.visibility = "visible";
	s.style.left =  px;
	s.style.top =  py;
	s.style.width = l.style.width;
    s.style.height = l.outerHeight;
}

function hide_list ()
{
	var l = document.getElementById("list")
	l.style.visibility = "hidden";
	l.style.height = "0px";
	l.style.width = "0px";
    l.style.innerHTML = "";
} //End function hideList
////////////////////////////////////////////////////////////////////////////////

function hide_money ()
{
	var b = document.getElementById("money")
	b.style.visibility = "hidden";
	b.style.height = "0px";
	b.style.width = "0px";
} //End function hideList
////////////////////////////////////////////////////////////////////////////////

function hide_hint ()
{
	var b = document.getElementById("hint")
	b.style.visibility = "hidden";
	b.style.height = "0px";
	b.style.width = "0px";
} //End function hideList
////////////////////////////////////////////////////////////////////////////////

function hide_ring(r)
{
	r.style.outline = "0px";
}

function set_note (id, name)
{
	var oldNote = "";
	var note = document.getElementById("note");
	if (note.value)
	{
		oldNote =  "; " + note.value;
	}
	var newNote = "Authorized by " + name + "(#" + id + ")" + oldNote;
	document.getElementById("note").value = newNote;
	
} //End function setNotea

function list_type ( thisObj, e, type)
{
	hideMoney ();
	hide_message ();
	
	//document.getElementById("table").background = "#000000";
	
	var l = document.getElementById("list");
	
	var obj = document.getElementById("credit_type");
	
	var p = find_pos (thisObj);
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


