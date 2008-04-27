//cashier.js

function get_accounts(thisObj, e)
{    
    // List all accounts that match a pattern
	var account_name = document.getElementById("account_name");
	var member_name = document.getElementById("member_name");
	
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
	
    var query = "cashier?search=accounts&string=" + account_name.value;

    xhr(query, 'list');
    show_list(thisObj);

} //End function get_accounts

////////////////////////////////////////////////////////////////////////

function get_account_members(e)
{
	// Get members that belong to an account
	var member_name = document.getElementById('member_name')
    var id_account = document.getElementById('id_account')

	hide_message();	
	
	if (!id_account.value)
	{
		show_message("member_name", "Please select an account first." )
	} else
	{
        hide_list();
       		
		var query = "cashier?search=members&account_id=" +
                    id_account.value;
		
        xhr(query, 'list');
        show_list(member_name);

	}
} // End function get_account_members

////////////////////////////////////////////////////////////////////////////////

function get_members(e)
{
	// List all members that match a pattern

    var member_name = document.getElementById('member_name')
    var id_member = document.getElementById('id_member')
    var id_account = document.getElementById('id_account')
	
	hide_message();
    hide_list();    

	// Try to check for the key
	if (!e) var e = window.event;
	if (e.keyCode) keycode = e.keyCode;
	else if (e.which) keycode = e.which;
		
	if(keycode == 8 )
	{
		//member.value = '';	
		id_member.value = '';
	}
		
	var query = "cashier?search=members&account_id=" +
                document.getElementById('id_account').value +
                "&string=" + member_name.value;
    
    xhr(query, 'list');
    show_list(member_name);

} // End function getMembers

////////////////////////////////////////////////////////////////////////

function set_account (this_obj)
{
	hide_list();
	hide_message();

	if (!this_obj.textContent) var account_name = this_obj.innerText;
	if (this_obj.textContent) var account_name = this_obj.textContent;
	id_account = this_obj.id
	document.getElementById("account_name").value = account_name;
	document.getElementById("id_account").value = id_account;
	get_account_members();
} // End function set_account

///////////////////////////////////////////////////////////////////////

function set_member (this_obj)
{      
	hide_list();
	hide_message();
    if ( this_obj.id == 'cancel')
    {
        member_name = '';
        id_member = '';
    }
    else
    {
        if (!this_obj.textContent) var member_name = this_obj.innerText;
	    if (this_obj.textContent) var member_name = this_obj.textContent;
	    id_member = this_obj.id;
    }
	document.getElementById("member_name").value = member_name;
	document.getElementById("id_member").value = id_member;
}

/////////////////////////////////////////////////////////////////////////////

function confirm_other_member (this_obj)
{
	hide_list();
	hide_message();

    account_name = document.getElementById("account_name").value;
    account_id = document.getElementById("id_account").value;
	if (!this_obj.textContent) var om_name = this_obj.innerText;
	if (this_obj.textContent) var om_name = this_obj.textContent;
    om_id = this_obj.id;

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
 
    var query = "cashier?search=other_member&account_name=" + account_name
                + "&account_id=" + id_account + "&om_name="
                + om_name + "&om_id=" + om_id; 

    xhr(query, 'message');

} // End function confirm_other_member 

/////////////////////////////////////////////////////////////////////////////

function set_other_member(this_obj, other_member_id, other_member_name)    
{
    hide_message();    
    if (!this_obj.textContent) var member_name = this_obj.innerText;
	if (this_obj.textContent) var member_name = this_obj.textContent;
	id_member = this_obj.id;
    set_note(id_member, member_name);
    document.getElementById("member_name").value = other_member_name;
	document.getElementById("id_member").value = other_member_id;

} //End function set_other_member

/////////////////////////////////////////////////////////////////////////////

function set_note (id_member, member_name)
{
	var old_note = "";
	var note = document.getElementById("id_note");
	if ( note.value )
	{
		old_note =  "; " + note.value;
	}
	var new_note = "Authorized by " + member_name + " (#" + id_member + ")" + old_note;
	note.value = new_note;
	
} //End function set_note

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
} // End function show_shadow

/////////////////////////////////////////////////////////////////////////////

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

///////////////////////////////////////////////////////////////////////


