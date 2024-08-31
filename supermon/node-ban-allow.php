<?php
//      Some modifications. KB4FXC 02/2018
//      Modifications for asl3. WD5M 08/2024
include("session.inc");
include("common.inc");

if ($_SESSION['sm61loggedin'] !== true) {
    die ("<br><h3>ERROR: You Must login to use the 'Restrict' function!</h3>");
}
$asl3=false;
$aslver=`$SUDO $ASTERISK -V`;
if (strpos($aslver,"asl3") > 0) {
        $asl3=true;
}
?>

<html>
<head>
<link type="text/css" rel="stylesheet" href="supermon.css">
</head>
<body style="background-color: powderblue;">

<?php
if ($asl3){
        // Read parameters passed to us
        $thisNode = @trim(strip_tags($_GET['nodes']));
        if ($thisNode == "") {
        die ("Please provide a properly formated URI. (ie node-ban-allow.php?nodes=1234)");
        }
        print "<p style=\"text-align:center;font-size: 1.5em;\"><b>Allow/Restrict AllStar Nodes for $thisNode</b></p>";
        $blist=`$SUDO $ASTERISK -rx "database showkey denylist/$thisNode/%"|$GREP -v ^0\ results`;
        $wlist=`$SUDO $ASTERISK -rx "database showkey allowlist/$thisNode/%"|$GREP -v ^0\ results`;
}else{
        print "<p style=\"text-align:center;font-size: 1.5em;\"><b>Allow/Restrict AllStar Nodes</b></p>";
        $blist=`$GREP -oP '^\s*context\s*=\s*blacklist' /etc/asterisk/iax.conf`;
        $wlist=`$GREP -oP '^\s*context\s*=\s*whitelist' /etc/asterisk/iax.conf`;
}
print "<center><p><b>System currently setup to only use - ";
if ( $blist != "" ) {
        if ($asl3){
                print "DENYLIST";
        }else{
                print "BLACKLIST";
        }
} elseif ( $wlist != "" ) {
        if ($asl3){
                print "ALLOWLIST";
        }else{
                print "WHITELIST";
        }
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
        if ($asl3){
                $DBname = "allowlist/$thisNode";
        }else{
                $DBname = "whitelist";
        }
 } else {
        if ($asl3){
                $DBname= "denylist/$thisNode";
        }else{
                $DBname= "blacklist";
        }
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
<?php if ($asl3) { ?>
        <input type="hidden" name="nodes" value="<?php print $thisNode;?>">
<?php } ?>
<table cellspacing="20">
<tr>
<td align="top">
<?php
if ($asl3){
        if ( $whiteblack == "whitelist" || $blist == "" ) {?>
                <input type="radio" class="submit" name="whiteblack" value="blacklist"> Restricted - denylist<br>
                <input type="radio" class="submit" name="whiteblack" value="whitelist" checked> Allowed - allowlist<br>
        <?php }else{ ?>
                <input type="radio" class="submit" name="whiteblack" value="blacklist" checked> Restricted - denylist<br>
                <input type="radio" class="submit" name="whiteblack" value="whitelist"> Allowed - allowlist<br>
        <?php } ?>
<?php }else{
        if ( $whiteblack == "whitelist" || $blist == "" ) {?>
                <input type="radio" class="submit" name="whiteblack" value="blacklist"> Restricted - blacklist<br>
                <input type="radio" class="submit" name="whiteblack" value="whitelist" checked> Allowed - whitelist<br>
        <?php }else{ ?>
                <input type="radio" class="submit" name="whiteblack" value="blacklist" checked> Restricted - blacklist<br>
                <input type="radio" class="submit" name="whiteblack" value="whitelist"> Allowed - whitelist<br>
        <?php }
}
?>
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
<?php
if ($asl3) {
        print "<td>Current Nodes in the Restricted - denylist:";
        $node=$_GET["node"];
        $data=`$SUDO $ASTERISK -rx "database showkey denylist/$thisNode/%"`;
}else{
        print "<td>Current Nodes in the Restricted - blacklist:";
        $data=`$SUDO $ASTERISK -rx "database show blacklist"`;
}
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
<?php
if ($asl3) {
        print "<td>Current Nodes in the Allowed - allowlist:";
        $node=$_GET["node"];
        $data=`$SUDO $ASTERISK -rx "database showkey allowlist/$thisNode/%"`;
}else{
        print "<td>Current Nodes in the Allowed - whitelist:";
        $data=`$SUDO $ASTERISK -rx "database show whitelist"`;
}
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
