//cashier.js

// Hide elements that aren't used yet
function hideUnusedElements()
{
    document.getElementById('member').style.display = 'none';
    document.getElementById('ref').style.display = 'none';
    document.getElementById('credit').style.display = 'none';
    document.getElementById('debit').style.display = 'none';
}

function getAccounts()
{
        var query = '';
        var mySchema = ['results', 'name', 'id'];
        var myDataSource = new YAHOO.widget.DS_XHR(query, mySchema);
        myDataSource.scriptQueryParam = 'string'
        myDataSource.scriptQueryAppend = 'search=accounts'
        myDataSource.responseType = YAHOO.widget.DS_XHR.TYPE_JSON; 
        //myDataSource.responseType = YAHOO.widget.DS_XHR.TYPE_XML; 
        var myAutoComp = new YAHOO.widget.AutoComplete("myInput","myContainer", myDataSource);
        myAutoComp.forceSelection = true;
        myAutoComp.allowBrowserAutocomplete = false;
        myAutoComp.itemSelectEvent.subscribe(setSelectedAccount);
}

////////////////////////////////////////////////////////////////////////

function setSelectedAccount(sType, aArgs)
{
	// aArgs[0] - AutoComplete instance
	// aArgs[1] - the <li> element selected in the suggestion container
    // aArgs[2] - array of the data for the item as returned by the DataSource
    var idAccount = aArgs[2][1]        
	document.getElementById('id_account').value = idAccount;
	document.getElementById('memberInput').focus();
	//document.getElementById('member').style.display = 'inline';
};

/////////////////////////////////////////////////////////////////////////////

function autoComp( inputId, containerId, searchType, onSelectFunction)
{
    /*
     * Create an autoComplete dropdown list.  Expects to get json
     * in the form of
     *
     *      { results: { id1: name1}, {id2: name2}}}
     * 
     * HTML should have this format:
     *      <div id="someName">
     *          <input id="inputId" />
     *          <div id="containerId" ></div>
     *      </div>
    */
        var schema = ['results', 'name', 'id'];
        var query = '';
        var dataSource = new YAHOO.widget.DS_XHR(query, schema);
        dataSource.scriptQueryParam = 'string';
        dataSource.scriptQueryAppend = 'search=' + searchType;
        dataSource.responseType = YAHOO.widget.DS_XHR.TYPE_JSON; 
        var autoComp = new YAHOO.widget.AutoComplete(
                                        inputId, containerId, dataSource);
        autoComp.forceSelection = true;
        autoComp.allowBrowserAutocomplete = false;
        autoComp.itemSelectEvent.subscribe(onSelectFunction);
}

/////////////////////////////////////////////////////////////////////////////

function getMembers()
{
    var id_account = document.getElementById('id_account')
}


function setSelectedMember(sType, aArgs)
{
	// aArgs[0] - AutoComplete instance
	// aArgs[1] - the <li> element selected in the suggestion container
    // aArgs[2] - array of the data for the item as returned by the DataSource
    var idMember = aArgs[2][1]        
	document.getElementById('id_member').value = idMember;
	//document.getElementById('member').style.display = 'inline';
};

/////////////////////////////////////////////////////////////////////////////

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

function hide_hint ()
{
	var b = document.getElementById("hint")
	b.style.visibility = "hidden";
	b.style.height = "0px";
	b.style.width = "0px";
} //End function hideList

/////////////////////////////////////////////////////////////////////////////
