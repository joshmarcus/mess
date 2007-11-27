<?php
session_start();

include 'functions.php';
include 'class/MyDB.php';

include 'html.php';
print htmlHead('Cashier');
print htmlTitle('Cashier');


//~~~~~~~~~~~ Print Stuff for debuging
//print "<br />SESSION:>> "; print_r($_SESSION); print "<<:SESSION<br />";
//print "login:>>"; print_r($LOGIN); print "<<:login<br />";
//print "GET:>>"; print_r($_GET); print "<<:GET<br />";
//print "POST:>>"; print_r($_POST); print "<<:POST<br />";
//print "xTRANS:>>"; print_r($xArray); print "<<:xTRANS<br />";
//~~~~~~~~~~~ Print Stuff for debugging


?>

<script type="text/javascript" src="functions.js"></script>
<script type="text/javascript" src="cashier.js"></script>

<div id='content' >
<div id="menu">
        <a class='button' href="home.php" >Home</a>
        <a class='button' href="memList.php" >Members</a>
        <a class='button' href="acctList.php" >Accounts</a>
        <a class='button' href="summary.php" >Summary</a>
        <a class='button' href="index.php" >Logout</a>
</div>

<div id='menuTask'>
        <a class='button' href='closeOut.php' >Close Out</a>
</div>

<form id='form' name='form' method='post' >

<input type='hidden' id='aID' name='aID' />
<input type='hidden' id='mID' name='mID' />
<input type='hidden' id='sale' name='sale' value='s' />
<input type='hidden' id='pay' name='pay' />


<table id='table'>
<tr>
	<th id='acctCell' style='text-align: left' >
		Account Name:
	</th>
	<td>
		<input style='outline: 0px;'
			   id='aName' name='aName'
			   type='text' size='40'
			   onclick='hideRing (this);
						showMessage ("aName", "Typing will display matches.")'
			   onkeyup='listAccounts(this, event)'/>
	</td>
	<th style='text-align: right' >
		Reference:
	</th>
	<td>
		<input type='text' size='10' id='ref' name='ref'
			   onkeyPress='return noEnter(event)' />
	</td>
</tr>
<tr>
	<th style='text-align: left' >
		Member Name:
	</th>
	<td id='fNameCell'>
		<input type='text' size='40' id='fName' name='fName'
			   onclick='getMembers(event)'
			   onkeyup='listMembers(event)' />
	</td>
	<th id='payCell'
		style='outline: 0px;
			   text-align: right;
			   background: #ffffff;'
		onmouseover="this.style.background = '#99cc99'"
		onmouseout="this.style.background = '#ffffff'"
		onclick="listType (this, event, 'p')" >
		<div id='payLabel'
			 style='outline: 0px;' >Select Payment</Select></div>
	</th>
	<td>
		<input style='outline: 0px;' type='text' size='10' id='payAmt' name='payAmt'
			   		  onclick='hideMessage(); hideRing(this)'
					  onkeyPress='return noEnter(event)'/>
	</td>
</tr>
<tr>
	<th style='text-align: right;' >
		Note:
	</th>
	<td >
		<input type='text' size='40' id='note' name='note' 
			   onkeyPress='return noEnter(event)'/>
	</td>
	<th id='saleCell'
		style='text-align: right; width: 120px'
		onmouseover="this.style.background = '#99cc99'"
		onmouseout="this.style.background = '#96b4c8'"
		onclick="hideMessage(); listType (this, event, 's')" >
		
		<div id='saleLabel' >
		Purchase:
		</div>
	</th>
	<td>
		<input style='outline: 0px;'
			   type='text' size='10' id='saleAmt' name='saleAmt'
			   onclick='hideMessage(); hideRing(this)'
			   onkeyPress='return noEnter(event)'/>
	</td>
</tr>
<tr>

	<td  colspan='2'>
	</td>
	<td style='text-align: right;' colspan='2'>
		<a href='javascript:resetForm()'
		   alt='Reset Button'
		   title='Click to reset the form' >
		   <img class='button'
		   		src='images/Reset.png' />
		</a>
		<a href='javascript:validate()'
		   alt='Enter Button'
		   title='Click to enter the transaction' >
		   <img class='button'
		   		src='images/Enter.png' />
		</a>	
	</td>
</tr>
</table>
</form>

</div>

<div id='list' ></div>
<div id='message' class='message' onclick='hideMessage ()'
	 style='visibility: hidden;' ></div>
<div id='money' onclick='hideMoney (), hideMessage ()' ></div>

<?php print htmlTail(); ?>
