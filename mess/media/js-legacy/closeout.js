// closeout.js

// prompts you to reverse a previous transaction
function reverse_trans(trans_id, account_name) {
    reason = prompt(account_name + ' Transaction ' + trans_id + '\n\nAre you sure it\'s wrong?\nExplain why you\'re changing it.\nThen you can fix it.');
    if (reason == undefined) return;
    document.getElementById('id_reverse_id').value = trans_id;
    document.getElementById('id_reverse_reason').value = reason;
    document.getElementById('reverse_form').submit();
}
