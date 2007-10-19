<?php

//require 'class/MyDB.php';

class trans
{
    
    private $link;
    
    private $xArray ;
    
    private $aID;
    private $mID;
    private $sale;
    private $saleAmt;
    private $pay;
    private $payAmt;
    private $note;
    private $ref;
    
    private $modID = '0';
    
    private $fName;
    private $aName;
    private $saleName;
    private $payName;

    function __construct($login) {
        $this->link = new MyDB($login);
        $this->clearXArray();
        $this->xArrayToVar();
    }

///////////////////////////////////////////////////////////////////////
    
    function clearXArray() {
        $this->xArray = array(
                            'aID'     => '',
                            'mID'     => '',
                            'aName'   => '',
                            'fName'   => '',
                            'sale'    => '',
                            'saleAmt' => '',
                            'pay'     => '',
                            'payAmt'  => '',
                            'note'    => '',
                            'ref'     => ''
                            );
    }

///////////////////////////////////////////////////////////////////////
                            
    private function xArrayToVar() {
         
        $this->aID     = $this->xArray['aID'];
        $this->mID     = $this->xArray['mID'];
        $this->aName   = $this->xArray['aName'];
        $this->fName   = $this->xArray['fName'];
        $this->sale    = $this->xArray['sale'];
        $this->saleAmt = $this->xArray['saleAmt'];
        $this->pay     = $this->xArray['pay'];
        $this->payAmt  = $this->xArray['payAmt'];
        $this->note    = $this->xArray['note'];
        $this->ref     = $this->xArray['ref'];

    } //end of function xArrayToVar

///////////////////////////////////////////////////////////////////////

function memName() {
        
        $q =<<<EOD
            SELECT  A.name AS aName,
                    CONCAT_WS(' ', given, middle, family) AS fName 
            FROM
                    acct A, mem M
            WHERE
                    (A.aID = $this->aID)
            AND     (M.mID = $this->mID)
EOD;

        //$link = dblink($l);
        $this->link->createResult($q);
        $row = $this->link->getRow();
        $this->link->closeResult();
        
        $this->fName = $row[fName];
        $this->aName = $row[aName];
        
    } // end of function memName

///////////////////////////////////////////////////////////////////////    
    private function getType() {
        switch ($this->type) {
            case 's':
                $this->tName = "Purchase";

            break;
            case 'b':
                $this->tName = "Bulk Order";
            break;
            case 'e':
                $this->tName = "Extras Purchase";
            break;
            case 'm':
                $this->tName = "Member Dues";
            break;
            case 'n':
                $this->tName = "Member Deposit";
            break;
            case 'k':
                $this->tName = "Key Deposit";
            break;
            case 'd':
                $this->tName = "Debit Card Payment";
            break;
            case 'c':
                $this->tName = "Credit Card Payment";
            break;
            case 'g':
                $this->tName = "Check Payment";
            break;
            case 'a':
                $this->tName = "Money Order Payment";
            break;
            case 'f':
                $this->tName = "EBT Payment";
            break;
            case 'r':
                $this->tName = "Refund or Credit";
            break;
            case 'w':
                $this->tName = "Work Credit";
            break;
            case 'o':
                $this->tName = "Misc";
            break;
            }
            
    } //end of getType

///////////////////////////////////////////////////////////////////////

    private function listAccts () {
        
        $q =<<<QUERY
            SELECT   A.aID,
                     A.name AS aName
            FROM     acct A
            ORDER BY A.name
QUERY;

        $this->link->createResult($q);
        $s = '';    
        while ( $a = $this->link->getRow()) {
            $aID = (integer) $a[aID];
            $aN = $a[aName];
            $s .=<<<EOD
                <option value='$aID' >$aN<br />
EOD;
        }
        
        $this->link->closeResult();    
        return $s;
    }  // end of function listaccts

///////////////////////////////////////////////////////////////////////

