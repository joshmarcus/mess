// cashier.js

// Hide elements that aren't used yet
function hideUnusedElements() {
  document.getElementById('account_row').style.display = 'block';
  document.getElementById('member_row').style.display = 'none';
  document.getElementById('debit_row').style.display = 'none';
  document.getElementById('debit_label').style.display = 'none';
  document.getElementById('debit_amount').style.display = 'none';
  document.getElementById('credit_row').style.display = 'none';
  document.getElementById('credit_label').style.display = 'none';
  document.getElementById('credit_amount').style.display = 'none';
  document.getElementById('last_row').style.display = 'none';
  document.getElementById('ref_label').style.display = 'none';
  document.getElementById('ref_text').style.display = 'none';
}
function getAccounts() {
  var query = '';
  var mySchema = ['results', 'name', 'id'];
  var myDataSource = new YAHOO.widget.DS_XHR(query, mySchema);
  myDataSource.scriptQueryParam = 'string';
  myDataSource.scriptQueryAppend = 'search=accounts';
  myDataSource.responseType = YAHOO.widget.DS_XHR.TYPE_JSON; 
  var myAutoComp = new YAHOO.widget.AutoComplete("myInput","myContainer", myDataSource);
  myAutoComp.forceSelection = true;
  myAutoComp.allowBrowserAutocomplete = false;
  myAutoComp.itemSelectEvent.subscribe(setSelectedAccount);
}
function setSelectedAccount(sType, aArgs) {
  // aArgs[0] - AutoComplete instance
  // aArgs[1] - the <li> element selected in the suggestion container
  // aArgs[2] - array of the data for the item as returned by the DataSource
  var idAccount = aArgs[2][1];
  document.getElementById('id_account').value = idAccount;
  //getMembers();
  document.getElementById('member_row').style.display = 'block';
  document.getElementById('member-input').focus();
}
function getAccountId() {
  return document.getElementById('id_account').value;
}
function getMembers() {
  var schema = ['results', 'name', 'id', 'account_member'];
  //var query = '';
  account_id = document.getElementById('id_account').value;
  var searchType = 'members&account_id=' + account_id;
  var dataSource = new YAHOO.widget.DS_XHR('', schema);
  dataSource.scriptQueryParam = 'string';
  dataSource.scriptQueryAppend = 'search=' + searchType;
  dataSource.responseType = YAHOO.widget.DS_XHR.TYPE_JSON; 
  var memberAutoComp = new YAHOO.widget.AutoComplete('member-input', 
      'member-container', dataSource);
  memberAutoComp.forceSelection = true;
  memberAutoComp.allowBrowserAutocomplete = false;
  memberAutoComp.itemSelectEvent.subscribe(setSelectedMember);
  memberAutoComp.doBeforeSendQuery = function(query) {
    var queryString = [];
    queryString.push(query);
    queryString.push('&search=members&account_id=');   
    queryString.push(document.getElementById('id_account').value);
    return queryString.join('');
  }
  memberAutoComp.formatResult = function(aResultItem, sQuery) {
    /* aResultItem[0] will always be the actual key data field returned
     * for the query. All subsequent data held in aResultItem[1] to
     * aResultItem[n] are the supplemental data points for the result,
     * as defined by the schema in your DataSource constructor.
     */
    var name = aResultItem[0];
    var accountMember = aResultItem[2];
    var html = [];
    if (!accountMember) {
      html.push('<span class=\"not-acct-mem\" >');
      html.push(name);
      html.push('</span>');
    }
    else {
      html.push('<span class=\"\" >');
      html.push(name);
      html.push('</span>');
    }
    return (html.join(''));
  }
}
function setSelectedMember(sType, aArgs) {
  // aArgs[0] - AutoComplete instance
  // aArgs[1] - the <li> element selected in the suggestion container
  // aArgs[2] - array of the data for the item as returned by the DataSource
  var idMember = aArgs[2][1];
  document.getElementById('id_member').value = idMember;
  document.getElementById('debit_row').style.display = 'block';
  document.getElementById('credit_row').style.display = 'block';
  document.getElementById('last_row').style.display = 'block';
}
function getTransactions(id) {
  var query = "?search=transactions"
  if (id == parseInt(id)) {  
    query += "&account_id=" + document.getElementById('id_account').value
  }
  xhr(query,'transactions');
}
function set_member(this_obj) {      
  hide_list();
  hide_message();
  if ( this_obj.id == 'list_cancel') {
    member_name = '';
    id_member = '';
  }
  else {
    if (!this_obj.textContent) var member_name = this_obj.innerText;
    if (this_obj.textContent) var member_name = this_obj.textContent;
    id_member = this_obj.id;
  }
  document.getElementById("member_name").value = member_name;
  document.getElementById("id_member").value = id_member;
}
function confirm_other_member(this_obj) {
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
}
function set_other_member(this_obj, other_member_id, other_member_name) {
  hide_message();
  if (!this_obj.textContent) var member_name = this_obj.innerText;
  if (this_obj.textContent) var member_name = this_obj.textContent;
  id_member = this_obj.id;
  set_note(id_member, member_name);
  document.getElementById("member_name").value = other_member_name;
  document.getElementById("id_member").value = other_member_id;
}
function set_note (id_member, member_name) {
  var old_note = "";
  var note = document.getElementById("id_note");
  if ( note.value ) {
    old_note =  "; " + note.value;
  }
  var new_note = "Authorized by " + member_name + " (#" + id_member + ")" +
      old_note;
  note.value = new_note;
} 
function hide_hint () {
  var b = document.getElementById("hint")
  b.style.visibility = "hidden";
  b.style.height = "0px";
  b.style.width = "0px";
} 
