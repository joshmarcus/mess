<?php

///////////////////////////////////////////////////////////////////////

function htmlHead($w='Database') {
$h =<<<EOD
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
    "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">

    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
    <head>
        <meta name="generator" content="Bluefish 1.0.7"/>
        <meta name="author" content="digger vermont"/>
        <link href="mariposa.css"
            type="text/css" rel="Stylesheet" media="screen" />

    <title>Mariposa Database: $w</title>

    </head>

    <body>
EOD;

    return $h;
} // End function htmlHead

///////////////////////////////////////////////////////////////////////

function htmlTail() {
    $h =<<<EOD
    </body>
    </html>
EOD;

    return $h;
}

///////////////////////////////////////////////////////////////////////

function htmlTitle($w=' Database') {
    
    $h =<<<EOD
    <div id='logo'>Mariposa: $w</div>
    <div id='headerLine'></div>
EOD;
    return $h;
}

///////////////////////////////////////////////////////////////////////

?>
