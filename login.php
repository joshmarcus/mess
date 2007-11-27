<?php
session_start();

include 'constants.php';
include 'functions.php';
include 'pwd.php';
include 'class/MyDB.php';

//~~~~~~~~~~~ Print Stuff for debuging
//print "<br />SESSION:>> "; print_r($_SESSION); print "<<:SESSION<br />";
//print "login:>>"; print_r($login); print "<<:login<br />";
//print "GET:>>"; print_r($_GET); print "<<:GET<br />";
print "POST:>>"; print_r($_POST); print "<<:POST<br />";
//print "xTRANS:>>"; print_r($xArray); print "<<:xTRANS<br /htmlspecialchars>";
//~~~~~~~~~~~ Print Stuff for debugging

if ($_POST)
{
	print "YEP, there is a post<br />";
	$user = filter_input(INPUT_POST, 'user', FILTER_SANITIZE_STRING);
	$pass = filter_input(INPUT_POST, 'pass', FILTER_SANITIZE_STRING);
	if($user)
	{
		print "the user is $user.<br />";
	} else
	{
		print "Sorry have post but no user<br />";
	}
	if($pass)
	{
		print "the password is $pass<br />.";
	} else
	{
		print "Sorry have post but no user<br />";
	}

} else
{
	print "Sorry you did not post<br />";
}

?>
