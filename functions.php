<?php

function varLogin() {
    if ($_POST && $_POST[Submit] == 'Login') {
        //echo "IAMPOST";
        $vars = $_POST;
        $_SESSION[varLogin] = $_POST;
    }
    elseif ($_SESSION[varLogin]) {
        //echo "IAMSESSION";
        $vars = $_SESSION[varLogin];    
    }
    return $vars;
} //end function varLogin

///////////////////////////////////////////////////////////////////////

function phone ($ac, $ex, $num, $ext) {
    $p = "($ac) $ex-$num";
    if($ext) {
        $p .= "ext $ext";
    }
    return $p;
} // End function phone

///////////////////////////////////////////////////////////////////////

function yesNo($b) {
    switch($b) {
        case '0': case 'n': $x = "No";  break;
        case '1': case 'y': $x = "Yes"; break;
        default:            $x = "??";  break;
    }
    return $x;
} //End function yesNo

///////////////////////////////////////////////////////////////////////

function workExempt($b) {
    switch($b) {
        case '0': $x = "Exempt"; break;
        case '1': $x = "Working";    break;
        default:  $x = "??????";     break;
    }
    return $x;
} //End function yesNo

///////////////////////////////////////////////////////////////////////

function statusName($e) {
    switch($e) {
        case 'a':   $s = "Active";  break;
        case 'i':   $s = "Inactive";break;
        case 'l':   $s = "Leave";   break;
        case 'q':   $s = "Quit";    break;
        case 'm':   $s = "Missing"; break;
        default:    $s = "?????"; break; 
    }
    return $s;
} //End function memStatus

///////////////////////////////////////////////////////////////////////

function location($loc) {
    switch($loc) {
        case 'h': $l = "Home";      break;
        case 'w': $l = "Work";      break;
        case 'm': $l = "Mobile";    break;
        case 'v': $l = "Voicemail"; break;
        case 'p': $l = "Pager";     break;
        case 'o': $l = "Other";     break;
        case 'n': $l = "None";      break;
        case 'u': $l = "Unknown";   break;
        default:  $l = "Unknown";   break;
    }
    return $l;
}
    
///////////////////////////////////////////////////////////////////////

function transTypeName ($type) {
    //~~~~ Convert type to make sense ~~~
    switch ($type) {
        case s: $t = "Sales";            break;
        case b: $t = "Bulk";             break;
        case e: $t = "Extras";           break;
        case m: $t = "Dues";             break;
        case n: $t = "Deposit";          break;
        case k: $t = "Key Deposit";      break;
        case d: $t = "Debit Card";       break;
        case c: $t = "Credit Card";      break;
        case g: $t = "Check";            break;
        case a: $t = "Money Order";      break;
        case f: $t = "EBT";              break;
        case r: $t = "Refund or Credit"; break;
        case w: $t = "Work Credit";      break;
        case o: $t = "Misc";             break;
        }
    return $t;
    }  //  end transTypeName

///////////////////////////////////////////////////////////////////////

function getSalesName ($type) {
    //~~~~ Convert type to make sense ~~~
    switch ($type) {
        case s: $t = "Sales";            break;
        case b: $t = "Bulk";             break;
        case e: $t = "Extras";           break;
        case m: $t = "Dues";             break;
        case n: $t = "Deposit";          break;
        case k: $t = "Key Deposit";      break;
        }
    return $t;
    }  //  end transTypeName

///////////////////////////////////////////////////////////////////////

function getPayName ($type) {
    //~~~~ Convert type to make sense ~~~
    switch ($type) {
        case d: $t = "Debit Card";       break;
        case c: $t = "Credit Card";      break;
        case g: $t = "Check";            break;
        case a: $t = "Money Order";      break;
        case f: $t = "EBT";              break;
        case r: $t = "Refund or Credit"; break;
        case w: $t = "Work Credit";      break;
        case o: $t = "Misc";             break;
        }
    return $t;
}  //  end transTypeName

function payName () {
    $a =  array( 'd' => 'Debit Card',
    			 'c' => 'Credit Card',
    			 'g' => 'Check',
    			 'a' => 'Money Order',
    			 'f' => 'EBT',
    			 'r' => 'Refund or Credit',
    			 'w' => 'Work Credit',
    			 'o' => 'Misc'
         );
    return $a;
    }  //  end payName

///////////////////////////////////////////////////////////////////////

function salesName () {
    $a =  array( 's' => 'Sales',
    			 'b' => 'Bulk',
    			 'e' => 'Extras',
    			 'm' => 'Dues',
    			 'n' => 'Deposit',
    			 'k' => 'Key Deposit'
         );
    return $a;
    }  //  end transTypeName

///////////////////////////////////////////////////////////////////////

function escChar ($S)
{

} //End function escChar
?>
