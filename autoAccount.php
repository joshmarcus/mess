<?php

session_start();

include 'class/MyDB.php';
include 'functions.php';

$l = varLogin();

if ($_GET['string'])
{
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
			    padding: 4px;
			    padding-right: 20px;
			    border: solid #990099;
			    border-width: 1px 1px 0px 1px;
			    height: 14px;
			    text-align: right;
			    color: #cc0000;"	    
			    onmouseover="this.style.background = '#cc9999'
			    		 this.style.color = '#0000cc'"
			    onmouseout="this.style.background = '#99cc99'
			    		this.style.color = '#cc0000'"
			    onclick="setAccount ('','')">
		Cancel</div>
		<div style="background: #99CC99;
			    border: solid #990099;
			    border-width: 0px 1px 1px 1px;
			    text-align: left;" >
		
EOD;

	if ($myDB->getNumRows ())
	{
		while ($r = $myDB->getRow())
		{
			$aName = addslashes ($r[aName]);
			$t .=<<<NAME
				<div style="padding: 4px;
					height: 14px;"
				 onmouseover="this.style.background = '#96b4ff'"
				 onmouseout="this.style.background = '#99CC99'"
				 onclick="setAccount ($r[aID], '$aName'); getMembers(event)">
				$r[aName]
				</div>
NAME;
		
		}
	}
	else
	{
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

