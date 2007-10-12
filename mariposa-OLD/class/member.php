<?php

class member{
    
    private $link;
    
    private $mID;
    private $fName;
    private $aPID;      // Primary aID
    private $paName;     // Primary acct name
    private $jID;
    private $jName;
    private $hID;

    private $pContact;  // Prefered contact type (e or p)
    private $ePID;      // Primary ePID
    private $pEmail;    // Primary email
    private $tPID;      // Primary tID
    private $pTel;      // Primary telephone
    
    private $status;
    private $key;
    private $join;
    private $memDetails;
    
    function __construct($login) {
        $this->link = new MyDB($login);
    }
    
///////////////////////////////////////////////////////////////////////

    function getName($ID) {
        
        $this->mID = $ID;
        
        $q =<<<QUERY
            SELECT CONCAT_WS(' ', given, middle, family) AS fName
            FROM   mem M
            WHERE  (M.mID = $this->mID)
QUERY;

        $this->link->createResult($q);
        $r = $this->link->getRow();
        
        $this->link->closeResult();
        return $r[fName];
        
    }  //end function getName
    
///////////////////////////////////////////////////////////////////////

function memDetails($ID) {
    
    $q =<<<QUERY
        SELECT
            CONCAT_WS( ' ', given, middle, family ) AS fName,
            M.aID    AS aPID,
            M.prefer AS pContact,
            M.eID    AS ePID,
            M.tID    AS tPID,
            M.jID, M.status, M.key, M.join, M.hID,
            T.tID, T.ac, T.ex, T.num, T.ext,
            J.name AS jName,
            E.email  AS paEmail,
            A.name   AS paName
        FROM mem M
        LEFT JOIN acct  A ON (M.aID = A.aID)
        LEFT JOIN email E ON (M.eID = E.eID)
        LEFT JOIN tel   T ON (M.tID = T.tID)
        LEFT JOIN job   J ON (M.jID = J.jID)
        WHERE (M.mID = $ID)
QUERY;

    $this->link->createResult($q);
    $r = $this->link->getRow();
    $this->link->closeResult();
    
    $this->mID      = $r[mID];
    $this->fName    = $r[fName];
    
    $this->aPID     = $r[aPID];
    $this->paName    = $r[paName];
    $this->pContact = $r[pContact];
    $this->ePID     = $r[ePID];
    $this->tPID  = $r[tPID];
    $this->jID   = $r[jID];
    $this->hID     =$r['hID'];
    $this->jName = $r[jName];
    $this->status = $r[status];
    $this->key = $r[key];
    
    $this->join = $r[join];
    
    $this->pTel = phone($r['ac'], $r['ex'], $r['num'], $r['ext']);
    
    $this->memDetails = array(
                            'mID'      => $this->mID,
                            'fName'    => $this->fName,
                            'aPID'     => $this->aPID,
                            'paName'    => $this->paName,
                            'pContact' => $this->pContact,
                            'ePID'     => $this->ePID,
                            'pEmail'   => $this->pEmail,
                            'tPID'     => $this->tPID,
                            'pTel'     => $this->pTel,
                            'jID'      => $this->jID,
                            'hID'      => $this->hID,
                            'jName'    => $this->jName,
                            'status'   => $this->status,
                            'key'      => $this->key,
                            'join'     => $this->join
                        );
                        
    return $this->memDetails;
    
    

} //End function memDetails

///////////////////////////////////////////////////////////////////////

