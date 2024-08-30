'use strict';

function JSDropDown(id) {
        var x = document.getElementById(id).options.length;
        document.getElementById(id).size = 10;
        document.getElementById(id).style.verticalAlign = "top";
}

function contentMouseOver() {
        contentfocused = true;
}

function contentMouseOut() {
        contentfocused = false;
}

function transparentMouseOver() {
        refreshtime = 1000;
        lastcommandtime = Date.now();
}

function transparentMouseOut() {
        refreshtime = 0;
}

function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
}

async function countdown(seconds,id,label) {
        // Sleep in loop
        var e = document.getElementById(id);
        e.setAttribute("disabled","disabled");
        for (let i = seconds; i > 0; i--) {
                $('#'+id).html('&nbsp;&nbsp;'+i+'&nbsp;&nbsp;');
                await sleep(1000);
        }
        $('#ptt').html("PTT");
        e.removeAttribute("disabled");
}

function myResetVFO() {
        var e = document.getElementById("tone");
        e.removeAttribute("style");
        e.selectedIndex = 0;
        var e = document.getElementById("ctcss");
        e.removeAttribute("style");
        e.checked = false;
        var e = document.getElementById("dcs");
        e.removeAttribute("style");
        e.selectedIndex = 0;
        var e = document.getElementById("shift");
        e.removeAttribute("style");
        e.selectedIndex = 0;
        var e = document.getElementById("mode");
        e.removeAttribute("style");
        e.selectedIndex = 0;
        var e = document.getElementById("repeaterinput");
        e.removeAttribute("style");
        e.checked = false;
}

// some global variables
let contentfocused = false;
var char = String.fromCharCode;
let sq = '';
let squelch = '';
let dcsstatus = 'None';
let tonestatus = 'None';
let ctcssstatus = 'None';
let channelselected = false;
let users = '';
let refreshtime = 1000; // refresh some content every 5 seconds.
let lastcommandtime = Date.now(); // last time a command was sent.
const refreshexpire = 3600000; // expire refresh if no commands in 60 minutes.
//const refreshexpire = 60000; // expire refresh if no commands in 1 minute.
const modeindex = ['FM','NFM','AM'];
const shiftindex = ['Simplex','Positive','Negative'];

