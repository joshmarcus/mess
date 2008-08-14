//cashier.js

// Hide elements that aren't used yet
function hide_unused_elements()
{
    document.getElementById("member").style.display = 'none';
    document.getElementById("ref").style.display = 'none';
    document.getElementById("credit").style.display = 'none';
    document.getElementById("debit").style.display = 'none';
}

function get_accounts(thisObj, e)
{    
    // List all accounts that match a pattern
	var account_name = document.getElementById("account_name");
	var member_name = document.getElementById("member_name");
	
	hide_message ();
		     
	// Try to check for the key
	if (!e) var e = window.event;
	if (e.keyCode) var keycode = e.keyCode;
	else if (e.which) var keycode = e.which;
	
	if(keycode == 8 )
	{
		member_name.value = '';	
        document.getElementById("id_account").value = '';
        document.getElementById("id_member").value = '';
	    document.getElementById("member").style.display = "none";
	}
	if (account_name.value.length > 0)
    {
        var query = "?search=accounts&string=" + account_name.value;

        xhr(query, 'list');
        YAHOO.util.Event.onAvailable('account_list',
                                    account_list_click, this, true); 
        show_list(thisObj);
        //setTimeout('account_list_click()', 100);
    }

} //End function get_accounts

////////////////////////////////////////////////////////////////////////

function get_account_members()
{
	// Get members that belong to an account
	var member_name = document.getElementById('member_name')
    var id_account = document.getElementById('id_account')

	hide_message();	
	
	//if (!id_account.value)
	//{
	//	show_message("member_name", "Please select an account first." )
	//} else
	//{
        hide_list();
       		
		var query = "?search=members&account_id=" +
                    id_account.value;
		
        xhr(query, 'list');
        YAHOO.util.Event.onAvailable('account_members',
                                    account_members_click, this, true);
        show_list(member_name);
        //setTimeout('account_members_click()', 100);
	//}
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
		
	var query = "?search=members&account_id=" +
                document.getElementById('id_account').value +
                "&string=" + member_name.value;
    
    xhr(query, 'list');
        YAHOO.util.Event.onAvailable('other_members',
                                other_members_click, this, true); 
    show_list(member_name);
    //setTimeout('other_members_click()', 100);

} // End function getMembers

////////////////////////////////////////////////////////////////////////

function set_account(this_obj)
{
	hide_list();
	//hide_message();
    if ( this_obj.id == 'list_cancel')
    {
        account_name = '';
        id_account = '';
        display = 'none';

    }
    else
    {
        if (!this_obj.textContent) var account_name = this_obj.innerText;
	    if (this_obj.textContent) var account_name = this_obj.textContent;
    	id_account = this_obj.id;
        display = 'inline';
    }
	document.getElementById("account_name").value = account_name;
	document.getElementById("id_account").value = id_account;
	document.getElementById("member").style.display = display;
    
} // End function set_account

///////////////////////////////////////////////////////////////////////

function get_transactions(id)
{
    var query = "?search=transactions"
    if (id == parseInt(id))
    {  
        query += "&account_id=" + document.getElementById('id_account').value
    }
    xhr(query,'transactions');
} // End function get_transactions

/////////////////////////////////////////////////////////////////////////////

function set_member(this_obj)
{      
	hide_list();
	hide_message();
    if ( this_obj.id == 'list_cancel')
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

function confirm_other_member(this_obj)
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
	//m.style.visibility = "visible";
	m.style.position = "absolute";
	m.style.left = px;
	m.style.top = py;
    m.style.width = "auto";
	m.style.height = "auto";
	m.style.textAlign =  "center";
    m.style.fontSize = "1.25em";
    m.style.display = "inline";
 
    var query = "?search=other_member&account_name=" + account_name
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

function list_cancel_click()
{
    if (document.getElementById('list_cancel'))
    {
        document.getElementById('list_cancel').onclick = function()
            {
                hide_list();
                set_account(this);
            }
    }
} // End function list_cancel_onclick

/////////////////////////////////////////////////////////////////////////////

function account_list_click()
{
    if (document.getElementById && document.getElementsByTagName)
    {
        if (document.getElementById('account_list'))
        {
            list_cancel_click();
            var list = document.getElementById('account_list');
            var item = list.getElementsByTagName('li');
            for( var i=0; i < item.length; i++ )
            {
                item[i].onclick = function()
                    {
                        hide_list();
                        set_account(this);
                        get_account_members();
                        get_transactions(i);                        
                    }
            }
        }
    }
} // End function account_list_onclick

/////////////////////////////////////////////////////////////////////////////

function account_members_click()
{
    if (document.getElementById && document.getElementsByTagName)
    {
        if (document.getElementById('account_members'))
        {
            var list = document.getElementById('account_members');
            var item = list.getElementsByTagName('li');
            for( var i=0; i < item.length; i++ )
            {
                item[i].onclick = function()
                    {
                        hide_list();
                        set_member(this);
                    }
            }
        }
    }
} // End function account_list_onclick

/////////////////////////////////////////////////////////////////////////////

function other_members_click()
{
    if (document.getElementById && document.getElementsByTagName)
    {
        if (document.getElementById("other_members"))
        {
            var list = document.getElementById('other_members');
            var item = list.getElementsByTagName('li');
            for( var i=0; i < item.length; i++ )
            {
                item[i].onclick = function()
                    {
                        hide_list();
                        confirm_other_member(this);
                    }
            }
        }
    }
} // End function account_list_onclick

/////////////////////////////////////////////////////////////////////////////

//function hide_box (box)
//{
//	box.style.visibility = "hidden";
//	box.style.height = "0px";
//	box.style.width = "0px";
//} //End function hideBox
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

function hide_hint ()
{
	var b = document.getElementById("hint")
	b.style.visibility = "hidden";
	b.style.height = "0px";
	b.style.width = "0px";
} //End function hideList

/////////////////////////////////////////////////////////////////////////////
