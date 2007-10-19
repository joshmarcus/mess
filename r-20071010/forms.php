<?php

$actionPhpSelf = <<<EOD
{$_SERVER['PHP_SELF']}
EOD;

function loginForm() {
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
//  Login Form

$actionPhpSelf = <<<EOD
{$_SERVER['PHP_SELF']}
EOD;

$form = <<<EOD

<div id='login'>

<h2>Please login to the database</h2>

<form method='POST'
      action={$actionPhpSelf}
      name='login'
      >
    <input type='hidden' name='db' value='mariposa' />
    <input type='hidden' name='server' value='localhost' />
    
    <table>
    <tr>
        <th>User Name:</th>
        <td><input type='text' name='user'></td>
    </tr>
    <tr>
        <th>Password:</th>
        <td><input type='password' name='pass'></td>
    <tr>
        <td colspan='2'>
            <input name='Clear' type='reset' />
            <input name='Submit' type='submit' value='Login' />
        </td>
    </tr>
    </table>

</form>
</div>

EOD;

return $form;

}

///////////////////////////////////////////////////////////////////////

?>
