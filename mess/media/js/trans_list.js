// trans_list.js

window.onload = function()
{
	// pop up Ajax Helper box for account names onkeyup
	var account_name = document.getElementById('account_name');
	account_name.onkeyup = ajax_request_accounts_list;

	// if list is hidden *instantly* then it gets hidden before it receives 
	// the click to fill in the value in the form!  Doh!  50ms should suffice...
	account_name.onblur = function() 
	{
		setTimeout("hide_helper('list','account_name');",300);
	}

	// same deal for member names...
	// but, also get the list of account members onfocus
	var member_name = document.getElementById('member_name');
	member_name.onkeyup = ajax_request_members_list;
	member_name.onfocus = ajax_request_members_list;
	member_name.onblur = function()
	{
		setTimeout("hide_helper('list','member_name');",300);
	}

}	// end window.onload function


function ajax_request_accounts_list()
{
    // List all accounts that match a pattern
	account_name = document.getElementById('account_name');
	if (account_name.value == '')
		hide_helper('list','account_name');
	else
		xml_send_then_run('/membership/rawlist/?account=%2A' + 
			account_name.value+'%2A&list=accounts', ajax_list_field, 'account_name');
} // end function ajax_request_accounts_list


function ajax_request_members_list()
{
	// If no account name, list all members matching a pattern
	// If account name is shown, list members of the account
	account_name = document.getElementById('account_name');
	member_name = document.getElementById('member_name');
	var query = '/membership/rawlist/?';
	if (account_name.value  == '')
	{
		if (member_name.value == '')
		{
			hide_helper('list','member_name');
			return;
		}
		else
		{
			query += 'list=members&member=%2A'+member_name.value+'%2A';
		}
	}
	else
	{
		if (member_name.value == '')
			query += 'account='+account_name.value+'&list=members';
		else
			query += 'account='+account_name.value+'&list=members&member=%2A'+
				member_name.value+'%2A';
	}
	xml_send_then_run(query, ajax_list_field, 'member_name');
}


function ajax_list_field(rawlist, field_id)
{
	choices = rawlist.split('\n');
	clickarray = '';
	for (i=0; i < choices.length; i++)
	{
		// in the JS, slash-escape any ' or "
		// in the HTML, amp-escape any & or <
		clickarray += '<div class="account_choice" onclick="fillnmit(\''+
			field_id+'\', \''+
			choices[i].replace(/'/g,'\\\'').replace(/"/g,'\\\"')+'\');">'+
			choices[i].replace(/&/g,'&amp;').replace(/</g,'&lt')+'</div>\n';
	}
	var l = document.getElementById('list');
	l.innerHTML = clickarray;
	//show_list(document.getElementById(field_id));
	show_helper('list',field_id);
}	// end function ajax_list_field


function xml_send_then_run(query, func_to_run_on_return, argv)
{	// This sends an xmlhttp request, then sets the func_to_run_on_return
	// for whenever we receive the response.  The argv goes to the func_to_run

	var req = xmlHttp(); // use base.js to create this xmlhttp object
	req.open('GET', query, true);
	req.onreadystatechange = function()
	{
		if (req.readyState == 4)
			func_to_run_on_return(req.responseText, argv);
	}
	req.send(null);
} // end function xml_send_then_run


function fillnmit(id, val)
{
	f = document.getElementById(id);
	f.value = val;
//	hide_list();
	document.forms[0].submit();
}

function show_helper(box_id,field_id)
{
	var box = document.getElementById(box_id);
	box.helped_field = field_id;
	box.inclick = false;
	var fld = document.getElementById(field_id);
	var p = find_pos(fld);	
	box.style.left = (p[0]+25) + 'px';
	box.style.top = (p[1]+25) + 'px';
	box.style.height = 'auto';
	box.style.display = 'block';
} // end function show_helper


function hide_helper(box_id, field_id)
{
	// hide the helper box ONLY IF the box is still helping the field
	// don't hide if the box.inclick == true, (box is being clicked)
	var box = document.getElementById(box_id);
	if (box.helped_field == field_id && box.inclick == false)
		box.style.display = 'none';
} // end function hide_helper


