<?php

session_start();

include 'functions.php';
include 'class/MyDB.php';

$login = varLogin();

// Set up the page
// This stuff seems to be common to all pages so lets do it this way
include 'html.php';
print htmlHead('Database');
print htmlTitle('Database');

//~~~~~~~~~~~ Print Stuff for debuging
//print "SESSION:>> "; print_r($_SESSION); print "<<:SESSION<br />";
//print "login:>>"; print_r($login); print "<<:login<br />";
//print "GET:>>"; print_r($_GET); print "<<:GET<br />";
//print "POST:>>"; print_r($_POST); print "<<:POST<br />";
//print "xTRANS:>>"; print_r($xArray); print "<<:xTRANS<br />";
//~~~~~~~~~~~ Print Stuff for debugging

// Until we implement actual logins and roles get get a name
    $u = $login['user'];
    $today = date("l, F j, Y \a\\t g:i a");


print<<<EOD
	<div id='content'>
    	<div id='home'>
    		<h1>Hello $u.</h1>
    		<h2>It is now $today</h2>
    	</div>
    </div>
EOD;

?>

<div id="menu">
        <a class='button' href="cashier.php" >Cashier</a>
        <a class='button' href="memList.php" >Members</a>
        <a class='button' href="acctList.php" >Accounts</a>
        <a class='button' href="summary.php" >Summary</a>    
        <a class='button' href="summary.php" >Staff</a>
        <a class='button' href="index.php" >Logout</a>
    </div>

<?php print htmlTail(); ?>
