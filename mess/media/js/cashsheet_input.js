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

  var sUrl = '?getcashierinfo=max_allowed_to_owe&account=' + account_id;
  var callback = {
    success: function(o) {
      var max_allowed_to_owe = document.getElementById('max_allowed_to_owe');
      max_allowed_to_owe.innerHTML = messmoney(o.responseText);
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

  sUrl = '?getcashierinfo=transactions&account=' + account_id;
  transax_callback = {
    success: function(o) {
      var transax = document.getElementById('transactions');
      transax.innerHTML = o.responseText;
    },
    failure: function(o) {},
    argument: [],
  };
  YAHOO.util.Connect.asyncRequest('GET', sUrl, transax_callback, null);

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
  balance -= -document.getElementById('id_misc').value;
  balance -= -document.getElementById('id_deposit').value;
  balance -= -document.getElementById('id_bulk_orders').value;
  balance -= -document.getElementById('id_regular_sales').value;
  balance -= document.getElementById('id_credit_debit').value;
  balance -= document.getElementById('id_check_mo').value;
  newbalance = document.getElementById('newbalance');
  newbalance.innerHTML = messmoney(balance);
}

function setup_autocalc() {
  document.getElementById('id_misc').onchange = autocalc;
  document.getElementById('id_deposit').onchange = autocalc;
  document.getElementById('id_bulk_orders').onchange = autocalc;
  document.getElementById('id_regular_sales').onchange = autocalc;
  document.getElementById('id_credit_debit').onchange = autocalc;
  document.getElementById('id_check_mo').onchange = autocalc;
}

// if form is basically ok, return true, else return confirm.
function confirm_if_weird(cashform) {
  var purchases = document.getElementById('id_misc').value ||
                  document.getElementById('id_deposit').value ||
                  document.getElementById('id_bulk_orders').value ||
                  document.getElementById('id_regular_sales').value
  var payments = document.getElementById('id_credit_debit').value ||
                 document.getElementById('id_check_mo').value
  if (payments && (! purchases)) {
    return confirm('Are you sure it\'s right?\nYou\'re saying they paid without\nbuying anything.');
  }
  return true;
}

// prompts you to reverse a previous transaction
function reverse_trans(trans_id, account_name) {
    reason = prompt(account_name + ' Transaction ' + trans_id + '\n\nAre you sure it\'s wrong?\nExplain why you\'re changing it.\nThen you can fix it.');
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
