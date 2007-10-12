<?php

class account
{
    
    private $link;
    
    public $aID;    // Account ID
    public $aName;  // Account name
    public $cID;    // account contact's ID
    public $mDate;  // date last modified
    public $mID;     // Who modified it
    public $cDate;  // account creation date
    
    public $address;
    
    public $curBal; // current balance
    
    function __construct($loginArr) {
        $this->link = new MyDB($loginArr);
    }

///////////////////////////////////////////////////////////////////////
    
    function getDetails() {
            
        $q =<<<QUERY
            SELECT  *
            FROM    acct
            WHERE   (acct.ID = $this->aID)
QUERY;

        $this->link->createResult($q);
        $r = $this->link->getRow();
        
        $this->aID   = $r[ID];
        $this->aName = $r[aName];
        $this->cID   = $r[contact];
        $this->cDate = $r[created];
        $this->mID   = $r[modDate];
        $this->mDate = $r[modDate];
        
        $this->link->closeResult();
        
    } // end of function getDetails
    
///////////////////////////////////////////////////////////////////////

    function getName($ID) {
        
        $this->aID = $ID;
        
        $q = "SELECT name FROM acct WHERE (ID = $this->aID)";
        $this->link->createResult($q);
        $r = $this->link->getRow();
        
        $this->link->closeResult();
        return $r[name];
        
    }  //end function getName

///////////////////////////////////////////////////////////////////////

    function getAcctMems($ID) {
    
        $q =<<<QUERY
            SELECT
                CONCAT_WS(' ', given, middle, family) AS fullName,
                mem.ID AS mID,
                name, contact
            FROM
                mem, acct, acctMem
            WHERE
                (acctMem.mem = mem.ID)
            AND (acctMem.acct = acct.ID)
            AND (acct.id = $ID)
            ORDER BY name
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
            SUM(IF(trans.type<=>'s',amt,0))
            + SUM(IF(trans.type<=>'e',amt,0))
            + SUM(IF(trans.type<=>'b',amt,0))
            + SUM(IF(trans.type<=>'m',amt,0))
            + SUM(IF(trans.type<=>'n',amt,0))
            + SUM(IF(trans.type<=>'k',amt,0))
            - SUM(IF(trans.type<=>'d',amt,0))
            - SUM(IF(trans.type<=>'c',amt,0))
            - SUM(IF(trans.type<=>'g',amt,0))
            - SUM(IF(trans.type<=>'a',amt,0))
            - SUM(IF(trans.type<=>'f',amt,0))
            - SUM(IF(trans.type<=>'r',amt,0))
            - SUM(IF(trans.type<=>'w',amt,0))
            - SUM(IF(trans.type<=>'o',amt,0))
            AS bal
        FROM
            trans
        WHERE
            (acct = $this->aID)
        AND	(modDate <= '$end')

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
            CONCAT_WS(' ' , given, middle, family) AS fullName,
            acct.name, acct.contact,
            mem.ID AS mID, acct.ID AS aID 
        FROM
            mem, acct, acctMem
        WHERE
            (acctMem.acct = acct.ID)
        AND (acctMem.mem = mem.ID)
        
        GROUP BY
            acct.contact ORDER BY name
QUERY;

    $t =<<<TABLE
    <table >
        <th>ID</th>
        <th>Account</th>
        <th>Members</th>
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
            //$bal = $this->getAcctBal($r[aID]);
        
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
                $t .= "<a href='memView.php?id=$r[mID]' >";
                if ($a[mID] == $a[contact]){
                    $t .= "$a[fullName] (Contact)";
                }
                else $t .= "$a[fullName]";
                $t .= "</a><br />";
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
    }
    
    $t .=<<<TABLE
            </table>
TABLE;
    
    return $t;
} // End function table

///////////////////////////////////////////////////////////////////////   
   
}  //end class account
        
?>
