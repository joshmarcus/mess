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
            var response = "<div id='list_cancel' onclick="
                            + "\"set_account('','');\" >Cancel</div>";
 			
            var num_accounts = 0;
            for ( key in accounts )
            {
                num_accounts++;
                response += "<div class=list_choice onclick=\'set_account("
                            + key + ", \"" + accounts[key] + "\");"
                            + " get_account_members(event);\'>"
                            + accounts[key] + "</div>";
            }
            if (num_accounts == 0)
            {
                response += "<div class=list_choices>" +
                            "------ Sorry No Matches ---------" +
                                "</div>";
            }

            document.getElementById("list").innerHTML = response;
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
	hide_message();	
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

            var response = "<div id=list_cancel onclick=\"set_member('','');\""
                            + " >Cancel</div>";
 			for ( key in account_members )
            {
                response += "<div class=list_choice onclick=\"set_member(" +
                                key + ", \'" + account_members[key] +
                                "\');\">" + account_members[key] + "</div>";
            }

            response += "<div class=other_choice>"
                        + "----  Other Members ----------</div>";
            
            var num_other_members = 0;

            for ( key in other_members )
            {
                num_other_members++;
                var name = other_members[key];
                response += "<div class=other_choice onclick="
                                + "\"confirm_other_member(" + key + ", \'"
                                + name + "\')\">" + name + "</div>";
            }
            if (num_other_members == 0)
            {
                response += "<div class=other_choices>"
                            + "----------- Sorry No Matches ---------</div>";
            }

            document.getElementById("list").innerHTML = response;
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
	hide_message();	
	
	if (!id_account.value)
	{
		show_message("member_name", "Please select an account first." )
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
                var response = "<div id='list_cancel' onclick=\"set_member"
                                + "('','');\" >Cancel</div>";
                for ( i in account_members )
                {
                    response += "<div class=list_choice onclick='set_member("
                                + i + ", \"" + account_members[i] + "\");'>"
                                + account_members[i] + "</div>";
                }
                document.getElementById('list').innerHTML = response;
            }
        }
        ajaxRequest.send(null);
	}
} // End function get_account_members

////////////////////////////////////////////////////////////////////////////////

function set_account (id_account, account_name)
{
	hide_list();
	hide_message();
	document.getElementById("account_name").value = account_name;	
	document.getElementById("id_account").value = id_account;
} // End function set_account

///////////////////////////////////////////////////////////////////////

function set_member (id_member, member_name)
{      
	hide_list ();
	hide_message ();
	document.getElementById("member_name").value = member_name;
	document.getElementById("id_member").value = id_member;
}

/////////////////////////////////////////////////////////////////////////////

function confirm_other_member (id_other, other_name)
{
	hide_list();
	hide_message();

    account_name = document.getElementById("account_name").value;
	
	p = find_pos('member_name');
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
    m.style.fontSize = "1.25em";

	var message = "Which member from<br /> "
				  + " <span style='color: red;'>"
				  + account_name + "<br /></span>"
				  + " is authorizing this transaction by<br /> "
				  + "<span style='color: red;'>"
				  + other_name + "</span>?";
	
    var query = "cashier?search=accountMembers&accountID=" +
                    document.getElementById("id_account").value;
	
	ajaxRequest = xmlHttp();
	ajaxRequest.open("GET",query,true);
	
	ajaxRequest.onreadystatechange = function ()
	{
		if (ajaxRequest.readyState == 4 || ajaxRequest.status == 200 )
		{
            var r = eval("(" + ajaxRequest.responseText + ")");
            var account_members = r['account_members'];
            var response = message;
 			for ( key in account_members )
            {
                response += "<div class=confirm_member "
                            + "onclick=\"set_other_member(" + key
                            + ", \'" + account_members[key] + "\', " + id_other
                            + ", \'" + other_name + "\');\">"
                            + account_members[key] + "</div>";
            }
            response += "<div class='confirm_member' "
                        + " onclick=\"set_member('', '');\" >"
                        + "No one, please cancel!</div>";
            m.innerHTML = response;
 		}
	}
	ajaxRequest.send(null);
	
} // End function confirm_other_member 

/////////////////////////////////////////////////////////////////////////////

function set_other_member(id_member, member_name, id_other, other_name)
{
    set_member(id_other, other_name);
    set_note(id_member, member_name);
}

/////////////////////////////////////////////////////////////////////////////

function set_note (id_other, other_name)
{
	var old_note = "";
	var note = document.getElementById("id_note");
	if ( note.value )
	{
		old_note =  "; " + note.value;
	}
	var new_note = "Authorized by " + other_name + " (#" + id_other + ")" + old_note;
	note.value = new_note;
	
} //End function set_note

/////////////////////////////////////////////////////////////////////////////

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


function hide_money ()
{
	var b = document.getElementById("money")
	b.style.visibility = "hidden";
	b.style.height = "0px";
	b.style.width = "0px";
} //End function hideList
/////////////////////////////////////////////////////////////////////////////

function hide_hint ()
{
	var b = document.getElementById("hint")
	b.style.visibility = "hidden";
	b.style.height = "0px";
	b.style.width = "0px";
} //End function hideList

/////////////////////////////////////////////////////////////////////////////

function hide_ring(r)
{
	r.style.outline = "0px";
}

/////////////////////////////////////////////////////////////////////////////

function list_type ( this_obj, e, type)
{
	hideMoney();
	hide_message();
	
	//document.getElementById("table").background = "#000000";
	
	var l = document.getElementById("list");
	
	//var obj = document.getElementById("credit_type");
	
	var p = find_pos (this_obj);
	var px = p[0] + "px";
	var py = p[1] + "px";
	
	
	l.style.visibility = "visible";
	l.style.position = "absolute";
	l.style.left = px;
	l.style.top = py;
	l.style.width = "200px";
    
    if ( this_obj.id == 'credit_type' )
    {
        type = 'credit';
    }
    else if (this_obj == 'debit_type' )
    {
       type = 'debit';
    }
    var query = "cashier?list=" + list_type;

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


