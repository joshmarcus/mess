// task_events.js

window.onload = function() {
  document.forms[0].elements[0].focus();

  var account = document.getElementById('id_account');
  account.onblur = function() {
    var selected_account = account.options[account.selectedIndex];
    var account_id = selected_account.value;
    memberFilter(account_id);
  }
}