<?php

// mariposa/index.php
session_start();

$_SESSION = array();
            
//~~~~~~ Set up the page ~~~~~~~~~~~
include 'html.php';

print htmlHead();
print htmlTitle('Login');

// Help with debugging 
//print "SESSION::";print_r($_SESSION);print "::SESSION<br />";
//print "POST::";print_r($_POST);print "::POST<br />";

if (empty($_POST['Submit'])) {
    
    include 'login.php';
    loginForm();

} else {
    include 'home.php';        
}

print htmlTail();

?>
            

