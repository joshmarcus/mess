// cashsheet_input.js

function getAccountInfo(account_id) {

  var sUrl = '?getcashierinfo=balance&account=' + account_id;
  var callback = {
    success: function(o) {
      var balance_val = document.getElementById('balance_val');
      balance_val.value = o.responseText;
      var balance_disp = document.getElementById('balance_disp');
      balance_disp.innerHTML = messmoney(o.responseText);
      autocalc();
    },
    failure: function(o) {},
    argument: [],
  };
  YAHOO.util.Connect.asyncRequest('GET', sUrl, callback, null);

  var sUrl = '?getcashierinfo=hours_balance&account=' + account_id;
  var callback = {
    success: function(o) {
      var hours_balance = document.getElementById('hours_balance');
      hours_balance.innerHTML = messmoney(o.responseText);
    },
    failure: function(o) {},
    argument: [],
  };
  YAHOO.util.Connect.asyncRequest('GET', sUrl, callback, null);

  var sUrl = '?getcashierinfo=acct_flags&account=' + account_id;
  var callback = {
    success: function(o) {
      var flags_holder = document.getElementById('flags');
      flags_holder.innerHTML = o.responseText;
    },
    failure: function(o) {},
    argument: [],
  };
  YAHOO.util.Connect.asyncRequest('GET', sUrl, callback, null);

  // jump cursor to regular sales field
  setTimeout("document.getElementById('id_regular_sales').focus();",20);
}

function messmoney(val) {
  if (val < 0)
    return '('+(-val).toFixed(2)+')';
  else
    return (-(-val)).toFixed(2);
}

function autocalc() {
  var balance = document.getElementById('balance_val').value;
  // double-negative forces addition, not string concatenation
  balance -= -document.getElementById('id_misc_sales').value;
  balance -= -document.getElementById('id_dues_deposits').value;
  balance -= -document.getElementById('id_bulk_orders').value;
  balance -= -document.getElementById('id_after_hours').value;
  balance -= -document.getElementById('id_regular_sales').value;
  balance -= document.getElementById('id_credit_debit').value;
  balance -= document.getElementById('id_check_mo').value;
  newbalance = document.getElementById('newbalance');
  newbalance.innerHTML = messmoney(balance);
}

function setup_autocalc() {
  document.getElementById('id_misc_sales').onchange = autocalc;
  document.getElementById('id_dues_deposits').onchange = autocalc;
  document.getElementById('id_bulk_orders').onchange = autocalc;
  document.getElementById('id_after_hours').onchange = autocalc;
  document.getElementById('id_regular_sales').onchange = autocalc;
  document.getElementById('id_credit_debit').onchange = autocalc;
  document.getElementById('id_check_mo').onchange = autocalc;
}

// prompts you to reverse a previous transaction
function reverse_trans(trans_id) {
    reason = prompt('Please explain why you are reversing this transaction.  (Transactions should only be reversed when absolutely necessary, as it complicates accounting.)');
    if (reason == undefined) return;
    document.getElementById('id_reverse_id').value = trans_id;
    document.getElementById('id_reverse_reason').value = reason;
    document.getElementById('reverse_form').submit();
}

window.onload = function() {
  document.getElementById('id_account').focus();
  setup_autocalc();
}

// Tell autocomplete.js to call us back
GETCASHIERINFO = true;
