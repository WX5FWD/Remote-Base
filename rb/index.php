<!DOCTYPE html>
<?php
	// from Supermon
	include("global.inc");
	$node = $NODE;
	$title = 'Node '.$node.' '.$HEADING.' <a href="/supermon/connectlog.php" target="blank" title="Allstar connect log"><img src="log.webp" style="height:1rem;"/></a> <a href="/supermon/edit/webacclog.php" target="blank" title="Apache web log"><img src="log.webp" style="height:1rem;"/></a> ';
if (isset($_COOKIE['display-data'])) {
    foreach ($_COOKIE['display-data'] as $name => $value) {
        $name = htmlspecialchars($name);
        switch ($name) {
            case "number-displayed";
               $Displayed_Nodes = htmlspecialchars($value);
               break;
            case "show-number";
               $Display_Count = htmlspecialchars($value);
               break;
            case "show-all";
               $Show_All = htmlspecialchars($value);
               break;
        }
       // echo "$name : $value <br />\n";
    }
}

// If not defined in cookie display all nodes
if (! isset($Displayed_Nodes)) {
    $Displayed_Nodes="999";
} elseif
    ($Displayed_Nodes === "0") {
         $Displayed_Nodes="999";
}

// If not define in cookie display all
if (! isset($Display_Count)) {
  $Display_Count=0;
}

// If not defined in cookie show all else omit "Never" Keyed
if ( ! isset($Show_All)) {
  $Show_All="1";
}

        #
        # index.php -   The entry file for the Remote Base control web page.
        #               https://hub.wx5fwd.org/rb/
        #               D. McAnally WD5M
        #
        # Load CTCSS tones and DCS code arrays for web form
        include("codes.inc");
        # load the channel records into an array of channel selections.
        $filename = '/var/www/html/rb/rbchannels.csv';  # file containing channel numbers/descriptions
        $csv = file_get_contents($filename,false);
        $channels = explode("\n", $csv);
        $csv = null;
        $filename = null;
        # create a javascript array of channel numbers.
        print("<script type=\"application/javascript\">\nconst channelsindex = [");
        foreach ($channels as $channel)
        {
                $channel = trim($channel);
                if ($channel) {
                        $f = explode(',', $channel);
                        print("\"" . $f[0] . "\",");
                }
        }
        print("];\n</script>\n");
?>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en-US" xml:lang="en-US">
        <body onfocus="transparentMouseOver();" onblur="transparentMouseOut();" onmouseover="transparentMouseOver();" onmouseout="transparentMouseOut();" onmousemove="transparentMouseOver();">
                <head>
                <title><?php print("$HEADING");?></title>
                        <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
                        <meta name="viewport" content="width=device-width, initial-scale=0.65" />
                        <meta name="description" content="Remote Base Radio Manager">
                        <meta name="keywords" content="remote base,allstar, app_rpt, asterisk">
                        <meta name="robots" content="noindex, nofollow">
                        <meta name="author" content="David McAnally, WD5M">
                        <link rel="icon" href="favicon.ico" type="image/x-icon">
                        <link type="text/css" rel="stylesheet" href="rb.css">
			<style data="specialcss" type="text/css"></style>
                        <script
                                src="https://code.jquery.com/jquery-3.6.0.min.js"
                                integrity="sha256-/xUj+3OJU5yExlq6GSYGSHk7tPXikynS7ogEvDej/m4="
                                crossorigin="anonymous">
                        </script>
                        <script
                                src="https://code.jquery.com/ui/1.12.1/jquery-ui.min.js"
                                integrity="sha256-VazP97ZCwtekAsvgPBSUwPFKdrwD3unUfSGVYrahUqU="
                                crossorigin="anonymous">
			</script>

                        <script src="codes.js"></script>
                        <script src="rb.js"></script>
<script type="text/javascript">
// when DOM is ready