    private function setAcct(){

        $q = <<<EOD
        SELECT A.name AS aName
        FROM   acct A
        WHERE  (A.aID = $this->aID)
EOD;

        $this->link->createResult($q);
        $r = $this->link->getRow();
        $this->link->closeResult();    
        $this->aName = $r['aName'];

        $s = <<<EOD
            <option value='$this->aID' >$r[aName]</option>
EOD;
        return $s;
    } //end of function setAcct

///////////////////////////////////////////////////////////////////////

	private function selectAcct() {
		
		$f =<<<SELECT
		<select tabindex='1' onchange="this.form.submit()" name='aID' >
SELECT;
		if($this->aID) {
        	$f .= $this->setAcct();
        } else $f .=<<<OPTION
        			<option value='' >-- Please Select --
OPTION;

    	$f .= $this->selectAcct;
		$f .= $this->listAccts();    
        $f .=<<<SELECT
        	</select>
SELECT;

        return $f;
        
	} //end function selrctAcct

///////////////////////////////////////////////////////////////////////
    private function selectWhom() {
    	
    	$f  = "<select tabindex='2' name='mID'>";
        
        if($this->aID) {
            
            $f .= $this->listAcctMems();
            
            $f .=<<<EOD
                    <option value='' >
                    <option value='' >---- Other Members ----</option>";
                    <option value='' >
EOD;
            $f .= $this->listAllMems();
        }
        else $f .= "<option value='' >--- Select Account First ---";
        
        $f .= "</select>";
            
        return $f;
        
    } //end of function whom

///////////////////////////////////////////////////////////////////////
    
private function selectSale() {
    // For now we can make only purchases
	$f =<<<OPTION
		<select tabindex='3' name='sale' >
		<option value='s' >---- Purchase ----------
		</select>
OPTION;

/*      
    unset($s);
    unset($f);
    
    $f =<<<EOD
            <select name='sale' >
EOD;
	
    if($this->type) {
		
 
        $this->getType($this->sale);
        
        $f .= "<option value='$this->sale' >$this->tName";
    } else $f .= "<option value='' >--- Select ---";
            
    $f .=<<<OPTION
            <option value='b' >Bulk
            <option value='e' >Extras
            <option value='m' >Dues
            <option value='n' >Deposit
            <option value='k' >Key Deposit            
            <option value='r' >Refund or Credit
            <option value='w' >Work Credit
            <option value='o' >Misc
        </select>
OPTION;
*/        
    return $f;
        
} //end of function selectSale

///////////////////////////////////////////////////////////////////////
   
private function selectPayment() {
          
    unset($s);
    unset($f);
    
    $f =<<<SELECT
            <select tabindex='5' name='pay' >
SELECT;

    if($this->type) {
        $this->getType($this->type);
        
        $f .=<<<OPTION
        	<option value='$this->type' >$this->tName
OPTION;

    } else $f .=<<<OPTION
    		<option value='' >--- Select Payment---
OPTION;
        
    $f .=<<<OPTION
            <option value='c' >Credit Card
            <option value='d' >Debit Card
            <option value='g' >Check
            <option value='a' >Money Order
            <option value='f' >EBT
        </select>
OPTION;

	return $f;

	
        
} //end of function selectPayment


///////////////////////////////////////////////////////////////////////

    private function listAcctMems(){
    
        $q =<<<EOD
            SELECT  M.mID,
                    CONCAT_WS(' ', given, middle, family) AS fName
            FROM    mem M, acct A, acctMem AM
            WHERE   (A.aID = $this->aID)
            AND     (AM.mID = M.mID)
            AND     (AM.aID = A.aID)
EOD;

        $this->link->createResult($q);
        $s = '';

        if( $this->link->getNumRows() > 1 ) {
            $s .=   "<option value='' > ---- Account Members ----
                    <option value='' >";
        }
    
        while ( $mem = $this->link->getRow()) {
            $mID = (integer) $mem[mID];
            $mN = $mem[fName];
            $s .=<<<EOD
                <option value='$mID' >$mN
EOD;
        }
        $this->link->closeResult();
        
        return $s;
        
    } //End of finction listAcctMems

///////////////////////////////////////////////////////////////////////

