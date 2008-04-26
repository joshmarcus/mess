// cashier_events.js

window.onload = function()
{
    var account_name = document.getElementById('account_name')
    account_name.onclick = function()
    {
        show_message('account_name', 'Typing will display matches.');
    }
    account_name.onkeyup = function(e)
    {
        if (!e) var e = window.event;
        get_accounts(this, e);
    }
    account_name.onkeypress = function(e)
    {
        if (!e) var e = window.event;
        return no_enter(e);  
    }

    var member_name = document.getElementById('member_name')
    member_name.onclick = function()
    {
        if (!e) var e = window.event;        
        get_account_members(e);
            }
    member_name.onkeyup = function(e)
    {
        if (!e) var e = window.event;
        get_members(e);
    }
    member_name.onkeypress = function(e)
    {
        if (!e) var e = window.event;
        return no_enter(e);  
    }

    var id_ref = document.getElementById('id_ref')
    id_ref.onkeypress = function(e)
    {
        if (!e) var e = window.event;
        no_enter(e);
        
    }

    var id_note = document.getElementById('id_note')
    id_note.onkeypress = function(e)
    {
        if (!e) var e = window.event;
        return no_enter(e);  
    }

    var id_debit = document.getElementById('id_debit')
    id_debit.onkeypress = function(e)
    {
        if (!e) var e = window.event;
        return no_enter(e);  
    }

    var id_credit = document.getElementById('id_credit')
    id_credit.onkeypress = function(e)
    {
        if (!e) var e = window.event;
        return no_enter(e);  
    }

    var message = document.getElementById('message')
    id_note.onclick = function(e)
    {
        hide_message();  
    }





}

