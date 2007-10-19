<?php
class tel {
    
    private $link;
    
    function __construct($login) {
        $this->link = new MyDB($login);
    }
    
///////////////////////////////////////////////////////////////////////

    function tels ($ID, $type = 'm') {
        
        if($type == 'm') {
            $field = 'M.mID';
            $table = 'mem M';
        } else {
            $field = 'A.aID';
            $table = 'acct A';
        }
        
        $q =<<<QUERY
            SELECT T.tID,
                   T.ac, T.ex, T.num, T.ext, 
                   TU.loc, TU.public
            FROM   $table, tel T, telUser TU
            WHERE  (TU.type = '$type')
            AND    (M.mID = TU.user)
            AND    (T.tID = TU.tID)
            AND    ($field = '$ID')
QUERY;

        $this->link->createResult($q);
        
        while($r = $this->link->getRow()) {
            
            $r['tel'] = $this->format($r['ac'], $r['ex'], $r['num'], $r['ext']);
            $t[] = $r;
        }
        
        $this->link->closeResult();
        return $t;

    } //End function tels
     
///////////////////////////////////////////////////////////////////////

    function format($ac, $ex, $num, $ext) {
        
        $p =<<<PHONE
                    ($ac) $ex-$num
PHONE;
        if($ext) {
            $p .=<<<PHONE
                    ext $ext
PHONE;
        }
        return $p;
        
    }  // End function format
    
///////////////////////////////////////////////////////////////////////

}

?>
