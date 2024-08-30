<?php
//	Some modifications. KB4FXC 02/2018
//	Modifications for asl3. WD5M 08/2024
include("session.inc");
include("common.inc");

if ($_SESSION['sm61loggedin'] !== true) {
    die ("<br><h3>ERROR: You Must login to use the 'Restrict' function!</h3>");
}
?>

<html>
<head>
<link type="text/css" rel="stylesheet" href="supermon.css">
</head>
<body style="background-color: powderblue;">

<?php
// Read parameters passed to us
$thisNode = @trim(strip_tags($_GET['nodes']));
if ($thisNode == "") {
    die ("Please provide a properly formated URI. (ie node-ban-allow.php?nodes=1234)");
}
?>
<p style="text-align:center;font-size: 1.5em;"><b>Allow/Restrict AllStar Nodes for <?php print $thisNode;?></b></p>
<?php
//$blist=`$GREP -oP '^\s*context\s*=\s*blacklist' /etc/asterisk/iax.conf`;
//$wlist=`$GREP -oP '^\s*context\s*=\s*whitelist' /etc/asterisk/iax.conf`;
$blist=`$SUDO $ASTERISK -rx "database showkey denylist/$thisNode/%"|$GREP -v ^0\ results`;
$wlist=`$SUDO $ASTERISK -rx "database showkey allowlist/$thisNode/%"|$GREP -v ^0\ results`;
print "<center><p><b>System currently setup to only use - ";
if ( $blist != "" ) {
   print "DENYLIST";
} elseif ( $wlist != "" ) {
   print "ALLOWLIST";
} else {
   print "NONE DEFINED";
}
print "</b></p></center>";
?>

<?php
if ( (isset($_GET["whiteblack"])) && ($_GET["whiteblack"] != "" )) {
  $whiteblack=$_GET["whiteblack"];
  $node=$_GET["node"];
  $comment=$_GET["comment"];
  $deleteadd=$_GET["deleteadd"];

if ( $whiteblack == "whitelist" ) {
    $DBname = "allowlist/$thisNode";
 } else {
    $DBname= "denylist/$thisNode";
}

if ( $deleteadd == "add" ) {
    $cmd = "put";
    $ret=`$SUDO $ASTERISK -rx "database $cmd $DBname $node \"$comment\""`;
 } else {
    $cmd = "del";
    $ret=`$SUDO $ASTERISK -rx "database $cmd $DBname $node"`;
}

}
?>

<center>
<form action="node-ban-allow.php" method="get">
<input type="hidden" name="nodes" value="<?php print $thisNode;?>">
<table cellspacing="20">
<tr>
<td align="top">
<?php
if ( $whiteblack == "whitelist" ) {
?>
 <input type="radio" class="submit" name="whiteblack" value="whitelist" checked> Allowed - allowlist<br>
<?php }else{ ?>
 <input type="radio" class="submit" name="whiteblack" value="blacklist" checked> Restricted - denylist<br>
<?php } ?>
</td></tr>
<tr><td>
Enter Node number -  
 <input type="text" name="node" maxlength="7" size="5">
</td></tr>
<td>
Enter comment -
 <input type="text" name="comment" maxlength="30" size="22">
</td></tr>
<tr>
<td>
 <input type="radio" class="submit" name="deleteadd" value="add" checked> Add<br>
 <input type="radio" class="submit" name="deleteadd" value="delete"> Delete<br>
</td>
</tr>
<tr>
<td>Current Nodes in the Restricted - denylist:
<?php
$node=$_GET["node"];
$data=`$SUDO $ASTERISK -rx "database showkey denylist/$thisNode/%"`;
if ( $data == "" ) {
   print "<p>---NONE---</p>";
} else {
   print "<pre>$data</pre>";
} 
?>
</td></tr>
<p>
<center>
<input type="submit" class="submit" value="Update">
 &nbsp;
<input type="button" class="submit" Value="Close Window" onclick="self.close()">
</center>
</p>
<tr>
<td>Current Nodes in the Allowed - allowlist:
<?php
$data=`$SUDO $ASTERISK -rx "database showkey allowlist/$thisNode/%"`; 
if ( $data == "" ) {
    print "<p>---NONE---</p>";
} else {
    print "<pre>$data</pre>";
}
//print "database $cmd $DBname $node \"$comment\"";
//print $ret;

?>
</td></tr>
</table
</center>
</form>
<form action="node-ban-allow-intro.php" method="get">
<input type="submit" class="submit" value="Help">
<br> &nbsp; <br>
</form>

</body>
</html>

