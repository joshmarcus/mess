<?php

session_start();

include 'class/MyDB.php';
include 'functions.php';

$l = varLogin();
	
if ($_GET['aID']) {
	$aID = $_GET['aID'];
	
	$q =<<<QUERY
		SELECT M.mID,
			   CONCAT_WS(' ', M.given, M.middle, M.family) AS fName
		FROM mem M, acct A, acctMem AM
		WHERE (M.mID = AM.mID)
		AND   (A.aID = '$aID')
		AND   (AM.aID = '$aID')
QUERY;

	$myDB = new myDB ($l);

	$myDB->createResult ($q);

	//print "<br />GET::";print_r($_GET);print "::GET";
	//print  "< br />PAT>> $_GET[string] <<PAT<br />";

	echo <<<EOD
		<div style="background: #cc9999;
				    border-style: solid;
				    border-width: 1px;
				    border-color: #990099;
				    width: 300px
				    padding: 4px;
				    text-size: 1em;"
					>
		<div onmouseover="this.style.background = '#99cc99'"
             onmouseout="this.style.background = '#cc9999'"
             onclick="getMembers (event)">No One!</div>
EOD;

	while ($r = $myDB->getRow()) {
		
		$m .=<<<NAME
				<div onmouseover="this.style.background = '#99cc99'"
					 onmouseout="this.style.background = '#cc9999'"
					 onclick="setMember ('$r[mID]','$r[fName]')
					 		  setNote ()">
				$r[fName]
				</div>
NAME;
	
	}

	$myDB->closeResult ();
	
	$m .= "</div>";

	echo $m;
}

?>
