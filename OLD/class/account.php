<?php

class account
{
    
    private $link;
    
    public $aID;    // Account ID
    public $aName;  // Account name
    public $mID;    // account contact's ID
    public $modDate;  // date last modified
    public $modID;     // Who modified it
    public $cDate;  // account creation date
    
    public $address;
    
    public $curBal; // current balance
    
    function __construct($loginArr) {
        $this->link = new MyDB($loginArr);
    }

///////////////////////////////////////////////////////////////////////
    
    function getDetails($aID) {
		$this->aID = $aID;
        $q =<<<QUERY
            SELECT  *
            FROM    acct A
            WHERE   (A.aID = $aID)
QUERY;

        $this->link->createResult($q);
        $r = $this->link->getRow();
        
        $this->aName = $r[aName];
        $this->mID   = $r[mID];
        $this->cDate = $r[created];
        $this->modID   = $r[modDate];
        $this->modDate = $r[modDate];
        
        $this->link->closeResult();
        return $r;
        
    } // end of function getDetails
    
///////////////////////////////////////////////////////////////////////

    function getName($ID) {
        
        $this->aID = $ID;
        
        $q =<<<QUERY
            SELECT A.name AS aName
            FROM   acct A
            WHERE  (A.aID = $this->aID)
QUERY;

        $this->link->createResult($q);
        $r = $this->link->getRow();
        
        $this->link->closeResult();
        return $r[aName];
        
    }  //end function getName

///////////////////////////////////////////////////////////////////////

    function getAcctMems($ID) {
    
        $q =<<<QUERY
            SELECT
                CONCAT_WS(' ', given, middle, family) AS fName,
                M.mID,
                A.name, A.mID AS contact
            FROM
                mem M, acct A, acctMem AM
            WHERE
                (AM.mID = M.mID)
            AND (AM.aID = A.aID)
            AND (A.aid = $ID)
            ORDER BY A.name
QUERY;
        $this->link->createResult($q);
        while ($m = $this->link->getRow()){
            $mems[] = $m; 
        }

        $this->link->closeResult();
    
        return $mems;
    } //End function getAcctMems
    
///////////////////////////////////////////////////////////////////////

    function getAcctBal($ID, $end='FALSE', $start='FALSE') {
        
        $this->aID = $ID;
        
        $q =<<<QUERY

        SELECT 
            SUM(IF(T.type<=>'s',amt,0))
            + SUM(IF(T.type<=>'e',amt,0))
            + SUM(IF(T.type<=>'b',amt,0))
            + SUM(IF(T.type<=>'m',amt,0))
            + SUM(IF(T.type<=>'n',amt,0))
            + SUM(IF(T.type<=>'k',amt,0))
            - SUM(IF(T.type<=>'d',amt,0))
            - SUM(IF(T.type<=>'c',amt,0))
            - SUM(IF(T.type<=>'g',amt,0))
            - SUM(IF(T.type<=>'a',amt,0))
            - SUM(IF(T.type<=>'f',amt,0))
            - SUM(IF(T.type<=>'r',amt,0))
            - SUM(IF(T.type<=>'w',amt,0))
            - SUM(IF(T.type<=>'o',amt,0))
            AS bal
        FROM
            trans T
        WHERE
            (T.aID = $this->aID)
        AND	(T.modDate <= '$end')

QUERY;

        $this->link->createResult($q);
        $r = $this->link->getRow();
        $bal = $r[bal];
        
        $this->link->closeResult();
        
        return $bal;
        
    } // end function getAcctBal

////////////////////////////////////////////////////////////////////
   
function table() {
    
    $q  =<<<QUERY
        SELECT
            CONCAT_WS(' ' , given, middle, family) AS fName,
            A.name,
            A.mID AS contact,
            M.mID, A.aID 
        FROM
            mem M, acct A, acctMem AM
        WHERE
            (AM.aID = A.aID)
        AND (AM.mID = M.mID)
        
        GROUP BY
            A.mID ORDER BY A.name
QUERY;

    $t =<<<TABLE
    <table >
        <th>ID</th>
        <th>Account</th>
        <th>Members</th>
        <th>Balance</th>
TABLE;

        $this->link->createResult($q);
        while ($a = $this->link->getRow()){
            $accts[] = $a;
        }
        $this->link->closeResult($q);
        
        reset($accts);

        while ($arr = each($accts)){
            $r = current($arr);
            //$account = new account($this->login);
            $bal = $this->getAcctBal($r[aID]);
        
        $t .=<<<ROWS
            <tr>
                <td>$r[aID]</td>
                <td>
                <a href='acctView.php?id=$r[aID]' >$r[name]</a>
                </td>
            <td>
ROWS;

        $mems = $this->getAcctMems($r[aID]);
        if (count($mems) != NULL) {
            foreach ($mems as $a) {
                if ($a[mID] == $a[contact]){
                    $t .=<<<MEM
                            <a href='memView.php?id=$r[mID]' >
                            $a[fName] (Contact)
                            </a> email@here 215.111.2222 
MEM;
                }
                else $t .=<<<MEM
                            <a href='memView.php?id=$r[mID]' >
                            $a[fName]
                            </a> email@here 215.111.2222
MEM;
                $t .=<<<MEM
                        </a><br />
MEM;
            }
        }
        else print "None";
 
/*            
        $t .=<<<CELL
                </td>
                <td>$ph</td>
                <td><a href='mailto:$r[email]' >EMAIL@HERE</a></td>
                <td class='address'>$adrs</td>
            </tr>"
CELL;
*/
		$t .=<<<CELL
			</td>
			<td>$bal</td>
CELL;
    }
    
    $t .=<<<TABLE
            </table>
TABLE;
    
    return $t;
} // End function table

///////////////////////////////////////////////////////////////////////   
   
}  //end class account
        
?>
