// hours_balance.js

function getAccountInfo(account_id) {
  var sUrl = '?getcashierinfo=hours_balance&account=' + account_id;
  var callback = {
    success: function(o) {
      var new_hours_balance = document.getElementById('id_hours_balance');
      new_hours_balance.value = messmoney(o.responseText);
      var old_hours_balance = document.getElementById('old_hours_balance');
      old_hours_balance.innerHTML = messmoney(o.responseText);
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

window.onload = function() {
  document.getElementById('id_account').focus();
}

// Tell autocomplete.js to call us back
GETCASHIERINFO = true;
