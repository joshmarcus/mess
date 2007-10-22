<?php
class address
{
    private $link;
    private $address;
    
    function __construct($loginArr) {
        $this->link = new MyDB($loginArr);
    }

///////////////////////////////////////////////////////////////////////

    function getAddrs($hID) {
    	$q =<<<QUERY
    		SELECT H.hID, H.num, H.street, H.adrs2,
    		       H.city, H.state, H.country, H.zip1, H.zip2
    		FROM   adrs H
    		WHERE  H.hID = '$hID'
QUERY;

		$this->link->createResult($q);
        $this->address = $this->link->getRow();
        $this->link->closeResult();
        
        return $this->address;
        
    } //End function getAddrs

///////////////////////////////////////////////////////////////////////

	function format() {
		$a = $this->address;
		unset($s);
		unset($a1);
		unset($c);
		
		if($a['num'] && $a['street']) {
			$adrs1  = "$a[num] $a[street]<br/>";
		} elseif($a['num']) {
			$adrs1  = $a['num'] . "<br/>";
		} elseif($a['street']) {
			$adrs1  = $a['street'] . "<br/>";
		}

		if($a['adrs2']) $s .= $a['adrs2'] . "<br/>";
		
		if($a['zip1'] && $a['zip2']) {
			$z = $a['zip1'] . "-" . $a['zip2'] . "<br/>";
		} elseif($a['zip1']) {
			$z = $a['zip1'] . "<br/>";
		}
		
		if($a['city'] && $a['state']) {
			$c = $a['city'] . ', ' . $a['state'] . "<br/>";
		} elseif($a['city']) {
			$c = $a['city'] . "<br/>";
		} elseif($a['state']) {
			$c = $a['state'] . "<br/>";
		}
		
		if($c && $z) {
			$c = rtrim($c, "<br/>");
			$adrs3 = $c . "  " . $z;
		} 
		
		if($adrs1) $s  = $adrs1;
		if($adrs2) $s .= $adrs2;
		if($adrs3)     $s .= $adrs3;
		if($s['country']) $s .= $a['country'];
		$s = rtrim($s, "<br/>");
		return $s;
	} // End function format

///////////////////////////////////////////////////////////////////////
}
    
?>
