<!--
rbmenu.inc -    This is the menu bar for the Remote Base control web site.
                This file is included (imported) into the index.php file.
D. McAnally WD5M
-->
                <style>

                        .scrollmenu {
                                //background-color: #00008B;
                                background: rgba(142, 166, 211, 0);
                                overflow-x: auto;
                                white-space: nowrap;
                                z-index: 4;
                                padding:0;
                                margin:0;
                                text-align: center;
                        }
                        ul {
                                //background-color: #00008B;
                                //background: rgba( 0, 0, 139, 1);
                                //background: rgba(142, 166, 211, 0.7);
                        }
                        ul li:hover, ul li:focus, ul li:focus-within {
                                background-color: yellow;
                                color: black;
                        }

                        #scrollmenu > ul > li {
                                display: inline-block;
                                text-align: center;
                                padding: 0.25em 1em;
                                text-decoration: none;
                                z-index: 4;
                                border-style: solid;
                                border-width: 1px;
                        }

                        //#scrollmenu li:hover > .wrapper {
                                //transition: 1s;
                                //display: block;
                                //background-color: yellow;
                                //color: black;
                        //}

                        .wrapper {
                                position: relative;
                                border-style: solid;
                                border-width: 1px;
                        }
                        .wrapper > ul {
                                //width:15em;
                                text-align: left;
                                max-height: 20em;
                                overflow-x: hidden;
                                overflow-y: auto;
                                padding: 0;
                                margin: 0;
                        }
                        .wrapper >ul >li >a >img {
                                height:16px;
                                width:16px;
                                margin: 0 .25em 0 0;
                        }
                        ul {
                                list-style-type: none;
                                padding:0;
                        }

                        li {
                                position: static;
                                padding: 0.25em;
                                margin: 0;
                        }
                        li > .wrapper {
                                position: absolute;
                                z-index: 5;
                                //display: none;
                                display: block;
                                max-height: 20em;
                                transition: 280ms all 120ms ease-out;
                                //transform: rotateX(-90deg) translateX(-50%);
                                transform: rotateX(-90deg);
                                transform-origin: top center;
                                visibility: hidden;
                        }
                        li:hover >.wrapper, li:focus >.wrapper, li:focus-within >.wrapper {
                                //display: block;
                                //background-color: yellow;
                                //color: black;
                                opacity: 1;
                                //transform: rotateX(0) translateX(-50%);
                                transform: rotateX(0);
                                visibility: visible;
                        }

                        ul, a {
                                margin: 0.25em;
                                color: black;
                                font-family: sans-serif;
                                //font-size: 16px;
                                list-style-type: none;
                                //text-decoration: none;
                        }
/*
                        li, ul {
                                margin: 1px;
                        }
*/
                        li .wrapper {
                                cursor: auto;
                        }
                        /*
                        li .wrapper li {
                                padding: 0.25em;
                        }
                        */
                        li:nth-child(2n) {
                                background: lightgrey;
                        }
                        li:nth-child(2n+1) {
                                background: lightgrey;
                        }
                        li.parent {
                                background: lightgrey;
                                cursor: pointer;
                        }
                </style>

<div id="scrollmenu">
        <ul class="scrollmenu">
                <li class="mainparent">Info&#9660;
                        <div class="wrapper">
                                <ul>
                                        <li><a href="help.html" target="rbhelp">Help</a></li>
                                </ul>
                                <ul>
                                        <li><a href="rbchannels.php" target="rbchannels">Channels</a></li>
                                </ul>
                                <ul>
                                        <li><a href="<?php print $ARCHIVE_URL;?>" target="Audio Archive">Audio Archive</a></li>
                                </ul>
                                <ul>
                                        <li><a href="/supermon/node-ban-allow.php?nodes=<?php echo $NODE; ?>" target="BanAllow">Allow List</a></li>
                                </ul>
                        </div>
                </li>
        </ul>
</div>
<!-- end of rbmenu.inc -->
