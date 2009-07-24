// closeout.js

// fixit prompts user to enter a corrected amount for a transaction,
// then submits it on a hidden form, processed by the same closeout view

function fixit(transid, old_amount, account_name) {
    var new_amount = prompt('If '+account_name+' did not actually pay '+ 
        old_amount+', please enter the amount they did pay:');
    if (new_amount == undefined)
        return;    // user clicked "Cancel"
    document.getElementById('id_fix_payment').value = new_amount;
    document.getElementById('id_transaction').value = transid;
    document.getElementById('closeoutfixform').submit();
}