// when DOM is ready
$(document).ready(function() {

        const options = { timeZone: "America/Chicago",
                hour12: false,
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: 'numeric',
                minute: 'numeric',
                second: 'numeric'
        };

        document.addEventListener("keyup", function(event) {
                if (event.keyCode === 13) {
                        enterKeyPressed(event.keyCode);
                }
        });

        function enterKeyPressed(event) {
                var command = '';
                lastcommandtime = Date.now();
                var e = document.getElementById("frequency");
                var name = e.name;
                var val = e.value;
                command = command + ' ' + name + ' ' + val;
                var e = document.getElementById("tone");
                var name = e.name;
                var val = e.options[e.selectedIndex].value;
                command = command + ' ' + name + ' ' + val;
                var e = document.getElementById("ctcss");
                var name = e.name;
                if (e.checked) {
                        command = command + ' ' + name;
                }
                var e = document.getElementById("dcs");
                var name = e.name;
                var val = e.options[e.selectedIndex].value;
                command = command + ' ' + name + ' ' + val;
                var e = document.getElementById("shift");
                var name = e.name;
                var val = e.options[e.selectedIndex].value;
                command = command + ' ' + name + ' ' + val;
                var e = document.getElementById("mode");
                var name = e.name;
                var val = e.options[e.selectedIndex].value;
                command = command + ' ' + name + ' ' + val;
                var form = 'vfo';
                $('#vfodiv').animate({opacity:".1"});
                $.ajax( { url:'v71cgi.py/?' + command, data: { 'command' : command, 'event' : form }, type:'post', success: function(result) {
                                var r = result.split('\n');
                                r.forEach(mySetAttributes);
                                let now = new Date();
                                $('#timetick').html(now.toLocaleString('en-US',options));
                                $('#vfodiv').animate({opacity:"1"});
                        }
                });
        }

        // a function to set page attributes based on radio setting results.
        function mySetAttributes(x,i) {
                if (x.trim() != '') {
                        var f = x.split(':');
                        if (f[0].trim(' \r\n') == 'Logged in') {
                                console.log(x);
                                users = x.trim(' \r\n');
                        }
                        if (f[0].trim(' \r\n') === 'Channel') {
                                var e = document.getElementById("channelsel");
                                let len = channelsindex.length;
                                for (let i = 0; i < len; i++) {
                                	if (channelsindex[i] == f[1].trim()) {
                                		channelselected = true;
                               			e.selectedIndex = i;
                                	}
                                }
                        }
                        if (f[0].trim(' \r\n') == 'RX Frequency') {
                                var e = document.getElementById("frequency");
                                e.value = parseFloat(f[1].trim()).toFixed(4);
                                var e = document.getElementById("proximityanchor");
                                e.href = 'https://www.repeaterbook.com/repeaters/prox2_result.php?city=&lat=32.836&long=-97.297&distance=200&Dunit=m&band%5B%5D=16&band%5B%5D=4&call=&mode%5B%5D=1&status_id=%25&use=%25&order=distance_calc%2C+distance+ASC&freq='+parseFloat(f[1].trim()).toFixed(4);
                        }
                        if (f[0].trim(' \r\n') == 'Tone Status') {
                                var e = document.getElementById("tone");
                                tonestatus = f[1].trim();
                                if (tonestatus == 'off') {
                                        e.removeAttribute("style");
                                        e.selectedIndex = 0;
                                }
                        }
                        if (f[0].trim(' \r\n') === 'Tone Frequency' && (tonestatus == 'on' || ctcssstatus == 'on')) {
                                var e = document.getElementById("tone");
                                let len = plindex.length;
                                for (let i = 0; i < len; i++) {
                                        if (plindex[i] == f[1].trim()) {
                                                e.selectedIndex = i+1;
                                        }
                                }
                        }
                        if (f[0].trim(' \r\n') == 'CTCSS Status') {
                                var e = document.getElementById("ctcss");
                                ctcssstatus = f[1].trim();
                                if (ctcssstatus == 'off') {
                                        e.removeAttribute("style");
                                        e.checked = false;
                                }else if (ctcssstatus == 'on') {
                                        e.checked = true;
                                }
                        }
                        if (f[0].trim(' \r\n') === 'CTCSS Frequency' && ctcssstatus == 'on') {
                                let len = plindex.length;
                                for (let i = 0; i < len; i++) {
                                        if (plindex[i] == f[1].trim()) {
                                                //e.selectedIndex = i+1;
                                                //e.setAttribute("style","color:yellow;font-weight:bold;background-color:darkblue;");
                                        }
                                }
                        }
                        if (f[0].trim(' \r\n') == 'DCS Status') {
                                var e = document.getElementById("dcs");
                                dcsstatus = f[1].trim();
                                if (dcsstatus == 'off') {
                                        e.removeAttribute("style");
                                        e.selectedIndex = 0;
                                }
                        }
                        if (f[0].trim(' \r\n') === 'DCS Code' && dcsstatus == 'on') {
                                var e = document.getElementById("dcs");
                                let dcslen = dcsindex.length;
                                for (let i = 0; i < dcslen; i++) {
                                        if (dcsindex[i] == f[1].trim()) {
                                                e.selectedIndex = i+1;
                                        }
                                }
                        }
                        if (f[0] == 'Input') {
                                var e = document.getElementById("repeaterinput");
                                var repeaterinput = f[1];
                                if (repeaterinput == 'off') {
                                        e.removeAttribute("style");
                                        e.checked = false;
                                }else if (repeaterinput == 'on') {
                                        e.checked = true;
                                }
                        }
                        if (f[0].trim() == 'Power Output') {
                                var e = document.getElementById("powersel");
                                let powersellen = powerselindex.length;
                                for (let i = 0; i < powersellen; i++) {
                                        if (powerselindex[i] == f[1].trim()) {
                                                e.selectedIndex = i;
                                        }
                                }
                        }
                        if (f[0].trim(' \r\n') == 'SQ') {
                                //var sqlevel =  parseInt(f[1].trim(), 16);
				var sqlevel =  f[1].trim();
                                if (sqlevel > 5) {
                                        if (sqlevel < 10) {
                                                var smlevel=1;
                                        }else if (sqlevel < 14) {
                                                var smlevel=2;
                                        }else if (sqlevel < 18) {
                                                var smlevel=3;
                                        }else if (sqlevel < 22) {
                                                var smlevel=4;
                                        }else if (sqlevel < 26) {
                                                var smlevel=5;
                                        }else if (sqlevel < 29) {
                                                var smlevel=6;
                                        }else{
                                                var smlevel=7;
                                        }
                                }else{
                                        var smlevel=0
                                }
                                var sqstyle = document.querySelector('[data="specialcss"]');
                                var el = document.getElementById("squelchlabel");
                                var e = document.getElementById("squelchsel");
                                var output = document.getElementById("sqlevel");
                                var smoutput = document.getElementById("smlevel");
                                if (squelch == 'Open') {
                                        e.setAttribute("style","color:black;background-color:yellow;");
                                        el.setAttribute("style","color:black;background-color:yellow;");
                                        sqstyle.innerHTML = "input[type=range]::-webkit-slider-thumb { background-color:red; }";
                                }else{
                                        e.removeAttribute("style");
                                        el.removeAttribute("style");
                                        sqstyle.innerHTML = "";
                                }
                                e.value = sqlevel;
                                smoutput.innerHTML = smlevel;
                                if (sqlevel < 10) {
                                        output.innerHTML = "0" + sqlevel;
                                }else{
                                        output.innerHTML = sqlevel;
                                }
                        }
                        if (f[0].trim(' \r\n') == 'Squelch') {
                                squelch = f[1].trim();
                                var sqstyle = document.querySelector('[data="specialcss"]');
                                var el = document.getElementById("squelchlabel");
                                var e = document.getElementById("squelchsel");
                                if (squelch == 'Open') {
                                        e.setAttribute("style","color:black;background-color:yellow;");
                                        el.setAttribute("style","color:black;background-color:yellow;");
                                        sqstyle.innerHTML = "input[type=range]::-webkit-slider-thumb { background-color:red; }";
                                }else{
                                        e.removeAttribute("style");
                                        el.removeAttribute("style");
                                        sqstyle.innerHTML = "";
                                }
                        }
                        if (f[0].trim(' \r\n') === 'Mode') {
                                var e = document.getElementById("mode");
                                let len = modeindex.length;
                                for (let i = 0; i < len; i++) {
                                        if (modeindex[i] == f[1].trim()) {
                                                e.selectedIndex = i+1;
                                        }
                                }
                        }
                        if (f[0].trim(' \r\n') === 'Shift') {
                                var e = document.getElementById("shift");
                                let len = shiftindex.length;
                                for (let i = 0; i < len; i++) {
                                        if (shiftindex[i] == f[1].trim()) {
                                                e.selectedIndex = i+1;
                                        }
                                }
                                var e = document.getElementById("proximitybutton");
                                if (f[1].trim() == 'Simplex') {
                                        e.setAttribute('style','visibility:hidden;opacity:0;');
                                }else{
                                        e.setAttribute('style','visibility:visible;opacity:1;');
                                }
                        }
                        if (f[0].trim(' \r\n') === 'Error') {
                                console.log('error: ' + f[1]);
                                var e = document.getElementById("connected");
                                $('#connected').html('<span style="color:black;background-color:yellow;"'+f[1]+'</span>');
                        }
                        if (f[0].trim(' \r\n') == 'Connected') {
                                var e = document.getElementById("connected");
                                var str = "Connected Allstar nodes: ";
                                let nodes = f[1].split(',');
                                let len = nodes.length;
                                if (!(f[1].match(/NONE/))) {
                                        if (len > 0) {
                                                for (let i = 0; i < len; i++) {
                                                        let node = nodes[i].trim();
                                                        var str = str.concat(" <a href='http://status.allstarlink.org/nodeinfo.cgi?node=" + node + "' target='_blank'>" + node + "</a> ");
                                                }
                                        }
                                        e.setAttribute("style","color:black;background-color:yellow;");
                                }else{
                                        str = str.concat(f[1].trim());
                                        e.removeAttribute("style");
                                }
                                $('#connected').html(str);
                        }
                }
        }

        // Ajax function. this first one runs with the page load.
        $.ajax( { url:'v71cgi.py/?', data: { 'command' : '', 'event' : 'load' }, type:'post', success: function(result) {
                        var r = result.split('\n');
                        r.forEach(mySetAttributes);
                        let now = new Date();
                        $('#timetick').html(now.toLocaleString('en-US',options));
                }
        });

        setInterval(function() {
                if (refreshtime == 0) {
                        document.getElementById("spinny").style.backgroundColor="red";
                        $('#spinny').html('Paused');
                        let now = new Date();
                        $('#timetick').html(now.toLocaleString('en-US',options));
                        return;
                }
                if (contentfocused) {
                        document.getElementById("spinny").style.backgroundColor="red";
                        $('#spinny').html('Paused');
                        let now = new Date();
                        $('#timetick').html(now.toLocaleString('en-US',options));
                        return;
                }
                if ((Date.now() - lastcommandtime) > refreshexpire) {
                        document.getElementById("spinny").style.backgroundColor="red";
                        $('#spinny').html('Paused');
                        let now = new Date();
                        $('#timetick').html(now.toLocaleString('en-US',options));
                        return;
                }
                let spinny = $('#spinny').text();
                var command = '';
                $.ajax( { url:'v71cgi.py/?' + command, data: { 'command' : command, 'event' : 'load' }, type:'post', success: function(result) {
                                var r = result.split('\n');
                                r.forEach(mySetAttributes);
                                let now = new Date();
                                $('#timetick').html(now.toLocaleString('en-US',options));
                                if (spinny == "|") {
                                        spinny = "/";
                                } else if (spinny == "/") {
                                        spinny = char("8212");
                                } else if ( spinny == char("8212") ) {
                                        spinny = "\\";
                                } else {
                                        spinny = "|";
                                }
                                $('#spinny').text(spinny);
                                document.getElementById("spinny").style.backgroundColor='rgba(0, 255, 0, 1';
                        }
                });
        }, refreshtime);

        // whenever we hover over a menu item that has a submenu
        $('li.parent').on('mouseover', function() {
                var $menuItem = $(this),
                $submenuWrapper = $('> .wrapper', $(this));
                // grab the menu item's position relative to its positioned parent
                // place the submenu in the correct position relevant to the menu item
                $submenuWrapper.position({
                        my: "left top",
                        at: "right top",
                        of: $(this),
                        collision: "flipfit"
                });
        });

        $('li.mainparent').on('mouseover', function() {
                var $menuItem = $(this),
                $submenuWrapper = $('> .wrapper', $(this));
                $submenuWrapper.position({
                        my: "left top",
                        at: "left bottom",
                        of: $(this),
                        collision: "fit"
                });
        });

        $('#up,#dw,#squelchUP,#squelchDW,#EL,#low,#high,#fastrestart').click(function() {
                var button = this.id;    // which button was pushed
                if (button == 'fastrestart') {
                        var r = confirm("Restart the Rosston AllStar update node list process?");
                        if (r !== true) {
                                return;
                        }
                }
                var command = this.value;
                lastcommandtime = Date.now();
                var e = document.getElementById(button);
                if (button == 'up' || button == 'dw') {
                        $('#channels').animate({opacity:"0.2"});
                }else{
                        $('#controls').animate({opacity:"0.2"});
                }
                $.ajax( { url:'v71cgi.py/?' + command, data: { 'command' : command, 'event' : button }, type:'post', success: function(result) {
                                var r = result.split('\n');
                                r.forEach(mySetAttributes);
                                let now = new Date();
                                $('#timetick').html(now.toLocaleString('en-US',options));
                                if (button == 'up' || button == 'dw') {
                                        $('#channels').animate({opacity:"1"});
                                }else{
                                        $('#controls').animate({opacity:"1"});
                                }
                        }
                });
        });

        $('#vfosubmit').click(function() {
                var form = this.id;
                var command = '';
                lastcommandtime = Date.now();
                var e = document.getElementById("frequency");
                var name = e.name;
                var val = e.value;
                command = command + ' ' + name + ' ' + val;
                var e = document.getElementById("tone");
                var name = e.name;
                var val = e.options[e.selectedIndex].value;
                command = command + ' ' + name + ' ' + val;
                var e = document.getElementById("ctcss");
                var name = e.name;
                if (e.checked) {
                        command = command + ' ' + name;
                }
                var e = document.getElementById("repeaterinput");
                var name = e.name;
                if (e.checked) {
                        command = command + ' ' + name;
                        let repeaterinput = 'on';
                }else{
                        let repeaterinput = 'off';
                }
                var e = document.getElementById("dcs");
                var name = e.name;
                var val = e.options[e.selectedIndex].value;
                command = command + ' ' + name + ' ' + val;
                var e = document.getElementById("shift");
                var name = e.name;
                var val = e.options[e.selectedIndex].value;
                command = command + ' ' + name + ' ' + val;
                var e = document.getElementById("mode");
                var name = e.name;
                var val = e.options[e.selectedIndex].value;
                command = command + ' ' + name + ' ' + val;
                var form = 'vfo';
                $('#vfodiv').animate({opacity:".1"});
                $.ajax( { url:'v71cgi.py/?' + command, data: { 'command' : command, 'event' : form }, type:'post', success: function(result) {
                                var r = result.split('\n');
                                r.forEach(mySetAttributes);
                                mySetAttributes('Input:'+repeaterinput);
                                let now = new Date();
                                $('#timetick').html(now.toLocaleString('en-US',options));
                                $('#vfodiv').animate({opacity:"1"});
                        }
                });
        });

        $('#ch').click(function() {
                var button = this.id;    // which button was pushed
                var name = this.name;
                lastcommandtime = Date.now();
                var sel = this.title;
                command = name + ' ' + sel;
                console.log(button+' '+command);
                $.ajax( { url:'v71cgi.py/?' + command, data: { 'command' : command, 'event' : button }, type:'post', success: function(result) {
                                var r = result.split('\n');
                                r.forEach(mySetAttributes);
                                mySetAttributes('Input:off');
                                let now = new Date();
                                $('#timetick').html(now.toLocaleString('en-US',options));
                        }
                });
        });

        $('#FWD,#FWD1,#FWD2,#FWD3,#FWD4,#NCTC,#SWIRA,#OUN,#Simplex,#Rosston,#Team,#GMRS,#NWR').click(function() {
                var button = this.id;    // which button was pushed
                var name = this.name;
                lastcommandtime = Date.now();
                var sel = this.title;
                var command = name + ' ' + sel;
                $.ajax( { url:'v71cgi.py/?' + command, data: { 'command' : command, 'event' : button }, type:'post', success: function(result) {
                                var r = result.split('\n');
                                r.forEach(mySetAttributes);
                                mySetAttributes('Input:off');
                                let now = new Date();
                                $('#timetick').html(now.toLocaleString('en-US',options));
                        }
                });
        });

        $('#channelsel').change(function() {
                var button = this.id;    // which button was pushed
                var name = this.name;
                lastcommandtime = Date.now();
                var sel = this.selectedOptions[0].value;
                var command = name + ' ' + sel;
                $('#channels').animate({opacity:".1"});
                $.ajax( { url:'v71cgi.py/?' + command, data: { 'command' : command, 'event' : button }, type:'post', success: function(result) {
                                var r = result.split('\n');
                                r.forEach(mySetAttributes);
                                mySetAttributes('Input:off');
                                let now = new Date();
                                $('#timetick').html(now.toLocaleString('en-US',options));
                                $('#channels').animate({opacity:"1"});
                        }
                });
        });

        $('#powersel').change(function() {
                var button = this.id;    // which button was pushed
                var name = this.name;
                lastcommandtime = Date.now();
                var sel = this.selectedOptions[0].value;
                var command = name + ' ' + sel;
                $('#powersel').animate({opacity:".1"});
                $.ajax( { url:'v71cgi.py/?' + command, data: { 'command' : command, 'event' : button }, type:'post', success: function(result) {
                                var r = result.split('\n');
                                r.forEach(mySetAttributes);
                                let now = new Date();
                                $('#timetick').html(now.toLocaleString('en-US',options));
                                $('#powersel').animate({opacity:"1"});
                        }
                });
        });
        var slider = document.getElementById("squelchsel");
        var output = document.getElementById("sqlevel");
        if (slider.value < 10) {
                output.innerHTML = "0" + slider.value;
        }else{
                output.innerHTML = slider.value;
        }
        output.innerHTML = slider.value; // Display the default slider value
        squelchsel.oninput = function() {
                if (this.value < 10) {
                        output.innerHTML = "0" + this.value;
                }else{
                        output.innerHTML = this.value;
                }
        }

        $('#squelchsel').change(function() {
                var button = this.id;    // which button was pushed
                var name = this.name;
                lastcommandtime = Date.now();
                var output = document.getElementById("sqlevel");
                var sel = this.value;
                if (sel < 10) {
                        output.innerHTML = "0" + sel;
                }else{
                        output.innerHTML = sel;
                }
                var command = name + ' ' + sel;
                $('#squelchsel').animate({opacity:".1"});
                $.ajax( { url:'v71cgi.py/?' + command, data: { 'command' : command, 'event' : button }, type:'post', success: function(result) {
                                var r = result.split('\n');
                                r.forEach(mySetAttributes);
                                let now = new Date();
                                $('#timetick').html(now.toLocaleString('en-US',options));
                                $('#squelchsel').animate({opacity:"1"});
                        }
                });
        });

        $("#ptt").click(function() {
                var button = this.id;    // which button was pushed
                var name = this.name;
                lastcommandtime = Date.now();
                var command ='--tx';
                $('#ptt').animate({backgroundColor:"red"});
                $('#ptt').animate({backgroundColor:"initial"},5000);
                countdown(6,'ptt','PTT');
                $.ajax( { url:'v71cgi.py/?' + command, data: { 'command' : command, 'event' : button }, type:'post', success: function(result) {
                                var r = result.split('\n');
                                r.forEach(mySetAttributes);
                                let now = new Date();
                                $('#timetick').html(now.toLocaleString('en-US',options));
                                var e = document.getElementById("ptt");
                                e.removeAttribute("style");
                        }
                });
        });

});
