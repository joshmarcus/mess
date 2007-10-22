<?php
session_start();

include 'functions.php';
include 'funcMem.php';

$varLogin = $_SESSION[varLogin];

if ($_GET[id]) $_SESSION[memID] = $_GET[id];

$memId = $_SESSION[memID];

include "fun-html.php";
htmlHeader();
include "header.php";

?>
<!--

<div id="content"></div>
-->
<?php

if (isset($_POST['action']) && $_POST['action'] == 'submitted') {
	$vars = $_POST;
	switch ($_POST['Submit']) {
		case 'Update Member':
			//~~~~~~~ Update Member ~~~~~~~~
			testForName($vars);
			$q = updateMemQuery($vars);
			$link = dbLink($varLogin);
			mysql_query($q, $link);
			mysql_close($link);
			viewMem($_SESSION);
			$ID = $_POST[memID];
			include 'prevNext.php'; 
		break;
		case 'Edit Accounts':
			//~~~~~~~ Edit Member's Accounts ~~~
			include "editAccts.php";
		break;
		case 'Update Accounts':
			$memAccts = $_SESSION[memAccts];
			$aI = 0;
			
		foreach ($memAccts as $a) {
			$aI++;
			$key = "ACCT" . $aI;
			echo "$key<br />";
			$memAcctsOld["$key"] = $a;
		}
		var_dump($memAcctsOld);
		break;
		
		case 'Cancel':
			//~~~~~~~ Cancel Form ~~~~~~~~~~
		break;
		}
		
	$_SESSION[memID] = $_POST[memID];

} else { // Not submitted yet! 

	//~~~~~~ Fill new member form ~~~~~~~~~~~~
	$given = "value=''";
	$middle = "value=''";
	$family = "value=''";
	$key = "value='n'";
	$join = "value=''";
	$status = "value='a'";
	
	$acct = "value=''";
	$prefer = "value='e'";
	$email = "value=''";
	$tel = "value=''";

	$job = "value=''";
	
	$num = "value=''";
	$street = "value=''";
	$adrs2 = "value=''";
	$city = "value='Philadelphia'";
	$state = "value='PA'";
	$zip1 = "value=''";
	$zip2 = "value=''";
	$country = "value='USA'";
	
	$Jd = date("d");
	$Jn = date("n");
	$JY = date("Y");


if ($_GET[action] == "edit" AND $_GET[id] != "" ) {
	
	$memID = $_GET['id'];
	$link = dbLink($varLogin);
	
	//$primAcct = getPrimAcct($_SESSION, $link); 
	$accts = getMemAccts($_SESSION, $link);
	$contact = getMemContacts($_SESSION, $link);

	$query = "SELECT *, acct.name ";
	$query .= "FROM mem, acct ";
	$query .= "WHERE (mem.ID = $memID ) ";
	
	$result = mysql_query($query, $link);
	
	$a = mysql_fetch_array($result, MYSQL_ASSOC);
	
	mysql_free_result($result);
	mysql_close($link);

	//~~~~~~ Fill form with Old values ~~~~~~~~~~~

	$given  = "value='" . $a[given] . "'";
	$middle = "value='" . $a[middle] . "'";
	$family = "value='" . $a[family] . "'";
	
	$key = "value='" . $a[key] . "'";
	$join = "value='" . $a[join] . "'";
	$status = "value='" . $a[status] . "'";
	
	$acct = "value='" . $a[acct] . "'";
	$addrs = "value='" . $a[addrs] . "'";

	$prefer = "value='" . $a[prefer] . "'";
	$email = "value='" . $a[email] . "'";
	$tel = "value='" . $a[tel] . "'";

	$job = "value='" . $a[job] . "'";
	$worker = "value='" . $a[worker] . "'";

	$aNum = "value='" . $a[num] . "'";
	$street = "value='" . $a[street] . "'";
	$adrs2 = "value='" . $a[adrs2] . "'";
	$city = "value='" . $a[city] . "'";
	$state = "value='" . $a[state] . "'";
	$zip1 = "value='" . $a[zip1] . "'";
	$zip2 = "value='" . $a[zip2] . "'";
	$country = "value='" . $a[country] . "'";
	
	
	$memName = $a[given] . " " . $a[middle] . " " .$a[family];

	list($jY, $jn, $jd) = explode("-",trim($a[dateJoin]));
	
	$modTime = date("M d, Y", $a[modTime]) . " at " . date("h:m:sa", $a[modTime]);
	
	list($ph1ac, $ph1ex, $ph1num) = explode("-",trim($a[ph1]));
	list($ph2ac, $ph2ex, $ph2num) = explode("-",trim($a[ph2]));
	list($ph3ac, $ph3ex, $ph3num) = explode("-",trim($a[ph3]));
	
	$ph1ac =  "value='" . $ph1ac . "'";
	$ph1ex =  "value='" . $ph1ex . "'";
	$ph1num =  "value='" . $ph1num . "'";
	$ph2ac =  "value='" . $ph2ac . "'";
	$ph2ex =  "value='" . $ph2ex . "'";
	$ph2num =  "value='" . $ph2num . "'";
	$ph3ac =  "value='" . $ph3ac . "'";
	$ph3ex =  "value='" . $ph3ex . "'";
	$ph3num =  "value='" . $ph3num . "'";
	
} 

?>
<div id="member">
<?php
	if ($_GET[action] == 'edit') {
		print ("<h1>$memName: Last edited by $a[mID] on $a[modDate]</h1>");
	} else print ("<h1>Oh boy! It's a new member!</h1>");
?>
</div>

<form method='POST' action="<?php echo $_SERVER['PHP_SELF']; ?>" >
	<input type="hidden" name="action" value="submitted" />

<?php print (" <input type='hidden' name='mID' value=$memID /> "); ?>

<div id='name'>
	<table>
		<caption>Name</caption>
		<tr>
			<th>Given:</th>
			
<?php print (" <td><input type='text' size='30' $given name='given' /></td> "); ?>

		</tr>
		<tr>
			<th>Middle:</th>

<?php print (" <td><input type='text' size='30' $middle name='middle' /></td>"); ?>

		</tr>
		<tr>
			<th>Family:</th>

<?php print (" <td><input type='text' size='30' $family name='family' /></td>"); ?>

		</tr>
	</table>
</div>

<div id='address'>
	<table>
		<caption>Address</caption>
		<tr>
			<th>Address 1:</th>

<?php print (" <td><input type='text' size='40' $adrs1 name='adrs1' /></td> "); ?>

</tr>
		<tr>
			<th>Address 2:</th>

<?php print (" <td><input type='text' size='40' name='adrs2' $adrs2 /></td>"); ?>

		</tr>
		<tr>
			<th>City:</th>

<?php print (" <td><input type='text' size='40' name='city' $city /></td>");?>

		</tr>
		<tr>
			<th>State:</th>

<?php print (" <td><input type='text' size='2' name='state' $state /></td>");?>

		</tr>
		<tr>
			<th>Zip Code:</th>

<?php print (" <td><input type='text' size='5' name='zip1' $zip1 /> -
		<input type='text' size='5' name='zip2' $zip2 /></td>"); ?>

		</tr>
		<tr>
			<th>Country:</th>

<?php print (" <td><input type='text' size='3' name='country' $country /></td>"); ?>

		</tr>
		<tr>
			<th>Public:</th>
			<td>

<?php pub_view('pubAdrs', $a[pubAdrs]) ?>
			
			</td>
		</tr>
	</table>
</div>

<div id='contact'>
	<table>
		<caption>Contact</caption>
		<tr>
			<th>Email:</th>

<?php print (" <td><input type='text' size='40' name='email' $email /></td>");?>

			<td>Public:
			
<?php pub_view('pubEmail', $a[pubEmail]) ?>
			
			</td>
		</tr>
		<tr>
			<td colspan='3'>Prefer email:
			
<?php pub_view('prefEmail', $a[prefEmail]) ?>
			
			</td>
		</tr>
		<tr>
			<th>Phone 1:</th>
			<td>
				
<?php 		
	phSelect(ph1Type, $a[ph1Type]);
		
	print (" <input type='text' maxlength='3' size='3' name='ph1ac' $ph1ac />-
				<input type='text' maxlength='3' size='3' name='ph1ex' $ph1ex />-
				<input type='text' maxlength='4' size='4' name='ph1num' $ph1num /> Ext:
				<input type='text' maxlength='4' size='4' name='ph1Ext' $ph1Ext />
			"); 
?>

			</td>
			<td>Public:

<?php pub_view('pubPh1', $a[pubph1]) ?>
		
			</td>
		</tr>
		<tr>
			<th>Phone 2:</th>
			<td>
			
<?php 
	phSelect(ph2Type, $a[ph2Type]);

	print (" <input type='text' maxlength='3' size='3' name='ph2ac' $ph2ac />-
				<input type='text' maxlength='3' size='3' name='ph2ex' $ph2ex />-
				<input type='text' maxlength='4' size='4' name='ph2num' $ph2num /> Ext:
				<input type='text' maxlength='4' size='4' name='ph2Ext' $ph2Ext />
			");
?>
			</td>
			<td>Public:
			
<?php pub_view('pubPh2', $a[pubPh2]) ?>
			
			</td>
		</tr>
		<tr>
			<th>Phone 3:</th>
			<td>
				
<?php
	phSelect(ph3Type, $a[ph3Type]);

	print (" <input type='text' maxlength='3' size='3' name='ph3ac' $ph3ac />-
				<input type='text' maxlength='3' size='3' name='ph3ex' $ph3ex />-
				<input type='text' maxlength='4' size='4' name='ph3num' $ph3num /> Ext:
				<input type='text' maxlength='4' size='4' name='ph3Ext' $ph3Ext />
			");
?>

			</td>
			<td>Public:
			
<?php pub_view('pubPh3', $a[pubPh3]) ?>
			
			</td>
		</tr>
		<tr>
			<td colspan='3'>Primary Phone:

<?php primPh('phPref', $a[phPref]) ?>
			
			</td>
		</tr>
	</table>
</div>

<div id='status'>
	<table>
		<caption>Status</caption>
		<tr>
			<th>Joined:</th>
			<td>
				<select name='joinM' size='1'>
<?php
	
	for ($M = 1; $M <= 12; $M++) {
		
		$mon = whatMonth($M);
		
		if ($M == $Jn) {
			print ("<option selected value=$M>$mon</option>");
			} else {
				print ("<option value=$M>$mon</option>");
			}
		}
?>

				</select>
				<select name='joinD' size='1'>

<?php
		for ($d = 1; $d <= 31; $d++) {
			if ($d == $Jd) {
				print ("<option selected>$d</option>");
			} else {
				print ("<option>$d</option>");
			}
		}
?>

				</select>
				<select name='joinY' size='1'>

<?php
	setType($jY, "integer");
	$Y = (integer) date("Y");

		for ($Y; $Y >= 1975; $Y--) {
			if ($Y == $jY) {
				print ("<option selected>$Y</option>");
			} else {
				print ("<option>$Y</option>");
			}
		}
?>

				</select>
	
			</td>
		</tr>
		<tr>
			<td colspan='2'>
				 <input type='radio' name='status' value='a' checked='checked'/>Active
				 <input type='radio' name='status' value='n' />Nonmember
				 <input type='radio' name='status' value='l' />On Leave
				 <input type='radio' name='status' value='q' />Quit
				 <input type='radio' name='status' value='r' />Rejoined
			</td>
		</tr>
	</table>
</div>

<div id='accounts'>

<table>
	<caption>Accounts</caption>
	<tr>
		<th>Primary:</th>
			<td>
				<select name='primAcct' >

<?php
$link = dbLink($varLogin);

$q =  "SELECT accts.aID, accts.aName, mem.nGiven ";
$q .= "From accts, mem, acctMem ";
$q .= "WHERE (acctMem.aID = accts.aID) AND (acctMem.mID = mem.mID) ";
$q .= "AND (acctMem.aType = 'p') AND (mem.mID = $memID)";

$r = mysql_query($q, $link);
$a = mysql_fetch_array($r, MYSQL_ASSOC);

$primAcctID = (integer) $a[accts.aID];
mysql_free_result($r);
	
$q = "SELECT * FROM accts ORDER BY aName";
$r = mysql_query($q, $link);

while ( $acct = mysql_fetch_array($r, MYSQL_ASSOC)) {
	$aID = (integer) $acct[aID];
	$aN = $acct[aName];
	if ( $aID == $primAcctID) {
		print("<option value='$aID' selected>$aN</ option>");
		} else {
			print ("<option value='$aID' >$aN</option");
		}
	}
mysql_free_result($r);	
mysql_close($link);
?>
			</ select>
		</td>
	</tr>
	<tr>
		<th>Contact For:</th>
		<td>
<?php		
	if (count($contact) != NULL) {
		foreach ($contact as $a) {
			$aN = $a[aName];
			print("$aN<br />"); 
		}
	}
	else print "None";
?>
		</td>
	</tr>
	<tr>
		<th>Others:</th>
		<td>
<?php		
	if (count($accts) != NULL){ 
		foreach ($accts as $a) {
			$aN = $a[aName];
			print("$aN<br />"); 
			}
	}
	else print "None";
?>
		</td>
	</tr>
	<tr>
		<td colspan='2'>
			<input name="Submit" type="submit" value='Edit Accounts'>
		</td>
	</ tr>
</table>

</div>

<?php
//}
?>

<div id='submit'>
	<input name="reset" type="reset" name='Reset'>
	<input name="Submit" type="submit" value='Cancel'>
	<input name="Submit" type="submit" value='Update Member'>
	
</div>

</form>

<?php
}
?>

</body>
</html>
