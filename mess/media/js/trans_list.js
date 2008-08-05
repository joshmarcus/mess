// trans_list.js

window.onload = function()
{
	// pop up Ajax Helper box for account names onkeyup
	var account_name = document.getElementById('account_name')
	account_name.onkeyup = function(e)
	{
		if (!e) var e = window.event;
		ajax_request_accounts_list(this, e);
	}
	// if list is hidden *instantly* then it gets hidden before it receives 
	// the click to fill in the value in the form!  Doh!  50ms should suffice...
	account_name.onblur = function() 
	{
		setTimeout('hide_list()',300);
	}

}	// end window.onload function


function ajax_request_accounts_list(account_name, e)
{
    // List all accounts that match a pattern
	if (account_name.value == '')
		hide_list();
	else
		xml_send_then_run('/membership/rawlist?list=accounts&account=' + 
			account_name.value, ajax_list_accounts, '');
} // end function ajax_request_accounts_list


function ajax_list_accounts(rawlist, unused_argv)
{
	acts = rawlist.split('\n');
	clickarray = '';
	for (i=0; i < acts.length; i++)
	{
		// in the JS, slash-escape any ' or "
		// in the HTML, amp-escape any & or <
		clickarray += '<div class="account_choice" '+
			'onclick="fillin(\'account_name\', \''+
			acts[i].replace(/'/g,'\\\'').replace(/"/g,'\\\"')+
			'\');">'+acts[i].replace(/&/g,'&amp;').replace(/</g,'&lt')+
			'</div>\n';
	}
	var l = document.getElementById('list');
	l.innerHTML = clickarray;
	show_list(document.getElementById('account_name'));
} // end function ajax_list_accounts


function xml_send_then_run(query, func_to_run_on_return, argv)
{	// This sends an xmlhttp request, then sets the func_to_run_on_return
	// for whenever we receive the response.  The argv is supposed to
	// get passed to the func_to_run_on_return.....

	var req = xmlHttp(); // use base.js to create this xmlhttp object
	req.open('GET', query, true);
	req.onreadystatechange = function()
	{
		if (req.readyState == 4)
			func_to_run_on_return(req.responseText, argv);
	}
	req.send(null);
} // end function xml_send_then_run


function fillin(id, val)
{
	f = document.getElementById(id);
	f.value = val;
	hide_list();
}
