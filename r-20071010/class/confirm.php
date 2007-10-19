<?php

//require 'class/MyDB.php';

class confirm {
    
    private $link;
    
    private $transArray = array(
                            'acct'  => '',
                            'who'   => '',
                            'type'  => '',
                            'amt'   => '',
                            'note'  => '',
                            'ref'   => ''
                            );
    
    private $acct;
    private $who;
    private $type;
    private $amt;
    private $note;
    private $ref;
    private $fName;
    private $aName;
    
    function __construct($login) {
        $this->link = new MyDB($login);
    }
    
    private function transArrayToVar() {
         
        $this->acct = $this->transArray[acct];
        $this->who = $this->transArray['who'];
        $this->type = $this->transArray['type'];
        $this->amt = $this->transArray['amt'];
        $this->note = $this->transArray['note'];
        $this->ref = $this->transArray['ref'];
    }
 
    
    function getNames() {
        
        $q =<<<EOD
            SELECT
                    name AS aName,
                    CONCAT_WS(' ', given, middle, family) AS fullName 
            FROM
                    acct, mem
            WHERE
                    (acct.ID = $this->acct)
            AND     (mem.ID = $this->who)
EOD;

        //$link = dblink($l);
        $this->link->createResult($q);
        $row = $this->link->getRow();
        $this->link->closeResult();
        
        $this->fName = $row[fullName];
        $this->aName = $row[aName];
        
    } // end of function fName
    
    function typeString() {
        switch ($this->type) {
            case s:
                $t = "Purchase";
            break;
            case b:
                $t = "Bulk Order";
            break;
            case e:
                $t = "Extras Purchase";
            break;
            case m:
                $t = "Dues";
            break;
            case n:
                $t = "Deposit";
            break;
            case k:
                $t = "Key Deposit";
            break;
            case d:
                $t = "Debit Card Payment";
            break;
            case c:
                $t = "Credit Card Payment";
            break;
            case g:
                $t = "Check Payment";
            break;
            case a:
                $t = "Money Order Payment";
            break;
            case f:
                $t = "EBT Payment";
            break;
            case r:
                $t = "Refund or Credit";
            break;
            case w:
                $t = "Work Credit";
            break;
            case o:
                $t = "Misc";
            break;
            }
    } //end of typeString
    
    function validate($aTrans){
        
        //print "<br />class/confirm.php<br />";
        //print "function validate \$aTrans: "; print_r($aTrans); print "<br />";
        //print "function pre validate \$transArray: "; print_r($aTrans); print "<br />";
        
        $this->transArray = $aTrans;
        $this->transArrayToVar();
        
        //print "function post validate \$transArray: "; print_r($aTrans); print "<br />";
        
        unset($arr);
        unset($s);
        unset($e);
        
        if ($this->acct == '') { $arr[] = " the account"; }
        if ($this->who == '') { $arr[] = "who"; }
        if ($this->type == '') { $arr[] = "type"; }
        if (is_numeric($this->amt) == FALSE) { $arr[] = "amount"; }
        
        switch (count($arr)) {
            case 1:
                $s = "$arr[0].";
            break;
            case 2:
                $s = "$arr[0] and $arr[1].";
            break;
            case 3:
                $s = "$arr[0], $arr[1], and $arr[2].";
            break;
            case 4:
                $s = "$arr[0], $arr[1], $arr[2], and $arr[3].";
            break;
        }
        if (isset($s)) { $e = "Sorry you forgot to fill out $s"; }
        
        return $e;
        
    }  //end of function validate
 
    function setTrans() {
    }  // end of function setTrans
    
    function form() {
        $this->getNames();
        $tN = transType($this->type);
        
        $actionPhpSelf = <<<EOD
            {$_SERVER['PHP_SELF']}
EOD;
        print <<<EOD
        <div id='transHeader'>
            <h2>Please Confirm $tN for $this->aName</h2>
        </div>
        <form    method='POST' 
            action="{$actionPhpSelf}"
        >
        <input type='hidden' name='action' value='submitted' />
        <input type='hidden' name='modID' value='0' />
        <input type='hidden' name='acct' value='$this->acct' />
        <input type='hidden' name='who' value='$this->who' />
        <input type='hidden' name='type' value='$this->type' />
        <input type='hidden' name='amt' value='$this->amt' />
        <input type='hidden' name='note' value='$this->note' />
        <input type='hidden' name='ref' value='$this->ref' />
        
        <div id='transForm' >
        <table name='transConfirm'>
        <tr>
        <th>Account:</th><td>$this->aName</td>
        <th>Who:</th><td>$this->fName</td>
        <th>Ref:</th><td>$this->ref</td>
        <th>Note:</th><td colspan='2'>$this->note</td>
        </tr>
        <tr>
        <th id='confirmType' ><h1>$tN:</h1></th>
        <td id='confirmAmt' ><h1>$this->amt</h1></td>
        <td colspan='3'>
        <input name='Submit' type='submit' value='Accept'>
        <br />And<br />
        <input name='Submit' type='submit' value='Make Payment'>
        </td>
        <td colspan='3'>
        <input name='Submit' type='submit' value='Cancel'>
        <input name='Submit' type='submit' value='Edit'
        </td>
        </tr>
        </table>
        </div>
        </form>
EOD;

        //mysql_free_result($r);


} //end of function form

}  //end of class confirm


?>