    private function listAllMems(){

        $q =<<<EOD
            SELECT  M.mID,
                    CONCAT_WS(' ', M.given, M.middle, M.family) AS fName
            FROM    mem M ORDER BY fName
EOD;

        $this->link->createResult($q);
        $s = '';
        while ( $mem = $this->link->getRow()) {
            $mID = (integer) $mem[mID];
            $mN = $mem[fName];
            $s .=<<<EOD
                <option value='$mID' >$mN
EOD;
        }
        
        $this->link->closeResult();    

        return $s;    
    } // End of function listAllNames

///////////////////////////////////////////////////////////////////
//
// Validate Transaction

function validate($aTrans){
        
        //print "<br />class/confirm.php<br />";
        //print "function validate \$aTrans: "; print_r($aTrans); print "<br />";
        //print "function pre validate \$xArray: "; print_r($aTrans); print "<br />";
        
        $this->xArray = $aTrans;
        $this->xArrayToVar();
        
        //print "function post validate \$xArray: "; print_r($aTrans); print "<br />";
        
        unset($arr);
        unset($s);
        unset($e);
        
        if ($this->aID == '') { $arr[] = " the account"; }
        if ($this->mID == '') { $arr[] = "who"; }
        
        // If the
        if ((is_numeric($this->payAmt) == FALSE) &&
            (is_numeric($this->saleAmt) == FALSE) &&
            $this->pay == '') {
            	
            	$arr[] = "amount and type of transaction";
        }

        if (is_numeric($this->payAmt) && $this->pay == '' ) {
        	
        	$arr[] = "type of payment"; }
        
        switch (count($arr)) {
        case 1: $s = "$arr[0]."; break;
        case 2: $s = "$arr[0] and $arr[1]."; break;
        case 3: $s = "$arr[0], $arr[1], and $arr[2]."; break;
        case 4: $s = "$arr[0], $arr[1], $arr[2], and $arr[3]."; break;
        }
        if (isset($s)) { $e = "Sorry you forgot to fill out $s"; }
        
        return $e;
        
    }  //end of function validate

///////////////////////////////////////////////////////////////////////
 
    function insertTrans($aTrans) {
        
        $this->xArray = $aTrans;
        $this->xArrayToVar();
        
        if($this->sale) {
	        $qs  =<<<QUERY
    	        INSERT INTO trans
        	            ( date, mID, aID, note, type, ref, amt, modID )
            	VALUES( 'DATE(NOW())',
                	    '$this->mID',
	                    '$this->aID',
	                    '$this->note',
	                    '$this->sale',
	                    '$this->ref',
	                    '$this->saleAmt',
	                    '$this->modID'
	                    )
QUERY;

			$this->link->insertQuery($qs);
		}
        
        if($this->pay) {
	        $qp  =<<<QUERY
    	        INSERT INTO trans
        	            ( date, mID, aID, note, type, ref, amt, modID )
            	VALUES( 'DATE(NOW())',
                	    '$this->mID',
	                    '$this->aID',
	                    '$this->note',
	                    '$this->pay',
	                    '$this->ref',
	                    '$this->payAmt',
	                    '$this->modID'
	                    )
QUERY;

			$this->link->insertQuery($qp);
		}
		
    }  // end of function insertTrans
       
//////////////////////////////////////////////////////////////////

function form ($aTrans) {
        
    $this->xArray = $aTrans;
    $this->xArrayToVar();
    /*
    $sA = $this->selectAcct();
	$aName = $this->aName;
	
	$sN = $this->selectWhom();
	$fName = $this->fName;
	*/
	
    $form =<<<EOD
        <div id='transForm'>
        <form    method='POST' action={$_SERVER['PHP_SELF']} >
            <input type='hidden' name='action' value='submitted' />
            <input type='hidden' name='modID' value='0' />
            <input type='hidden' name='aName' value='${aName}' />
            <input type='hidden' name='fName' value='{$fName}' />
            <table name='trans'>
            <tr>
                <th>Account</th>
                <th>Who</th>
                <td>
                	{$this->selectPayment()}
                </td>
                 <td>
                <input tabindex='6'
                	   type='text' size='10'
                	   name='payAmt'
                	   value='{$aTrans[payAmt]}'/>
            </td>
          
            </tr>
            <tr>
                <td>
                	{$this->selectAcct()}
                	</td>
                <td>
                	{$this->selectWhom()}
                </td>
          		<td>
          			{$this->selectSale()}
          		</td>
            	<td>
                	<input tabindex='4' 
                    	   type='text' 
                    	   size='10' 
                    	   name='saleAmt' 
                    	   value='{$aTrans[saleAmt]}'/>
            	</td>
        	</tr>
        	<tr>
            	<th colspan='2'>Note</th>
            	<th>Ref</th>
            	<td>
                	<input tabindex='8' 
                	       name='Submit' 
                	       type='submit' value='Next' >
            	</td>
        	</tr>
        	<tr>
            	<td colspan='2'>
                	<input  tabindex='6' 
                	        type='text' 
                	        size='70' 
                	        name='note' 
                	        value='{$aTrans[note]}'/>
            	</td>
            	<td>
                	<input tabindex='7' 
                	       type='text' 
                	       size='10' 
                	       name='ref' 
                	       value='{$aTrans[ref]}'/>
            	</td>
            	<td>
                	<input tabindex='9' 
                	       name='Submit' 
                	       type='submit' value='Cancel' >
	            </td>
    	    </tr>
    	</table>
    </form>
    </div>
EOD;

        return $form;
        
    }  //end of function form

////////////////////////////////////////////////////////////////////
//
// Confirm Transaction

