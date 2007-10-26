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
			    padding: 4px;
			    padding-right: 20px;
			    border: solid #990099;
			    border-width: 1px 1px 0px 1px;
			    height: 14px;
			    text-align: right;
			    color: #cc0000;"	    
			    onmouseover="this.style.background = '#cc9999'
			    		 this.style.color = '#0000cc'"
			    onmouseout="this.style.background = '#99cc99'
			    		this.style.color = '#cc0000'"
			    onclick="setAccount ('','')">
		Cancel</div>
		<div style="background: #99CC99;
			    border: solid #990099;
			    border-width: 0px 1px 1px 1px;
			    text-align: left;" >		
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

