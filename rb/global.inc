<?php
// Set the values to your parameters for Remote Base
// This file is included at the top of index.php
// ONLY change text between quotes
//
// Your callsign Only:
$CALL = "WX5FWD";
//
// Your Allstar node number:
$NODE = "473546";
//
// Audio archive
$ARCHIVE_URL="/archive/$NODE/";
//
// Your location:
$LOCATION = "Roof NWS";
//
// Grid Square
$GRID = "EM12iu";
//
//Supermon URL
$SMURL="https://$NODE.wx5fwd.org/supermon/link.php?nodes=$NODE";
//
$HEADING = "$LOCATION Remote Base - $CALL";
//
// Second line header title:
$TITLE = "Allstar Node <a href='$SMURL' target='_blank' title='Node Info'>$NODE</a> $GRID";
//
// Third line header title:
$TITLE2 = "15ft Roof Antenna";
//
// Background image - specify path if not /var/www/html/rb
// Leaving BACKGROUND null "" results in BACKGROUND_COLOR:
//$BACKGROUND = "background.jpg";
$BACKGROUND = "";
//
// Background color if no image:
//$BACKGROUND_COLOR = "green";
$BACKGROUND_COLOR = "#0000ff";
//
// Height of background - matches image height:
$BACKGROUND_HEIGHT = "124px";
//
//
?>