    function confirm() {
    	
    	if($this->sale) {
        	$saleName = transTypeName($this->sale);
		} else $saleName = "Purchase";
		
		if($this->pay) {
        	$payName = transTypeName($this->pay);
		} else $payName = "Payment";
       
        $saleAmt = $this->saleAmt;
        $payAmt = $this->payAmt;
        
        if(!$saleAmt) $saleAmt = "0.00";
        if(!$payAmt) $payAmt = "0.00";
        	
        $actionPhpSelf = <<<EOD
            {$_SERVER['PHP_SELF']}
EOD;
        print <<<EOD
        <div id='transHeader'>
            <h2>Please Confirm Transaction</h2>
        </div>
        <form    method='POST' 
            action="{$actionPhpSelf}"
        >
        <input type='hidden' name='action' value='submitted' />
        <input type='hidden' name='modID' value='0' />
        <input type='hidden' name='aID' value='$this->aID' />
        <input type='hidden' name='mID' value='$this->mID' />
        <input type='hidden' name='aName' value='$this->aName' />
        <input type='hidden' name='fName' value='$this->fName' />
        <input type='hidden' name='sale' value='$this->sale' />
        <input type='hidden' name='saleAmt' value='$this->saleAmt' />
        <input type='hidden' name='pay' value='$this->pay' />
        <input type='hidden' name='payAmt' value='$this->payAmt' />
        <input type='hidden' name='note' value='$this->note' />
        <input type='hidden' name='ref' value='$this->ref' />
        
        <div id='transForm' >
        <table>
     
        <tr>
        <th class='confirm' >Account:</th>
        <td class='confirm' >$this->aName</td>
        <th class='confirm' >$saleName:</th>
        <td class='confirm' >$saleAmt</td>
        
         <td rowspan='2'>
        <input name='Submit' type='submit' value='Accept'><br />
        <input name='Submit' type='submit' value='Edit' ><br />
        <input name='Submit' type='submit' value='Cancel'>
        </td>
        
        </tr>
        <tr>
        
        
        <th class='confirm' >Who:</th>
        <td class='confirm' >$this->fName</td>
        
        <th class='confirm' >$payName:</th>
        <td class='confirm' >$payAmt</td>
        </tr>
        <tr>
        <th>Ref:</th><td>$this->ref</td>
        <th>Note:</th><td colspan='2'>$this->note</td>
        </tr>
        </table>
        </div>
        </form>
EOD;

    } //end of function confirm

///////////////////////////////////////////////////////////////////////

} //end of class trans

?>