$(document).ready(function() {
  myTitle = document.title;
  if(typeof(EventSource)!=="undefined") {

    // Start SSE
    var source=new EventSource("/supermon/server.php?nodes=<?php echo $node; ?>");

    // Fires when node data come in. Updates the whole table
    source.addEventListener('nodes', function(event) {
    //console.log('nodes: ' + event.data);
    // server.php returns a json formated string

    var tabledata = JSON.parse(event.data);
    for (var localNode in tabledata) {
        var tablehtml = '';

        var total_nodes = 0;
        var shown_nodes = 0;
        var ndisp = <?php echo (int) $Displayed_Nodes ?>;
        ndisp++;
        var sdisp = <?php echo $Display_Count ?>;
        var sall = <?php echo $Show_All ?>;

        // KN2R -- refactoring - Added Idle, COS, PTT, and Full Duplex indicators 6/11/2018

        var cos_keyed = 0;
        var tx_keyed = 0;

        for (row in tabledata[localNode].remote_nodes) {

               if (tabledata[localNode].remote_nodes[row].cos_keyed == 1)
                        cos_keyed = 1;

                if (tabledata[localNode].remote_nodes[row].tx_keyed == 1)
                        tx_keyed = 1;

        }

        if (cos_keyed == 0) {
                if (tx_keyed == 0) {
			document.title = myTitle;
                        tablehtml += '<tr class="gColor"><td colspan="1" align="center">' + localNode + '</td><td colspan="1" align="center">Idle</td><td colspan="5"></td></tr>';
		}
                else {
			document.title = 'PTT-Keyed ' + myTitle;
			tablehtml += '<tr class="tColor"><td colspan="1" align="center">' + localNode + '</td><td colspan="1" align="center">PTT-Keyed</td><td colspan="5"></td></tr>';
		}
        }
        else {
                if (tx_keyed == 0) {
			document.title = 'COS-Detected ' + myTitle;
                        tablehtml += '<tr class="lColor"><td colspan="1" align="center">' + localNode + '</td><td colspan="1" align="center">COS-Detected</td><td colspan="5"></td></tr>';
		}
                else {
			document.title = 'COS-Detected and PTT-Keyed ' + myTitle;
                        tablehtml += '<tr class="bColor"><td colspan="1" align="center">' + localNode + '</td><td colspan="2" align="center">COS-Detected and PTT-Keyed (Full-Duplex)</td><td colspan="4"></td></tr>';
		}
        }
        for (row in tabledata[localNode].remote_nodes) {

            if (tabledata[localNode].remote_nodes[row].info === "NO CONNECTION") {

               tablehtml += '<tr><td colspan="7"> &nbsp; &nbsp; No Connections.</td></tr>';

            } else {

               nodeNum=tabledata[localNode].remote_nodes[row].node;
               if (nodeNum != 1) {

               // ADDED WA3DSP
               // Increment total and display only requested
               total_nodes++
               if (row<ndisp) {
                  if (sall == "1" || tabledata[localNode].remote_nodes[row].last_keyed != "Never" || total_nodes < 2) {
                     shown_nodes++;
               // END WA3DSP

                     // Set blue, red, yellow, whatever, or no background color
                     if (tabledata[localNode].remote_nodes[row].keyed == 'yes') {
                        tablehtml += '<tr class="rColor">';
                     } else if (tabledata[localNode].remote_nodes[row].mode == 'C') {
                        tablehtml += '<tr class="cColor">';
                     } else {
                        tablehtml += '<tr>';
                     }

                     var id = 't' + localNode + 'c0' + 'r' + row;
                     //console.log(id);
                     tablehtml += '<td id="' + id + '" align="center" class="nodeNum">' + tabledata[localNode].remote_nodes[row].node + '</td>';

                     // Show info or IP if no info
                     if (tabledata[localNode].remote_nodes[row].info != "") {
                        tablehtml += '<td>' + tabledata[localNode].remote_nodes[row].info + '</td>';
                     } else {
                        tablehtml += '<td>' + tabledata[localNode].remote_nodes[row].ip + '</td>';
                     }
                     tablehtml += '<td align="center" id="lkey' + row + '">' + tabledata[localNode].remote_nodes[row].last_keyed + '</td>';
                     tablehtml += '<td align="center">' + tabledata[localNode].remote_nodes[row].link + '</td>';
                     tablehtml += '<td align="center">' + tabledata[localNode].remote_nodes[row].direction + '</td>';
                     tablehtml += '<td align="right" id="elap' + row +'">' + tabledata[localNode].remote_nodes[row].elapsed + '</td>';

                     // Show mode in plain english
                     if (tabledata[localNode].remote_nodes[row].mode == 'R') {
                        tablehtml += '<td align="center">Receive Only</td>';
                     } else if (tabledata[localNode].remote_nodes[row].mode == 'T') {
                        tablehtml += '<td align="center">Transceive</td>';
                     } else if (tabledata[localNode].remote_nodes[row].mode == 'C') {
                        tablehtml += '<td align="center">Connecting</td>';
                     } else {
                        tablehtml += '<td align="center">' + tabledata[localNode].remote_nodes[row].mode + '</td>';
                     }
                     tablehtml += '</tr>';
                  }
                  //console.log('tablehtml: ' + tablehtml);

                 }
               }
            }
         }

      // ADDED WA3DSP
      // Display Count
         if (sdisp === 1 && total_nodes >= shown_nodes && total_nodes > 1) {
            if (shown_nodes == total_nodes) {
               tablehtml += '<td colspan="2"> &nbsp; &nbsp;' + total_nodes + ' nodes connected.</td></tr>';
            } else {
               tablehtml += '<td colspan="2"> &nbsp; &nbsp;' + shown_nodes + ' shown of ' + total_nodes + ' nodes connected.</td></tr>';
            }
         }
      // END WA3DSP

      $('#table_' + localNode + ' tbody:first').html(tablehtml);
    }
});


        // Fires when new time data comes in. Updates only time columns
        source.addEventListener('nodetimes', function(event) {
                        //console.log('nodetimes: ' + event.data);
                        var tabledata = JSON.parse(event.data);
                        for (localNode in tabledata) {
                                tableID = 'table_' + localNode;
                                for (row in tabledata[localNode].remote_nodes) {
                                        //console.log(tableID, row, tabledata[localNode].remote_nodes[row].elapsed, tabledata[localNode].remote_nodes[row].last_keyed);

                                        rowID='lkey' + row;
                                        $( '#' + tableID + ' #' + rowID).text( tabledata[localNode].remote_nodes[row].last_keyed );
                                        rowID='elap' + row;
                                        $( '#' + tableID + ' #' + rowID).text( tabledata[localNode].remote_nodes[row].elapsed );

                                }
                        }


        });

        // Fires when connection message comes in.
        source.addEventListener('connection', function(event) {
                        //console.log(statusdata.status);
                        var statusdata = JSON.parse(event.data);
                        tableID = 'table_' + statusdata.node;
                        $('#' + tableID + ' tbody:first').html('<tr><td colspan="7">' + statusdata.status + '</td></tr>');
                });

    } else {
        $("#list_link").html("Sorry, your browser does not support server-sent events...");
    }
});
</script>
                </head>
                <header>
                        <div id="rbmenuinfo">
                        	<?php include "rbmenu.inc" ?>
                        </div>
                        <h1><?php print("$HEADING");?></h1>
