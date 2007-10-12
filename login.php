<?php function loginForm() { ?>

<div id='content' >

<h2>Please login to the database</h2>

<form method='POST'
      action='home.php'
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
        <td colspan='2' style='text-align: right;';>
            <input name='Submit' type='image' value='Login' src='images/Login.png'/>
        </td>
    </tr>
    </table>

</form>
</div>

<?php } ?>
