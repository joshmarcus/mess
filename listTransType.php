<?php

include 'functions.php';

$role = $_GET['ps'];
$spacer = array ('line' => '-------------------------');


switch ($role) {
case 's': $ps = salesName(); break;
case 'p': $ps = payName(); break;
case 'a':
default : $ps = salesName() + $spacer + payName(); break;

}

$t =<<<EOD
		<div style="background: #99CC99;
				    border-style: solid;
				    border-width: 1px;
				    border-color: #990099;
				    width: 150px;"
				    >
				     
EOD;

while ($a = current($ps)) {
	$k = key($ps);
	$v = current($ps);
	
	$t .=<<<EOD
		<div style="padding: 4px;
					height: 14px;"
					onmouseover="this.style.background = '#EEEEEE'"
					onmouseout="this.style.background = '#99CC99'"
					onclick="setType ('$role','$k','$v')"
		>$v</div>
EOD;

next($ps);
}

$t .= "</div>";

echo $t;

?>

