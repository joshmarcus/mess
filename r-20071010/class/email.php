<?php
class email {
    
    private $link;
    
    function __construct($login) {
        $this->link = new MyDB($login);
    }
    
///////////////////////////////////////////////////////////////////////

    function addrs ($ID, $type = 'm') {
        
        if($type == 'm') {
            $field = 'M.mID';
            $table = 'mem M';
        } else {
            $field = 'A.aID';
            $table = 'acct A';
        }
        
        $q =<<<QUERY
            SELECT E.eID, E.email,
                   U.loc, U.public
            FROM   $table, email E, emUser U
            WHERE  (U.type = '$type')
            AND    (M.mID = U.user)
            AND    (E.eID = U.eID)
            AND    ($field = '$ID')
QUERY;

        $this->link->createResult($q);
        
        while($r = $this->link->getRow()) {
            
            $e[] = $r;
        }
        
        $this->link->closeResult();
        return $e;

    } //End function tels
     
///////////////////////////////////////////////////////////////////////
    
///////////////////////////////////////////////////////////////////////

}

?>