	function contact($ID) {
		
		$q =<<<QUERY
			SELECT CONCAT_WS(' ', given, middle, family) AS fName,
			       M.prefer, M.eID, M.tID, M.hID,
			       E.email, EU.loc AS eLoc,
			       T.ac, T.ex, T.num, T.ext, TU.loc AS tLoc
			FROM   mem M
			LEFT JOIN email E ON (E.eID = '$ID')
			LEFT JOIN tel T   ON (T.tID = '$ID')
			LEFT JOIN adrs H  ON (H.hID = '$ID')
			LEFT JOIN emUser  EU ON (EU.user = $ID) AND (EU.type = 'm')
			LEFT JOIN telUser TU ON (TU.user = $ID) AND (TU.type = 'm')
			WHERE (M.mID = '$ID')
QUERY;


    $q =<<<QUERY
        SELECT
            CONCAT_WS( ' ', given, middle, family ) AS fName,
            M.aID    AS aPID,
            M.prefer,
            M.eID    AS ePID,
            M.tID    AS tPID,
            M.jID, M.status, M.key, M.join, M.hID,
            T.tID, T.ac, T.ex, T.num, T.ext,
            J.name AS jName,
            E.email,
            A.name   AS paName
        FROM mem M
        LEFT JOIN acct  A ON (M.aID = A.aID)
        LEFT JOIN email E ON (M.eID = E.eID)
        LEFT JOIN tel   T ON (M.tID = T.tID)
        LEFT JOIN job   J ON (M.jID = J.jID)
        WHERE (M.mID = $ID)
QUERY;
		$this->link->createResult($q);
        $r = $this->link->getRow();
        $this->link->closeResult();
        
        return $r;
        
	} //End function contact
	
///////////////////////////////////////////////////////////////////////
function memAccts ($ID) {
    
    $q =<<<QUERY
        SELECT T.ID AS tID,
               T.ac, T.ex, T.num, T.ext,
               TU.loc
        FROM   tel T, mem M, telUser TU
        WHERE  (TU.type = 'm')
        AND    (M.ID = TU.user)
        AND    (T.ID = TU.tel)
        AND    (M.ID = '$ID')
QUERY;
    
    $this->link->createResult($q);
    while($r = $this->link->getRow()) {
        $p = "($r[ac]) $r[ex]-$r[num]";
        if($ext) {
            $p .= "ext $r[ext]";
        }
        $r['tel'] = $p;
        $t[] = $r;
    }
    $this->link->closeResult();
    return $t;

} // End function memAccts

///////////////////////////////////////////////////////////////////////

function table() {
    
    $q  =<<<QUERY
        SELECT
            CONCAT_WS( ' ', given, middle, family ) AS fName,
            A.name AS aName,
            M.mID, M.aID,
            M.eID AS ePID, M.tID AS tPID,
            J.jID, J.name AS jName,
            M.prefer, M.status,
            M.key, M.join,
            E.email, T.*
        FROM
            mem M
        LEFT JOIN acct A  ON (M.aID = A.aID)
        LEFT JOIN email E ON (M.eID = E.eID)
        LEFT JOIN tel T   ON (M.tID = T.tID)
        LEFT JOIN job J   ON (M.jID = J.jID)
        ORDER BY M.given
QUERY;

    $t =<<<TABLE
    <table >
    <tr>
        <th>ID</th>
        <th>Name</th>
        <th>Accounts</th>
        <th>Prefered Contact</th>
        <th>Other Contact</th>
        <th>Status</th>
        <th>Job</th>
        <th>Key</th>
        <th>Member Since</th>
    </tr>
TABLE;

        $this->link->createResult($q);
        
        while ($r = $this->link->getRow()){
            $memStatus = statusName($r[status]);
            $key = yesNo($r[key]);
            
            if($r[tPID]) {
                $phone = phone($r[ac], $r[ex], $r[num], $r[ext]);
            }
            
            switch($r[prefer]) {
                case 'e':
                    $primary = $r[email];
                    $other = $phone;
                break;
                case 'p':
                    $primary = $phone;
                    $other = $r[email];
                break;
            }
            
            $t .=<<<ROW
            <tr>
                <td>$r[aID]</td>
                <td>
                <a href='memView.php?id=$r[mID]' >$r[fName]</a>
                </td>
                <td>
                <a href='acctView.php?id=$r[mID]' >$r[aName]</a></td>
                <td>$primary</td>
                <td>$other</td>
                <td>$memStatus</td>
                <td><a href='jobView.php?id=$r[jID]' >$r[jName]</a></td>
                <td>$key</td>
                <td>$r[join]</td>
ROW;
        }
        
        $this->link->closeResult($q);

        $t .=<<<TABLE
            </table>
TABLE;
    
    return $t;
    
} // End function table

///////////////////////////////////////////////////////////////////////   
   
}
        
?>
