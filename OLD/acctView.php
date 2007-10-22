<?php

session_start();

include 'functions.php';
include 'class/MyDB.php';
include 'class/account.php';
include 'class/member.php';
include 'class/tel.php';
include 'class/email.php';
include 'class/address.php';

$loginArr = varLogin();

//~~~~~~~~~~~ Print Stuff for debuging
//print "<br />SESSION:>> "; print_r($_SESSION); print "<<:SESSION<br />";
//print "POST:>>"; print_r($_POST); print "<<:POST<br />";
//print "GET:>>"; print_r($_GET); print "<<:GET<br />";
//print "loginArr:>>"; print_r($loginArr); print "<<:loginArr<br />";
//print "ATRANS:>>"; print_r($aTrans); print "<<:ATRANS<br />";
//~~~~~~~~~~~ Print Stuff for debugging

$aID = $_GET['id'];

$prevID = $aID - 1; 
$nextID = $aID + 1;
 
$acct = new account($loginArr);
$a = $acct->getDetails($aID);


//~~~~~~ Now that we have some info, Set up the page ~~~~~~~~~~~
include 'html.php';
include 'nav.php';

print htmlHead($a['name']);
print htmlMariposa($a['name']);
print navAcct();
print navAcctTask($aID, $prevID, $nextID);

$mem = new member($loginArr);
$m	= $mem->contact($a['mID']);

$tele = new tel($loginArr);
$t = $tele->format($m['ac'],$m['ex'],$m['num'],$m['ext']);

if($m['ePID']) {
        $loc = location($m['eLoc']);
        $email = "$loc: <a href='mailto:$m[email]' >$m[email]</a>";
}
 
if($m['tPID']) {
        $loc = location($m['tLoc']);
        $tel = "$loc: <a href='telView.php?id=$m[tID]' >$t</a>";
}
print $email;
switch ($m[prefer]) {
    case 'e':
    	if($email) $contact  = $email . " (prefered)<br/>";
    	if($tel)   $contact .= $tel;    		
    break;
    case 'p':
    	if($tel) $contact  = $tel . " (prefered)<br/>";
    	if($email)   $contact .= $email;    		
    break;
}

print <<<ACCT

<div id='field'>

<table class='acctViewContact'>
    <caption class='view' >Contact Information<caption>
    <tr>
        <th>Contact</th><td>$m[fName]</td>
    </tr>
    <tr>
    	<th>Contact</th><td>$contact</td>
	</tr>
</table>

<table class='acctViewMems' >   
</table>

<table class='memViewMisc' >
</table>

</div>
</body>
</html>

ACCT;

?>
