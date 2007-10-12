<?php

session_start();

include 'functions.php';
include 'class/MyDB.php';
include 'class/account.php';

$loginArr = varLogin();

//include 'header.php';

//~~~~~~ Set up the page ~~~~~~~~~~~
include 'html.php';
include 'nav.php';

print htmlHead(Accounts);
print htmlMariposa(Accounts);
print navAcctList();
//print navAcctTask();


//~~~~~~~~~~~ Print Stuff for debuging
//print "<br />SESSION:>> "; print_r($_SESSION); print "<<:SESSION<br />";
//print "POST:>>"; print_r($_POST); print "<<:POST<br />";
//print "loginArr:>>"; print_r($loginArr); print "<<:loginArr<br />";
//print "ATRANS:>>"; print_r($aTrans); print "<<:ATRANS<br />";
//~~~~~~~~~~~ Print Stuff for debugging

$acct = new account($loginArr);

print "<div id='table'>";
print $acct->table();
print "</div>";
print htmlTail();

?>
