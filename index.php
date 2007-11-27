<?php
session_start();

$_SESSION = array();

include 'functions.php';
include 'class/MyDB.php';

include 'html.php';
print htmlHead('Login');
//print htmlTitle('Login');

//~~~~~~~~~~~ Print Stuff for debuging
print "<br />SESSION:>> "; print_r($_SESSION); print "<<:SESSION<br />";
//print "login:>>"; print_r($login); print "<<:login<br />";
//print "GET:>>"; print_r($_GET); print "<<:GET<br />";
//print "POST:>>"; print_r($_POST); print "<<:POST<br />";
//print "xTRANS:>>"; print_r($xArray); print "<<:xTRANS<br />";
//~~~~~~~~~~~ Print Stuff for debugging

/*
if (empty($_POST['Submit'])) {
    
    include 'login.php';
    loginForm();

} else {
    include 'home.php';        
}

print htmlTail();
*/
?>
            
<script type="text/javascript" src="functions.js"></script>

<div id='content' >

<h2>Please login to the database</h2>

<form method='POST' action='login.php' name='login' >
    
    <table>
    <tr>
        <th>User Name:</th>
        <td><input type='text' name='user'></td>
    </tr>
    <tr>
        <th>Password:</th>
        <td><input type='password' name='pass'></td>
    <tr>
        <td colspan='2' style='text-align: right;';>
            <input name='Submit' type='image' value='Login' src='images/Login.png'/>
        </td>
    </tr>
    </table>

</form>
</div>