<!--
                        <div id="imgwx5fwd">
                                <img src="Skywarn.svg" loading="lazy" height="59px" alt="SKYWARN" onClick="window.open('https://wx5fwd.org','_blank');" title="WX5FWD.org">
                        </div>
                        <div id="imgnws">
                                <img loading="lazy" src="US-NationalWeatherService-Logo.svg" height="59" alt="NWS" onClick="window.open('https://weather.gov/fwd','_blank');" title="WEATHER.gov/fwd">
                        </div>
-->
                        <h2><?php print("$TITLE");?></h2>
                </header>
                <nav aria-label="Main Navigation">
                        <div id="content" onfocus="contentMouseOver();" onblur="contentMouseOut();" onfocusin="contentMouseOver();" onfocusout="contentMouseOut();" onmouseout="contentMouseOut();" onmouseover="contentMouseOver();">
                        <div id="channels">
                                <button class="submit" id="dw" value="--dw" title="Channel Down">&#8595;</button>
                                <select id="channelsel" class="submit" name="--memory" title="Select a Radio Channel Memory">
                                        <!--<option value="">Select Channel</option>-->
                                        <?php
                                                # list the channels for selection from the array.
                                                foreach ($channels as $channel)
                                                {
                                                        $channel = trim($channel);
                                                        if ($channel) {
                                                                $f = explode(',', $channel);
                                                                print("<option value=\"" . $f[0] . ' ' . $f[3] . "\">" . $f[1] . " " . $f[2] . " (" . $f[0] . ")" . "</option>\n");
                                                        }
                                                }
                                        ?>
                                </select>
                                <button class="submit" id="up" value="--up" title="Channel Up">&#8593;</button>
                                <button class="submit" id="proximitybutton" title="Repeater Book Proximity Search"><a class="submit" id="proximityanchor" href="" target="_proximity">Proximity</a></button>
                        </div>
                        <div id="vfodiv">
                                <input id="frequency" class="submit" type="number" step="any" size="10" name="--frequency" title="Enter desired frequency" />
                                <select id="shift" class="submit" name="--shift" title="Set transmit offset shift. Simplex, Positive(+) or Negative(-). Leave unset to automatically set per Texas bandplan.">
                                        <option value="">Shift</option>
                                        <option value="s">(S)</option>
                                        <option value="p">(+)</option>
                                        <option value="n">(-)</option>
                                </select>
                                <select id="tone" class="submit" name="--tone" title="Select CTCSS Transmit Tone. Leave unselected to disable TX Tone.">
                                        <option value="">No Tone</option>
                                        <?php
                                                # list the pl tones for selection from the array.
                                                foreach ($plindex as $pl)
                                                {
                                                        echo "<option value=\"{$pl}\">{$pl}</option>\n";
                                                }
                                        ?>
                                </select>
                                <input class="submit" id="ctcss" name="--ctcss" type="checkbox" title="Enable CTCSS on receiver." /><label class="submit" for="ctcss" title="Enable CTCSS on receiver.">CTCSS</label>
