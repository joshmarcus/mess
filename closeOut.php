<?php
session_start();

include 'functions.php';
include 'class/MyDB.php';
include 'class/transTable.php';
include 'class/reconcile.php';

$loginArr = varLogin();

include 'html.php';
include 'nav.php';

//~~~~~~ Set up the page ~~~~~~~~~~~

print htmlHead('Close Out' );
print htmlMariposa('Close Out');
print navCashier();
print navCashierTask();

//~~~~~~~~~~~ Print Stuff
//print "<br />SESSION:>> "; print_r($_SESSION); print "<<:SESSION<br />";
//print "POST:>>"; print_r($_POST); print "<<:POST<br />";
//print "loginArr:>>"; print_r($loginArr); print "<<:loginArr<br />";
//print "ATRANS:>>"; print_r($aTrans); print "<<:ATRANS<br />";
//~~~~~~~~~~~ Print Stuff


$today = date("l, F j, Y \a\\t g:i a");

$trans = new transTable($loginArr);
$sum = $trans->dailySummary();

$actionPhpSelf =<<<EOD
{$_SERVER['PHP_SELF']}
EOD;

print <<<EOD

    <div id='totalsTitle' ><h2>Summary for Today - $today</h2></div>

    <div id='closeOutSummary'>
    <table>
        <tr>
            <th colspan='3'>Deposits</th>
            <th colspan='3'>Credits</th>
            <th colspan='5'>Sales</th>
            <th colspan='6'>Payments</th>
            <th>Today's Total</th>
        </tr>
        <tr>
            <th>Member</th>
            <th>Key</th>
            <th>Total</th>
            
            <th>Refunds</th>
            <th>Work</th>
            <th>Misc</th>
            
            <th>Purchases</th>
            <th>Bulk Orders</th>
            <th>Extras</th>
            <th>Dues</th>
            <th>Total</th>
            
            <th>Checks</th>
            <th>Money Orders</th>
            <th>Credit</th>
            <th>Debit</th>
            <th>EBT</th>
            <th>Total</th>
            <td rowspan='2'>$sum[total]</td>
        </tr>
        <tr>
            <td>$sum[memDep]</td>
            <td>$sum[keyDep]</td>
            <td>$sum[deposits]</td>
            
            <td>$sum[credits]</td>
            <td>$sum[workCredit]</td>
            <td>$sum[misc]</td>
            
            <td>$sum[purchases]</td>
            <td>$sum[bulk]</td>
            <td>$sum[extras]</td>
            <td>$sum[dues]</td>
            <td>$sum[sales]</td>
            
            <td>$sum[checks]</td>
            <td>$sum[mo]</td>
            <td>$sum[credit]</td>
            <td>$sum[debit]</td>
            <td>$sum[ebt]</td>
            <td>$sum[payments]</td>
        </tr>
    </table>
    </div>
    
    <div id='reconcileTitle' >
    <h2>Reconcile Credits and Debits for Today</h2>
    </div>
    
EOD;

$reconcile = new reconcile($loginArr);

print "<div id='reconcileSummary' >";
print $reconcile->form();
print "</div>";

print "<div id='reconcileItems' >";

if(isset($_POST['reconList'])) {
    switch($_POST['reconList']) {
        case 'Reconcile Checks':
            print $reconcile->reconcile('c');
        break;
        case 'Reconcile Credits':
            print $reconcile->reconcile('d');
        break;
        case 'Reconcile Money Orders':
            print $reconcile->reconcile('a');
        break;
        case 'Reconcile EBT':
            print $reconcile->reconcile('f');
        break;
    }
}
print "</div>";

print $htmlTail;

?>
