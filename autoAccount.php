<?php

session_start();

include 'class/MyDB.php';
include 'functions.php';

$l = varLogin();

if ($_GET['string']) {
	$pat = "%" . $_GET['string'] . "%";
	
	$q =<<<QUERY
		SELECT aID, name AS aName
		FROM   acct
		WHERE  name
		LIKE  '$pat'
		LIMIT 20
QUERY;

	$myDB = new myDB ($l);

	$myDB->createResult ($q);

	//print "<br />GET::";print_r($_GET);print "::GET";
	//print  "< br />PAT>> $_GET[string] <<PAT<br />";
	
	$t =<<<EOD
		<div style="background: #99CC99;
				    border-style: solid;
				    border-width: 1px;
				    border-color: #990099;
				    width: 300px;
				    text-align: left; 
				     ">
EOD;

	if ($myDB->getNumRows ()) {
		while ($r = $myDB->getRow()) {
			
			$t .=<<<NAME
					<div style="padding: 4px;
								height: 14px;"
						 onmouseover="this.style.background = '#96b4ff'"
						 onmouseout="this.style.background = '#99CC99'"
						 onclick="setAccount ('$r[aID]','$r[aName]'); getMembers(event)">
					$r[aName]
					</div>
NAME;
		
		}
}	else {
		$t .=<<<NAME
			<div style="padding: 4px;
						height: 14px;"
				 onmouseover="this.style.background = '#96b4ff'"
				 onmouseout="this.style.background = '#99CC99'">
			--- Sorry No Matches! ---
			</div>
NAME;
	}

}

//$debug =  "<br />GET::" . print_r($_GET) . "::GET<br />";
//$debug .= "< br />PAT:: " .  $_GET[string] . " ::PAT<br />";
echo $t;

?>

