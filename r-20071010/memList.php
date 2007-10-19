<?php

session_start();

include 'functions.php';
include 'class/MyDB.php';
include 'class/member.php';

$loginArr = varLogin();

//~~~~~~ Set up the page ~~~~~~~~~~~
include 'html.php';
include 'nav.php';

print htmlHead(Members);
print htmlMariposa(Members);
print navMemList();
print navMemListTask();


//~~~~~~~~~~~ Print Stuff for debuging
//print "<br />SESSION:>> "; print_r($_SESSION); print "<<:SESSION<br />";
//print "POST:>>"; print_r($_POST); print "<<:POST<br />";
//print "loginArr:>>"; print_r($loginArr); print "<<:loginArr<br />";
//print "ATRANS:>>"; print_r($aTrans); print "<<:ATRANS<br />";
//~~~~~~~~~~~ Print Stuff for debugging

$mems = new member($loginArr);

print "<div id='table'>";
print $mems->table();
print "</div>";

print htmlTail();

?>