<!--
                                <select id="ctcsstone" class="submit" name="--ctcsstone" title="Select CTCSS Receiver Squelch Tone if different from Transmit Tone and CTCSS is enabled. If CTCSS is enabled and this is left unselected or CSQ, the selected TX Tone is copied.">
                                        <option value="">CSQ</option>
                                        <?php
                                                # list the pl tones for selection from the array.
                                                foreach ($plindex as $pl)
                                                {
                                                        echo "<option value=\"{$pl}\">{$pl}</option>\n";
                                                }
                                        ?>
                                </select>
-->
                                <select id="dcs" class="submit" name="--dcs" title="Select Digital Code Sqlulch. Leave unselected to disable.">
                                        <option value="">DCS</option>
                                        <?php
                                                # list the dcs codes for selection from the array.
                                                foreach ($dcsindex as $dcs)
                                                {
                                                        echo "<option value=\"{$dcs}\">{$dcs}</option>\n";
                                                }
                                        ?>
                                </select>
                                <select id="mode" class="submit" name="--mode" title="Modulation mode, FM (default), NFM or AM.">
                                        <option value="">Mode</option>
                                        <option value="FM">FM</option>
                                        <option value="NFM">NFM</option>
                                        <option value="AM">AM</option>
                                </select>
                                <input class="submit" id="repeaterinput" name="--input" type="checkbox" type="hidden" title="Set receiver to repeater input frequency" /><label title="Set receiver to repeater input frequency" class="submit" for="repeaterinput">Input</label>
                                <button class="submit" id="vfosubmit" name="vfosubmit">Submit</button>
<!--
                                <button class="submit" id="resetvfo" name="resetvfo" onclick="myResetVFO()">Reset</button>
-->
                        </div>
                        <div id="controls">
                                <div id="sqcontrols">
                                <button class="submit" id="squelchDW" value="--squelch n" title="Squelch Down"><b>&#8595;</b></button><label class="submit" for="squelchsel" title="Squelch Level" id="squelchlabel">SQ <span id="sqlevel"></span><input type="range" min="0" max="31" step="1" value="8" class="submit slider" id="squelchsel" name="--squelch" title="Set Radio Squelch Level" /><span id="smlevel"></span></label><button class="submit" id="squelchUP" value="--squelch p" title="Squelch Up">&#8593;</button>
                                </div>
                                <select id="powersel" class="submit" name="--power" title="Select a Radio Power Level">
                                        <option value="e">5 Watts</option>
                                        <option value="l">10 Watts</option>
                                        <option value="h">50 Watts</option>
                                </select>
<!--
                                <?php if (isset($_SERVER['PHP_AUTH_USER']) && strtolower($_SERVER['PHP_AUTH_USER'])=='wd5m') { ?>
                                	<button class="submit" id="ptt" value="--tx" title="Click or touch and hold to enable radio PTT">PTT</button>
                                	<button class="submit" id="fastrestart" value="--aslres" title="Perform a fast restart of Asterisk on the remote base system.">ASLRES</button>
				<?php } ?>
				<button class="submit" id="fastrestart" value="--nodelistres" title="Restart node list process to update recent node registrations.">Restart Nodelist</button>
-->
				<table class=gridtable id="table_<?php echo $NODE ?>">
					<colgroup>
						<col span="1">
						<col span="1">
						<col span="1">
						<col span="1">
						<col span="1">
						<col span="1">
						<col span="1">
					</colgroup>
					<thead>
						<tr><th colspan="7"><i><?php echo $title; ?></i></th></tr>
						<tr><th>&nbsp;&nbsp;Node&nbsp;&nbsp;</th><th>Node Information</th><th>Received</th><th>Link</th><th>Direction</th><th>Connected</th><th>Mode</th></tr>
					</thead>
					<tbody>
						<tr><td colspan="7"> &nbsp; Waiting...</td></tr>
					</tbody>
				</table>
			</div>
                        <h2>
                                <span style="font-size:smaller;">
                                        <?php print("$TITLE2");?>
                                </span>
                        </h2>
                </nav>
                <footer>
                        <div id="timetick">&nbsp;</div>
                        <div id="spinny">&nbsp;</div>
                        <div id="author">
                                WX5FWD&#174; SKYWARN Team
                                <?php
                                                if (isset($_SERVER['PHP_AUTH_USER']) && !empty($_SERVER['PHP_AUTH_USER'])) {
                                                        print(" [".$_SERVER['PHP_AUTH_USER']."]");
                                                } else {
                                                        print(" [Unauthorized]");
                                                }
                                ?>
                        </div>
		</footer>
        </body>
</html>
