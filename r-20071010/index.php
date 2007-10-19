<?php

// mariposa/index.php

session_start();
            
//~~~~~~ Set up the page ~~~~~~~~~~~
include 'html.php';
include 'nav.php';

print htmlHead();
print htmlMariposa();
//print navHome;


/*
print "SESSION::";
print_r($_SESSION); 
print "::SESSION<br />";
print "POST::";
print_r($_POST);
print "::POST<br />";
*/

if (empty($_POST['Submit'])) {
    
    include 'forms.php';
    print loginForm();

} else {
    include 'functions.php';        
    $login = varlogin();
    print navHome();
    print htmlHomePage($login[user]);
}

print $htmlTail;

?>
            

