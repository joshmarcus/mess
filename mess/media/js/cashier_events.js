// cashier_events.js

window.onload = function() {
  document.forms[0].elements[0].focus();
  var account = document.getElementById('id_account');
  account.onblur = memberFilter;
}

/*
window.onload = function() {
  hideUnusedElements();
  autoComp( "account-input", "account-container", "accounts", 
      setSelectedAccount);
  getMembers();
  getTransactions();
    
  //  Display form elements when needed    
  document.getElementById('debit_type').onchange = function() {
    document.getElementById('debit').style.display = 'inline';
    document.getElementById('ref').style.display = 'inline';
  }
  document.getElementById('credit_type').onchange = function() {
    if (document.getElementById('id_credit_type.value') != 'N') {
      document.getElementById('credit').style.display = 'inline';
    }
    else if (document.getElementById('id_credit_type.value') == 'N') {
      document.getElementById('credit').style.display = 'none';
    }
  }
  var id_ref = document.getElementById('id_ref')
  id_ref.onkeypress = function(e) {
    if (!e) var e = window.event;
    no_enter(e);
  }
  var id_note = document.getElementById('id_note')
  id_note.onkeypress = function(e) {
    if (!e) var e = window.event;
    return no_enter(e);  
  }
  var id_debit = document.getElementById('id_debit')
  id_debit.onkeypress = function(e) {
    if (!e) var e = window.event;
    return no_enter(e);  
  }
  var id_credit = document.getElementById('id_credit')
  id_credit.onkeypress = function(e) {
    if (!e) var e = window.event;
    return no_enter(e);  
  }
  var message = document.getElementById('message')
  id_note.onclick = function(e) {
    hide_message();  
  }
}
*/
