<?php

class MyDB{
    //data members

    private $link;
    private $result;
    static $instances = 0;
  
    function __construct($login){

        if(MyDB::$instances == 0){
            
            $this->link = new mysqli(   $login[server],
                                        $login[user],
                                        $login[pass],
                                        $login[db]
                                        );

            if (mysqli_connect_errno()) {
                printf("Can't connect to MySQL Server.
                        Errorcode: %s\n", mysqli_connect_error());
                exit;
                } 
            MyDB::$instances = 0;
            } else {
                $msg = "Close the existing instance of the ".
                        "MySQLConnect class.";
            die($msg);
        }
    }

    function __destruct(){
        $this->close();
    }
    
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
// methods
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    function createResult($q) {
        $this->result = $this->link->query($q)
            or die("query:</br></br> $q;</br></br> failed at createResult!</br>");
        return $this->result;
    }

    function getRow() {
        return $this->result->fetch_assoc();
    }

    function getNumRows() {
        return $this->result->num_rows;
    }
    
    function getVersionNumber(){
        //mysql_get_server_info
        return $this->link->server_version;
    }

    function insertQuery($q) {
        $this->link->query($q)
            or die ("query failed at insertQuery!");
    }
    
    function closeResult() {
        if(isset($this->result)) {
            $this->result->close();
            unset ($this->result);
        }
    }
         
    function close(){
        MyDB::$instances = 0;
        if(isset($this->link)){
            $this->link->close();
            unset($this->link);
            }
    }
  
}//end class
////////////////////////////////////////////////////////////////////
?>
