// hours_balance.js

function getAccountInfo(account_id) {
  var sUrl = '?getcashierinfo=hours_balance&account=' + account_id;
  var callback = {
    success: function(o) {
      var hours_balance_val = document.getElementById('hours_balance_val');
      hours_balance_val.value = o.responseText;
      var hours_balance_disp = document.getElementById('hours_balance_disp');
      hours_balance_disp.innerHTML = messmoney(o.responseText);
      autocalc();
    },
    failure: function(o) {},
    argument: [],
  };
  YAHOO.util.Connect.asyncRequest('GET', sUrl, callback, null);

}

function messmoney(val) {
  if (val < 0)
    return '('+(-val).toFixed(2)+')';
  else
    return (-(-val)).toFixed(2);
}

function autocalc() {
  var balance = document.getElementById('hours_balance_val').value;
  // double-negative forces addition, not string concatenation
  balance -= -document.getElementById('id_hours_balance_change').value;
  newbalance = document.getElementById('new_hours_balance');
  newbalance.innerHTML = messmoney(balance);
}

function setup_autocalc() {
  document.getElementById('id_hours_balance_change').onchange = autocalc;
}

window.onload = function() {
  document.getElementById('id_account').focus();
  setup_autocalc();
}

// Tell autocomplete.js to call us back
GETCASHIERINFO = true;
