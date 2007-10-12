<?php
session_start();

include 'functions.php';
//include 'fun-table.php';

include 'class/MyDB.php';
include 'class/trans.php';
include 'class/transTable.php';
include 'class/account.php';
include 'class/member.php';

// Collect server, user, password, and database into an array
$loginArr = varLogin();

$step = "Start";

if ($_POST) {
	
	$step = $_POST['Submit'];
	
    $xArray = array ('aID'     => $_POST['aID'],
                     'mID'     => $_POST['mID'],
                     'aName'   => $_POST['aName'],
                     'fName'   => $_POST['fName'],
                     'sale'    => $_POST['sale'],
                     'saleAmt' => $_POST['saleAmt'],
					 'pay'     => $_POST['pay'],
                     'payAmt'  => $_POST['payAmt'],
                     'note'    => $_POST['note'],
                     'ref'     => $_POST['ref']
                     );
                     
	if ($xArray['aID'] && !$xArray['aName']) {
		$account = new account($loginArr);
		$xArray['aName'] = $account->getName($xArray['aID']);
	}
	
    if ($xArray['mID'] && !$xArray['fName']) {
		$member = new member($loginArr);
		$xArray['fName'] = $member->getName($xArray['mID']);
	}
	                
} else {
	
	$xArray = array('aID'     => '',
						'mID'     => '',
						'aName'   => '',
						'fName'   => '',
						'sale'    => '',
						'saleAmt' => '',
						'pay'     => '',
						'payAmt'  => '',
						'note'    => '',
						'ref'     => ''
						);
}
                            

//~~~~~~ Set up the page ~~~~~~~~~~~
include 'html.php';
include 'nav.php';

print htmlHead(Cashier);
print htmlMariposa(Cashier);
print navCashier();
print navCashierTask();

//~~~~~~~~~~~ Print Stuff for debuging
//print "<br />SESSION:>> "; print_r($_SESSION); print "<<:SESSION<br />";
//print "loginArr:>>"; print_r($loginArr); print "<<:loginArr<br />";
//print "GET:>>"; print_r($_GET); print "<<:GET<br />";
//print "POST:>>"; print_r($_POST); print "<<:POST<br />";
//print "xTRANS:>>"; print_r($xArray); print "<<:xTRANS<br />";
//~~~~~~~~~~~ Print Stuff for debugging

    switch ($step) {
    	
    case 'Start': case 'Cancel':
    	unset($xArray);
		print <<<EOD
			<div id='transHeader'><h2>
			Oh Baby! It's a new transaction!
			</h2></div>
EOD;
		$trans = new trans($loginArr);
		print $trans->form($xArray);

		$table = new transTable($loginArr);
		print $table->table();
            
	break;
	case 'New': case '':
	
		print <<<TITLE
			<div id='transHeader'>
			<h2>New Transaction for "$xArray[aName]."</h2>
			</div>
TITLE;
		$trans = new trans($loginArr);
		print $trans->form($xArray);
		
		$table = new transTable($loginArr);
		print $table->acctTrans($xArray['aID']);

	break;

	case 'Next':
	
		$trans = new trans($loginArr);
		$validate = $trans->validate($xArray);
		if ( isset($validate) == TRUE ) {

			print <<<EOD
				<div id='transHeader'>
				<h2>$validate</h2> 
				</div>
EOD;
			print $trans->form($xArray);
			
			$table = new transTable($loginArr); 
			
			if($xArray['aID']) {
				print $table->acctTrans($xArray['aID']);
			} else print $table->table();
			
			
			//tableTransToday($link); 
		}
		else {
			
			$trans->confirm();
			
			$table = new transTable($loginArr);
			print $table->acctTrans($xArray['aID']);
		}
		
	break;
	case 'Edit':
		
		$trans = new trans($loginArr);
		//$trans->insertTrans($xArray);
		
		print <<<EOD
			<div id='transHeader'><h2>
			Edit transaction for $aName.
			</h2></div>
EOD;

		print $trans->form($xArray);
		
		$table = new transTable($loginArr);
		print $table->acctTrans($xArray['aID']);
		
	break;
	case 'Accept':

		$trans = new trans($loginArr);
		$trans->insertTrans($xArray);

		print <<<EOD
			<div id='transHeader'><h2>
			Oh Baby! It's a new transaction!
			</h2></div>
EOD;
		unset($xArray);
		print $trans->form($xArray);
		
		$table = new transTable($loginArr);
		print $table->table(); 

	break;
	}    
    
   // $_SESSION[memID] = $_POST[memID];

/*
} else {
    //
    //  Start a new transaction here
    //print navCashier();
    //print navCashierTask();
    
    print <<<EOD
        <div id='transHeader'><h2>
        Oh Baby! It's a new transaction!
        </h2></div>
EOD;
    
    $trans = new trans($loginArr);
    print $trans->form($xArray);
    
    $table = new transTable($loginArr);
    print $table->table();
    
    }
*/
print $htmlTail;
?>
