<?php

session_start();

include 'functions.php';
include 'class/MyDB.php';
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

$mID = $_GET['id'];

$prevID = $mID - 1; 
$nextID = $mID + 1;
 
$mem = new member($loginArr);
$m = $mem->memDetails($mID);


//~~~~~~ Now that we have some info, Set up the page ~~~~~~~~~~~
include 'html.php';
include 'nav.php';

print htmlHead($m['fName']);
print htmlMariposa($m['fName']);
print navMem();
print navMemTask($mID, $prevID, $nextID);

$key = yesNo($m['key']);
$status = statusName($m['status']);

$tel = new tel($loginArr);
$tels = $tel->tels($mID);

unset($phone);
unset($loc);

if($tels) {
    foreach($tels as $t) {
    
        $loc = location($t['loc']);
    
        if($m[tPID] == $t[tID]) {
            $primePhone = "$loc: $t[tel]";
        } else {
            $phones .= "$loc: $t[tel]</br>";
        } 
    }
    rtrim($phones, "</br>");
} else {
    $phones =     "None";
    $primePhone = "None"; 
}

$em = new email($loginArr);
$ems = $em->addrs($mID);

unset($email);
unset($loc);

if($ems) {
    foreach($ems as $e) {
    
        $loc = location($e['loc']);
    
        if($m[ePID] == $e[eID]) {
            $primeEmail = "$loc: <a href='mailto:$e[email]' >$e[email]</a>";
        } else {
            $email .= "$loc: <a href='mailto:$e[email]' >$e[email]</a></br>";
        }
    }
    rtrim($email, "</br>");
} else {
    $email =      "None";
    $primeEmail = "None";
} 


switch ($m[pContact]) {
    case 'e': $contact = $primeEmail; break;
    case 'p': $contact = $primePhone; break;
} 

rtrim($phones, "</br>");

$addrs = new address($loginArr);
$addrs->getAddrs($m['hID']);
$a = $addrs->format();
$address = "<a href='addrsView.php?id=$m[hID]' >$a</a>";

print <<<MEM

<div id='field'>

<table class='memViewContact'>
    <caption class='view' >Contact Information<caption>
    <tr>
        <th>Prefered Contact</th><td colspan='3'>$contact</td>
    </tr>
    <tr>
        <th>Primary Phone:</th><td>$primePhone</td>
        <th>Primary Email:</th> <td>$primeEmail</td>
	</tr>
    <tr>
        <th>Other Phones</th><td>$phones</td>        
    	<th>Other Email</th><td>$email</td>
	</tr> 
</table>

<table class='memViewAccts' >
    <caption class='view' >Accounts</contact>
    
    <tr>
    <th>Primary:</th><td><a href='acctView.php?=$m[aPID]'>$m[paName]</a></td>
    </tr>
    <tr><th>Contact for:</th><td></td></tr>    
    <tr><th>Others:</th>     <td></td></tr>    
</table>

<table class='memViewMisc' >
	<caption class='view' >Misc.</caption>
	<tr><th>Address</th><td>$address</td></tr>
	<tr><th>Job:</th>   <td>$m[jName]</td></tr>
	<tr><th>Status:</th><td>$status</td>  </tr>
	<tr><th>Key:</th>   <td>$key</td>    </tr>
</table>

</div>
</body>
</html>

MEM;

?>
