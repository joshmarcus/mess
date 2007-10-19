<?php

class transTable
{
    
    private $login;
    private $link;

    private $fName;
    private $aName;
    private $tName;
    
    function __construct($login) {
        $this->login = $login;
        $this->link = new MyDB($login);
    }

/////////////////////////////////////////////////////////////////////

    function table() {
    
        $today = date("l, F j, Y \a\\t g:i a");

        $q =<<<QUERY
                SELECT  T.modDate AS tDate,
                        DATE(T.modDate) AS mDate,
                        TIME(T.modDate) AS tTime,
                        CONCAT_WS(' ', given, middle, family) AS fName,
                        T.xID,
                        A.aID, M.mID,
                        A.name AS aName,
                        T.type, T.amt, T.note, T.ref
                FROM
                        trans T, acct A, mem M
                WHERE
                        (DATE(T.modDate) = CURDATE())
                AND     (T.aID = A.aID)
                AND     (T.mID = M.mID)
                ORDER BY
                        T.modDate DESC
QUERY;

        print <<<EOD
            <div id="trans">
            <h2>Transactions for Today, $today
            
            </h2>
            <table>
                <th>Time</th>
                <th>Transaction<br />Number</th>
                <th>Reference</th>
                <th>Account</th>
                <th>Who</th>
                <th>Note</th>
                <th>Type</th>
                <th>Amount</th>
                <th>Account<br />Balance</th>
EOD;

        $this->link->createResult($q);
        
        while ($r = $this->link->getRow()){
            
            $this->tName = transTypeName($r[type]);
            
            $account = new account($this->login);
            $bal = $account->getAcctBal($r[aID], $r[tDate]);

        print <<<EOD
            <tr>
            <td>$r[tTime]</td>
            <td>$r[xID]</td>
            <td>$r[ref]</td>
            <td><a href='viewAcct.php?id=$r[aID]' >$r[aName]</a></td>
            <td><a href='viewMem.php?id=$r[mID]' >$r[fName]</a></td>
            <td>$r[note]</td>
            <td>$this->tName</td>
            <td>$r[amt]</td>
            <td>$bal</td>
            </tr>
EOD;
    }
        $this->link->closeResult();

        //$link->close();

    print <<<EOD
        </table>
        </div>
EOD;

    } //end function table

/////////////////////////////////////////////////////////////////////

 function acctTrans($aID) {
        
        $account = new account($this->login);
        $name = $account->getName($aID);
        
        $q =<<<QUERY
            SELECT  T.xID,
                    T.modDate AS mTime,
                    TIME(T.modDate) AS tTime,
                    DATE(T.modDate) AS tDate,
                    CONCAT_WS(' ', M.given, M.middle, M.family )
                    AS fName,
                    T.amt, T.type, T.note, T.ref, 
                    A.name, M.mID 
            FROM    trans T, acct A, mem M
            WHERE   (A.aID = $aID)
            AND     (T.aID = $aID)
            AND     (T.mID = M.mID)
            ORDER BY T.modDate DESC
            LIMIT 0, 10;
QUERY;

        $this->link->createResult($q);

        print <<<TABLE
            <div id="trans">
            <h2>Latest Transactions for $name </h2>
            <table>
                <th>Date</th>
                <th>Time</th>
                <th>Transaction<br />Number</th>
                <th>Reference</th>
                <th>Who</th>
                <th>Note</th>
                <th>Type</th>
                <th>Amount</th>
                <th>Balance</th>
TABLE;

        while ($r = $this->link->getRow()){
            
            $tName = transTypeName($r['type']);
            
            $bal = $account->getAcctBal($aID, $r['mTime']);
           
            print <<<ROW
                <tr>
                <td>$r[tDate]</td>
                <td>$r[tTime]</td>
                <td>$r[tID]</td>
                <td>$r[ref]</td>
                <td><a href='viewMem.php?id=$r[mID]' >$r[fName]</a></td>
                <td>$r[note]</td>
                <td>$tName</td>
                <td>$r[amt]</td>
                <td>$bal</td>
                </tr>
ROW;
        }

        print <<<TABLE
            </table>
            </div>
TABLE;

        $this->link->closeResult();
   
    }  //end of function acctTrans

////////////////////////////////////////////////////////////////////


function dailySummary() {
    $q =<<<EOD
        SELECT
            SUM(IF(type<=>'s',amt,0)) AS purchases,
            SUM(IF(type<=>'b',amt,0)) AS bulk,
            SUM(IF(type<=>'e',amt,0)) AS extras,
            SUM(IF(type<=>'m',amt,0)) AS dues,
            SUM(IF(type<=>'n',amt,0)) AS memDep,
            SUM(IF(type<=>'k',amt,0)) AS keyDep,
            SUM(IF(type<=>'d',amt,0)) AS debit,
            SUM(IF(type<=>'c',amt,0)) AS credit,
            SUM(IF(type<=>'g',amt,0)) AS checks,
            SUM(IF(type<=>'a',amt,0)) AS mo,
            SUM(IF(type<=>'f',amt,0)) AS ebt,
            SUM(IF(type<=>'r',amt,0)) AS credits,
            SUM(IF(type<=>'w',amt,0)) AS workCredit,
            SUM(IF(type<=>'o',amt,0)) AS misc,
            
            SUM(IF(type<=>'s',amt,0))
            + SUM(IF(type<=>'b',amt,0))
            + SUM(IF(type<=>'e',amt,0))
            + SUM(IF(type<=>'m',amt,0))
            - SUM(IF(type<=>'n',amt,0))
            - SUM(IF(type<=>'k',amt,0))
            - SUM(IF(type<=>'d',amt,0))
            - SUM(IF(type<=>'c',amt,0))
            - SUM(IF(type<=>'g',amt,0))
            - SUM(IF(type<=>'a',amt,0))
            - SUM(IF(type<=>'f',amt,0))
            - SUM(IF(type<=>'r',amt,0))
            - SUM(IF(type<=>'w',amt,0))
            - SUM(IF(type<=>'o',amt,0)) AS total,

            SUM(IF(type<=>'s',amt,0))
            + SUM(IF(type<=>'b',amt,0))
            + SUM(IF(type<=>'e',amt,0))
            + SUM(IF(type<=>'m',amt,0)) AS sales,
            
            SUM(IF(type<=>'d',amt,0))
            + SUM(IF(type<=>'c',amt,0))
            + SUM(IF(type<=>'g',amt,0))
            + SUM(IF(type<=>'a',amt,0))
            + SUM(IF(type<=>'f',amt,0))
            + SUM(IF(type<=>'r',amt,0))
            + SUM(IF(type<=>'w',amt,0))
            + SUM(IF(type<=>'o',amt,0)) AS payments,
            
            SUM(IF(type<=>'n',amt,0))
            + SUM(IF(type<=>'k',amt,0)) AS deposits,
            
            SUM(IF(type<=>'d',amt,0))
            + SUM(IF(type<=>'c',amt,0)) AS crDbt,
            
            SUM(IF(type<=>'g',amt,0))
            + SUM(IF(type<=>'a',amt,0)) AS ckMo
        
        FROM    trans
        WHERE   (DATE(modDate) = DATE(NOW()))
        GROUP BY date
EOD;

    $this->link->createResult($q);
    $arr = $this->link->getRow();
    $this->link->closeResult();
    
    return $arr;
    
} // End function dailySummary

////////////////////////////////////////////////////////////////////

} //end class transTable

?>
