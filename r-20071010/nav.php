<?php

///////////////////////////////////////////////////////////////////////

function navHome() {
    $n =<<<EOD
    <div id="nav">
        <a class='button' href="cashier.php" >Cashier</a>
        <a class='button' href="memList.php" >Members</a>
        <a class='button' href="acctList.php" >Accounts</a>
        <a class='button' href="summary.php" >Summary</a>    
        <a class='button' href="summary.php" >Staff</a>
        <a class='button' href="index.php" >Logout</a>
    </div>
EOD;
    return $n;
}  // End function navHome

///////////////////////////////////////////////////////////////////////

function navCashier() {
    $n =<<<EOD
    <div id="nav">
        <a class='button' href="index.php" >Home</a>
        <a class='button' href="memList.php" >Members</a>
        <a class='button' href="acctList.php" >Accounts</a>
        <a class='button' href="summary.php" >Summary</a>
        <a class='button' href="index.php" >Logout</a>
    </div>
EOD;
    return $n;
} // End function navCashier

///////////////////////////////////////////////////////////////////////

function navCashierTask() {
    $n =<<<EOD
    <div id='navCashierTask'>
        <a class='button' href='closeOut.php' >Close Out</a>
    </div>
EOD;
    return $n;
} // End function navTaskCashier

///////////////////////////////////////////////////////////////////////

function navMemList() {
    $n =<<<EOD
    <div id="nav">
        <a class='button' href="index.php" >Home</a>
        <a class='button' href="acctList.php" >Accounts</a>
        <a class='button' href="summary.php" >Summary</a>
        <a class='button' href="summary.php" >Staff</a>
        <a class='button' href="index.php" >Logout</a>
    </div>
EOD;
    return $n;
} // End function navCashier

///////////////////////////////////////////////////////////////////////

function navMemListTask() {
    $n =<<<EOD
    <div id='navCashierTask'>
        <a class='button' href='summary.php' >New</a>
    </div>
EOD;
    return $n;
} // End function navMemListCashier

///////////////////////////////////////////////////////////////////////

function navMem() {
    $n =<<<EOD
    <div id="nav">
        <a class='button' href="index.php" >Home</a>
        <a class='button' href="memList.php" >Members</a>
        <a class='button' href="acctList.php" >Accounts</a>
        <a class='button' href="summary.php" >Summary</a>
        <a class='button' href="summary.php" >Staff</a>
        <a class='button' href="index.php" >Logout</a>
    </div>
EOD;
    return $n;
} // End function navCashier

///////////////////////////////////////////////////////////////////////

function navMemTask($id, $prev, $next) {
    $n =<<<EOD
    <div id='navMemTask'>
        <a class='button' href='memEdit.php' >New</a>
        <a class='button' href='memEdit.php?id=$id' >Edit</a>
        <a class='button' href='memView.php?id=$prev' >Previous</a>
        <a class='button' href='memView.php?id=$next' >Next</a>
    </div>
EOD;
    return $n;
} // End function navTaskCashier

///////////////////////////////////////////////////////////////////////

function navAcct() {
    $n =<<<EOD
    <div id="nav">
        <a class='button' href="index.php" >Home</a>
        <a class='button' href="memList.php" >Members</a>
        <a class='button' href="acctList.php" >Accounts</a>
        <a class='button' href="summary.php" >Summary</a>
        <a class='button' href="summary.php" >Staff</a>
        <a class='button' href="index.php" >Logout</a>
    </div>
EOD;
    return $n;
} // End function navCashier

///////////////////////////////////////////////////////////////////////

function navAcctTask($id, $prev, $next) {
    $n =<<<EOD
    <div id='navMemTask'>
        <a class='button' href='acctEdit.php' >New</a>
        <a class='button' href='acctEdit.php?id=$id' >Edit</a>
        <a class='button' href='acctView.php?id=$prev' >Previous</a>
        <a class='button' href='acctView.php?id=$next' >Next</a>
    </div>
EOD;
    return $n;
} // End function navTaskCashier


///////////////////////////////////////////////////////////////////////

function navAcctList() {
    $n =<<<EOD
    <div id="nav">
        <a class='button' href="index.php" >Home</a>
        <a class='button' href="memList.php" >Members</a>
        <a class='button' href="summary.php" >Summary</a>
        <a class='button' href="summary.php" >Staff</a>
        <a class='button' href="index.php" >Logout</a>
    </div>
EOD;
    return $n;
} // End function navCashier

///////////////////////////////////////////////////////////////////////

function navAcctListTask() {
    $n =<<<EOD
    <div id='navCashierTask'>
        <a class='button' href='summary.php' >Summary</a>
        <a class='button' href='closeOut.php' >Close Out</a>
    </div>
EOD;
    return $n;
} // End function navTaskCashier

///////////////////////////////////////////////////////////////////////
?>
