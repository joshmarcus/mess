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
		<div style="background: #99CC99;
				    border-style: solid;
				    border-width: 1px;
				    border-color: #990099;
				    width: 300px; 
				     ">
EOD;

	while ($r = $myDB->getRow()) {
		
		$m .=<<<NAME
				<div style="padding: 4px;
							height: 14px;"
					 onmouseover="this.style.background = '#96b4ff'"
					 onmouseout="this.style.background = '#99CC99'"
					 onclick="setMember ('$r[mID]','$r[fName]')">
				$r[fName]
				</div>
NAME;
	
	}

	$myDB->closeResult ();
	
	$m .= "</div>";

	echo $m;
}


if ($_GET['string']) {
	$pat = "%" . $_GET['string'] . "%";

	$q =<<<QUERY
		SELECT mID,
			   CONCAT_WS(' ', given, middle, family) AS fName
		FROM   mem
		WHERE  CONCAT_WS(' ', given, middle, family)
		LIKE  '$pat'
		LIMIT 10
QUERY;

	$myDB = new myDB ($l);

	$myDB->createResult ($q);


	echo <<<EOD
		 <div style="background: #cc9999;
				    border-style: solid;
				    border-width: 1px;
				    border-top: 0px;
				    border-color: #990099;
				    width: 300px; 
				     ">
				     <br /><div style='text-align: center;' >
				     --Other Members--
				     </div>
EOD;

	while ($r = $myDB->getRow()) {
		
		$o .=<<<NAME
				<div style="padding: 4px;
							height: 14px;"
					 onmouseover="this.style.background = '#96b4ff'"
					 onmouseout="this.style.background = '#cc9999'"
					 onclick="setOtherMember ('$r[mID]','$r[fName]')">
				$r[fName]
				</div>
NAME;
	
	}

	$myDB->closeResult ();
	
	$o .= "</div>";

	echo $o;
}


?>
