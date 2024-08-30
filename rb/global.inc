<?php
// Set the values to your parameters for Remote Base
// This file is included at the top of index.php
// ONLY change text between quotes
//
// Your callsign Only:
$CALL = "?????";
//
// Your Allstar node number:
$NODE = "12345";
//
// Audio archive
$ARCHIVE_URL="/archive/$NODE/";
//
// Your location:
$LOCATION = "NWS";
//
// Grid Square
$GRID = "EM12iu";
//
//Supermon URL
$SMURL="https://$NODE.somewhere.org/supermon/link.php?nodes=$NODE";
//
$HEADING = "$LOCATION Remote Base - $CALL";
//
// Second line header title:
$TITLE = "Allstar Node <a href='$SMURL' target='_blank' title='Node Info'>$NODE</a> $GRID";
//
// Third line header title:
$TITLE2 = "Roof Antenna";
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
