<?php

class reconcile
{

private $link;
private $tName;
private $tFilter;
    
    function __construct($login) {
        $this->link = new MyDB($login);
    }

///////////////////////////////////////////////////////////////////////

private function nameType($type) {
        switch ($type) {
            case d:
                $this->tName = "Debit and Credit";
                $this->tFilter =<<<FILTER
                                (T.type = 'c' OR T.type = 'd')
FILTER;
            break;
            case c:
                $this->tName = "Checks";
                $this->tFilter =<<<FILTER
                                (T.type = 'g')
FILTER;
            break;
            case a:
                $this->tName = "Money Orders";
                $this->tFilter =<<<FILTER
                                (T.type = 'a')
FILTER;
            break;
            case f:
                $this->tName = "EBT Payments";
                $this->tFilter =<<<FILTER
                                (T.type = 'f')
FILTER;
            break;
            }
            
    } //end of nameType

//////////////////////////////////////////////////////////////////////

private function summary() {
    $q =<<<EOD
        SELECT
            SUM(IF(type<=>'d',amt,0))
            + SUM(IF(type<=>'c',amt,0)) AS crDbt,
            
            SUM(IF(type<=>'g',amt,0)) AS checks,
            SUM(IF(type<=>'a',amt,0)) AS mo,
            SUM(IF(type<=>'f',amt,0)) AS ebt
        
        FROM    trans
        WHERE   (DATE(modDate) = DATE(NOW()))
        GROUP BY date
EOD;
    
    $this->link->createResult($q);
    $arr = $this->link->getRow();
    $this->link->closeResult();
    
    return $arr;
    
} // End function summary

//////////////////////////////////////////////////////////////////////
function reconcile($type) {
    
    $this->nameType($type);
    
    $q =<<<QUERY
                SELECT
                    TIME(T.modDate) AS tTime,
                    T.xID, A.aID,
                    A.name, T.amt, T.ref
                FROM
                    trans T, acct A
                WHERE
                    (DATE(T.modDate) = CURDATE())
                AND    (T.aID = A.aID)
                AND    $this->tFilter
                ORDER BY
                    T.modDate DESC
QUERY;

    $this->link->createResult($q);
    
    $f =<<<FORM
    <h3>$this->tName</h3>
    <form method='POST' action={$_SERVER['PHP_SELF']} >
    <input type='hidden' name='action' value='reconcile' />
    <table>
        <tr>
            <th>Time</th>
            <th>Number</th>
            <th>Reference</th>
            <th>Account</th>
            <th>Amount</th>
            <th>Reconciled?</th>
        </tr>
FORM;

    while ($r = $this->link->getRow()){
           
        $f .=<<<ROW
            <tr>
                <td>$r[tTime]</td>
                <td>$r[xID]</td>
                <td>$r[ref]</td>
                <td><a href='viewAcct.php?id=$r[aID]' >$r[name]</a></td>
                <td>$r[amt]</td>
                <td>No
                    <input type='radio'checked name='$r[xID]' value='n' />
                    Yes
                <input type='radio' name='$r[xID]' value='y' />
                </td>
            </tr>
ROW;
        }
        
        $this->link->closeResult();
        
        $f .=<<<FORM
                    <tr>
                        <td colspan='6'>
                        <input type='submit' name='reconDone'value='Done'>
                        </td>
                    </tr>
                </table>
                </form>
FORM;

    
    return $f;
    
} // End function reconcile


//////////////////////////////////////////////////////////////////////

    function form() {
    
    $sum = $this->summary();
    
    $actionPhpSelf = <<<EOD
                        {$_SERVER['PHP_SELF']}
EOD;

    $f =<<<FORM
    <h3>Summary</h3>
    <form name='reconcileSummary' method='POST' action={$_SERVER['PHP_SELF']} >
    
    <table>
        <tr>
            <th>Checks</th>
            <td>$sum[checks]</td>
            <td><input type='submit' name='reconList' value='Reconcile Checks'></td>
        </tr>
        <tr>
            <th>Money Orders</th>
            <td>$sum[mo]</td>
            <td><input type='submit' name='reconList' value='Reconcile Money Orders'></td>
        </tr>
        <tr>
            <th>Credits</th>
            <td>$sum[crDbt]</td>
            <td><input type='submit' name='reconList' value='Reconcile Credits'></td>
        </tr><tr>
            <th>EBT</th>
            <td>$sum[ebt]</td>
            <td><input type='submit' name='reconList' value='Reconcile EBT'></td>
        </tr>
    </table>
    </form>
    
FORM;
    return $f;
    
    } //end function form

//////////////////////////////////////////////////////////////////////

} //end of class trans

?>
