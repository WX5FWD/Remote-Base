#!/usr/bin/env /usr/bin/python3
#
# TM-V71A Remote Base Controller script.
# This will be web control interface script.
# For command line use, try running with the "-h" argument for a list of command options.
# Note, channel/memory zero (000) is used to store --frequency settings so don't use channel/memory zero.
# Eventually this script should be convertng to JSON instead of plain text output.
#
# David McAnally WD5M
# July 2024
#
from os import environ
from shlex import split
from sys import stderr, exit, argv
from argparse import ArgumentParser
from time import sleep
from decimal import getcontext, Decimal
getcontext().prec = 10
environ["TERM"] = "dumb"

# A few global constants
ASLNODE='YourNodeNbrHere'        # This is required for --nodes, --cop49 and --cop50.
global ser
BAND='0'		# 0 for band A (left), 1 for band B (right)
BAUD='38400'		# 9600, 19200, 38400, 59800
vhfstep='0'
uhfstep='4'
JSON = False
ASLNODES = []

plindex = [67,69.3,71.9,74.4,77,79.7,82.5,85.4,88.5,91.5,94.8,97.4,100,103.5,107.2,
                110.9,114.8,118.8,123,127.3,131.8,136.5,141.3,146.2,151.4,156.7,162.2,167.9,
                173.8,179.9,186.2,192.8,203.5,206.5,210.7,218.1,225.7,229.1,233.6,241.8,250.3,254.1]

dcsindex = [23,25,26,31,32,36,43,47,51,53,54,65,71,72,73,74,
                114,115,116,122,125,131,132,134,143,145,152,155,156,162,165,172,174,
                205,212,223,225,226,243,244,245,246,251,252,255,261,263,265,266,271,274,
                306,311,315,325,331,332,343,346,351,356,364,365,371,
                411,412,413,423,431,432,445,446,452,454,455,462,464,465,466,
                503,506,516,523,565,532,546,565,
                606,612,624,627,631,632,654,662,664,
                703,712,723,731,732,734,743,754]

shiftindex = ['s','p','n']
shiftwindex = ['Simplex','Positive','Negative']

stepindex = ['5','6.25','28.33','10','12.5','15','20','25','30','50','100']

onoffindex = ['off','on']

smeterindex = ['Off','1','2','3','4','5','6','7']

modeindex = ['FM','NFM','AM']

powerindex = ['50 W','10 W','5 W']

byindex = ['Closed','Open']

announceindex = ['off','auto','manual']

languageindex = ['English','Japanese']

totindex = ['3 min','5 min','10 min']

mutehangupindex = ['Off','125','250','500','750','1000']

apoindex = ['Off','30 min','60 min','90 min','120 min','180 min']

rmindex = ['All','Current']

fsindex = ['Fast','Slow']

blindex = ['Off','Max']

blcindex = ['Amber','Green']

srindex = ['Time','Carrier','Seek']

edsindex = ['1200','9600']

totindex = ['3 min','5 min','10 min']

dtmfpauseindex = ['100','250','500','750','1000','1500','2000']

dbindex = ['Band A','Band B','TX A - RX B','TX B - RX A']

bandindex = ['A','B']

bcindex = ['Closed','Open']

sqcindex = ['Off','Busy','SQL','TX','BUSY or TX','SQL or TX']

pkindex = ['WX','Frequency Band','CTRL','Monitor','VQS','VOICE','Group Up','Menu','Mute','Shift','Dual',
                                'M>V','VFO','MR','CALL','MHz','Tone','REV','LOW','LOCK','A/B','ENTER','1750 Hz']

# Define serial port; connect
def getSer():
        from serial import Serial, SerialException
        try:
                ser = Serial('/dev/ttyUSB0', BAUD, timeout=1, exclusive=True)
                return ser
        except SerialException as e:
                sleep(.35)
                try:
                        ser = Serial('/dev/ttyUSB0', BAUD, timeout=1, exclusive=True)
                        return ser
                except SerialException as e:
                        sleep(.35)
                        try:
                                ser = Serial('/dev/ttyUSB0', BAUD, timeout=1, exclusive=True)
                                return ser
                        except SerialException as e:
                                stderr.write('Could not open serial port\n')
                                exit(1)

# read any length non empty serial buffer up to first '\r'
# newer versions of python may privde this as a built-in read function.
def readser():
                # function to read serial port
                line = str(ser.read_until(b'\r'))
                ser.reset_input_buffer()
                ser.reset_output_buffer()
                #print(line)
                line = line[2:-3]
                return line

def upperstr(string):
                return str(string).upper()

def showss(band='0',ssset='0'):
        # ssset=0 disables S-Meter Squelch
        # ssset=1 enables S-Meter Squelch
        answer = cmdRadio('SS','0')
        if answer['cmd'] == 'success':
                arr = answer['result']
                return 'Band: ' + bandindex[int(arr[0])] + '\tS-Meter: ' + smeterindex[int(arr[1])]
        else:
                return "SS failed: " + answer['result']

# asterisk cmd
def asl49():
                from subprocess import check_output
                RES = []
                oscmd = '/usr/bin/sudo /usr/sbin/asterisk -rx "rpt cmd ' + ASLNODE + ' cop 49 xxx"'
                args = split(oscmd)
                try:
                                RES = check_output(args)
                                RES = RES[2:-1]
                                return {'cmd':'success','result':RES}
                except:
                                return {'cmd':'failed','result':RES}

# asterisk cmd
def asl50():
                from subprocess import check_output
                RES = []
                oscmd = '/usr/bin/sudo /usr/sbin/asterisk -rx "rpt cmd ' + ASLNODE + ' cop 50 xxx"'
                args = split(oscmd)
                try:
                                RES = check_output(args)
                                RES = RES[2:-1]
                                return {'cmd':'success','result':RES}
                except:
                                return {'cmd':'failed','result':RES}

# Restart asl node-list process
def nodelistrestart():
                from subprocess import check_output
                RES = []
                oscmd = '/usr/bin/sudo /usr/bin/systemctl restart asl-update-node-list.service'
                args = split(oscmd)
                try:
                                RES = check_output(args)
                                RES = RES[2:-1]
                                return {'cmd':'success','result':RES}
                except:
                                return {'cmd':'failed','result':RES}

# Restart asterisk
def aslrestart():
                from subprocess import check_output
                RES = []
                oscmd = '/usr/bin/sudo /usr/sbin/asterisk -rx "restart now"'
                #oscmd = '/usr/bin/sudo /sbin/shutdown -r now'
                args = split(oscmd)
                try:
                                RES = check_output(args)
                                RES = RES[2:-1]
                                return {'cmd':'success','result':RES}
                except:
                                return {'cmd':'failed','result':RES}

# Return the list of connected allstar nodes from asterisk
def aslnodes():
                from subprocess import check_output
                NODE = ''
                RES = ''
                NODES = []
                oscmd = '/usr/bin/sudo /usr/sbin/asterisk -rx "rpt lstats ' + ASLNODE + '"'
                args = split(oscmd)
                try:
                                RES = str(check_output(args))
                                RES = RES[2:-1]
                                arr = RES.split('\\n')
                                if len(arr) == 3:
                                        NODES.append('<NONE>')
                                else:
                                        for l in arr[2:]:
                                                f = l.strip(' \r\n').split(' ')
                                                NODES.append(f[0])
                                return {'cmd':'success','result':NODES}
                except:
                                return {'cmd':'failed','result':NODES}

# cmdRadio sends commands to the radio and
# returns the result in a dictionary array.
# success/fail is indicatd by the 'cmd' key value.
# a result list array split by a comma are in the
# 'result' key value. This could become JSON.
def cmdRadio(cmd,cmdargs=''):
                if cmdargs:
                                ser.write(str.encode(cmd + ' ' + cmdargs + '\r'))
                else:
                                ser.write(str.encode(cmd + '\r'))
                response = readser()
                if response[0:2] != cmd:
                                return {'cmd':"failed",'result':response}
                response = response[3:].strip('\r\n')
                arr = response.split(',')
                return {'cmd':"success","result":arr}

def getMR():
                return cmdRadio('MR',BAND)

# return MN channel name
def getMN(channel='000'):
                answer = cmdRadio('MN',channel.zfill(3))
                if answer['cmd'] == 'success':
                                return 'Name: ' + str(answer['result'][1])
                else:
                                return 'Name: '

# return SQ level
def getSQ(arg=''):
                answer = cmdRadio('SQ',BAND)
                if answer['cmd'] == 'success':
                                if arg == 'v':
                                                return answer['result'][0]
                                else:
                                                return 'SQ: ' + str(int(answer['result'][0],16))
                else:
                                return ''

# set CNTRL and PTT Band Normally A and A
def setBC(values):
        ctrl = str(values[0])
        ptt = str(values[1])
        if ctrl == '-1':
                return cmdRadio('BC')
        else:
                response = cmdRadio('BC', ctrl + ',' + ptt)
        if response['cmd'] != 'success':
                print('BC Failed: ' + response['result'])
        #else:
                #arr = response[3:].split(',')
                #print('CTRL: ' + bandindex[int(arr[0])] + '\tPTT: ' + bandindex[int(arr[1])])
                #print('CTRL: ' + byindex[int(response['result'][1])])

# set SQ level
def setSQ(squelch='8'):
                if squelch == 'p':
                                cursquelch = int(getSQ('v'),16)
                                squelch = str(hex(cursquelch + 1))
                                squelch = squelch[2:]
                elif squelch == 'n':
                                cursquelch = int(getSQ('v'),16)
                                squelch = str(hex(cursquelch - 1))
                                squelch = squelch[2:]
                elif squelch == 's':
                                return getSQ()
                else:
                                squelch = str(hex(int(squelch)))
                                squelch = squelch[2:]
                return cmdRadio('SQ',BAND + ',' + squelch.zfill(2).upper())

# return BY value to show open/closed squelch
def getBY():
                answer = cmdRadio('BY',BAND)
                if answer['cmd'] == 'success':
                                return 'Squelch: ' + byindex[int(answer['result'][1])]
                else:
                                return 'Squelch: '

# return transmit power setting
def getPC():
                answer = cmdRadio('PC',BAND)
                if answer['cmd'] == 'success':
                                return 'Power Output: ' + powerindex[int(answer['result'][1])]
                else:
                                return 'Power Output: '

# set transmit power
def setPC(power='e'):
                if power == 'h':
                                power = '0'
                elif power == 'l':
                                power = '1'
                else:
                                power = '2'
                return cmdRadio('PC',BAND + ',' + str(power))
                #answer = cmdRadio('PC',BAND + ',' + str(power))
                #if answer['cmd'] == 'success':
                #                return 'Power Output: ' + powerindex[int(answer['result'][1])]
                #else:
                #                return 'Power Output: '

def dumpchannels(band='0'):
        #dump all channels
        maxch = 999
        print("Channel,Name,RX Frequency,RX Step,Shift,Reverse,Tone Status,CTCSS Status,DCS Status,Tone Frequency,CTCSS Frequency,DCS Code,Offset Frequency,Mode,TX Frequency,TX Step,Lock Out,SQ Status\r")
        answer = cmdRadio('VM', band + ',1') # Toggle it back to Memory mode
        if answer['cmd'] != 'success':
                print("VM command failed :" + str(answer))
        answer = cmdRadio('MR', band + ',000') # move to channel 0
        if answer['cmd'] != 'success':
                print("MR command failed " + answer)
        i = 0
        while i < maxch:
                answer = cmdRadio('MR', band)
                if answer['cmd'] == 'success':
                        arr = answer['result']
                        if arr[1] == '000' and i > 0:
                                return
                else:
                        print("MR failed " + answer)
                        return
                answer = cmdRadio('MN', str(arr[1].zfill(3)))
                if answer['cmd'] == 'success':
                        name = answer['result'][1]
                        #arrname = answer['result']
                        #name = arrname[1]
                else:
                        name=""
                answer = cmdRadio('BY', band)
                if answer['cmd'] == 'success':
                        arrby = answer['result']
                        by = arrby[1]
                else:
                        by = '?'
                answer = cmdRadio('ME', str(arr[1].zfill(3)))
                if answer['cmd'] == 'success':
                        arr = answer['result']
                        rxfrequency = Decimal(int(arr[1]))/1000000
                        offsetfrequency = Decimal(int(arr[11]))/1000000
                        print(arr[0] + ',' + \
                                name + ',' + \
                                '%.4f' % rxfrequency + ',' + \
                                stepindex[int(arr[2])] + ',' + \
                                shiftindex[int(arr[3])] + ',' + \
                                onoffindex[int(arr[4])] + ',' + \
                                onoffindex[int(arr[5])] + ',' + \
                                onoffindex[int(arr[6])] + ',' + \
                                onoffindex[int(arr[7])] + ',' + \
                                '%.1f' % Decimal(str(plindex[int(arr[8])])) + ',' + \
                                '%.1f' % Decimal(str(plindex[int(arr[9])])) + ',' + \
                                str(dcsindex[int(arr[10])]) + ',' + \
                                '%.4f' % offsetfrequency + ',' + \
                                modeindex[int(arr[12])] + ',' + \
                                arr[13] + ',' + \
                                stepindex[int(arr[14])] + ',' + \
                                onoffindex[int(arr[15])] + ',' + \
                                bcindex[int(by)])
                else:
                        print(str(arr[i].zfill(3)) + ',C')
                if args.pause and by == "1":
                        if args.pause >= 99:
                                return
                        else:
                                sleep(args.pause)
                i += 1
                answer = cmdRadio('UP')
                if answer['cmd'] != 'success':
                        print("UP failed:" + answer)
                        return

# function to set menu settings
def setmenu(values):
        smi=int(values[0])
        smv=values[1]
        answer = cmdRadio('MU')
        if answer['cmd'] == 'success':
                arr = answer['result']
                arr[smi]=smv
                j=','
                answer = cmdRadio('MU', j.join(arr))
        return answer

# function to show menu settings
def showmenu():
                answer = cmdRadio('MU')
                if answer['cmd'] != 'success':
                        return 'MU failed: ' + answer
                arr = answer['result']
                #arr = response.split(',')
                return 'Beep [0]: ' + onoffindex[int(arr[0])] + '\t\t\t\t' \
                'Beep Volume [1]: ' + arr[1] + '\r\n' \
                'Ext Speaker Mode [2]: ' + arr[2] + '\t\t\t' \
                'Announce [3]: ' + announceindex[int(arr[3])] + '\r\n' \
                'Language [4]: ' + languageindex[int(arr[4])] + '\t\t\t' \
                'Voice Volume [5]: ' + arr[5] + '\r\n' \
                'Voice Speed [6]: ' + arr[6] + '\t\t\t' \
                'Playback Repeat [7]: ' + onoffindex[int(arr[7])] + '\r\n' \
                'Playback Repeat Interval [8]: ' + arr[8] + '\t' \
                'Continous Recording [9]: ' + onoffindex[int(arr[9])] + '\r\n' \
                'VHF AIP [10]: ' + onoffindex[int(arr[10])] + '\t\t\t' \
                'UHF AIP [11]: ' + onoffindex[int(arr[11])] + '\r\n' \
                'S-meter Squelch hang up time [12]: ' + mutehangupindex[int(arr[12])] + '\t' \
                'Mute hang up time [13]: ' + mutehangupindex[int(arr[13])] + '\r\n' \
                'Beat Shift [14]: ' + onoffindex[int(arr[14])] + '\t\t\t' \
                'Time-out timer [15]: ' + totindex[int(arr[15])] + '\r\n' \
                'Recall Method [16]: ' + rmindex[int(arr[16])] + '\t\t\t' \
                'EchoLink Speed [17]: ' + fsindex[int(arr[17])] + '\r\n' \
                'DTMF Hold [18]: ' + onoffindex[int(arr[18])] + '\t\t\t' \
                'DTMF Speed [19]: ' + fsindex[int(arr[19])] + '\r\n' \
                'DTMF Pause [20]: ' + dtmfpauseindex[int(arr[20])] + '\t\t\t' \
                'DTMF Key Lock [21]: ' + onoffindex[int(arr[21])] + '\r\n' \
                'Auto Repeater Offset [22]: ' + onoffindex[int(arr[22])] + '\t\t' \
                '1750 TX Hold [23]: ' + onoffindex[int(arr[23])] + '\r\n' \
                'Unknown [24]: ' + arr[24] + '\t\t\t\t' \
                'Brightness level [25]: ' + arr[25] + '\r\n' \
                'Auto Brightness [26]: ' + onoffindex[int(arr[26])] + '\t\t' \
                'Backlight Color [27]: ' + blcindex[int(arr[27])] + '\r\n' \
                'PF 1 Key [28]: ' + pkindex[int(arr[28],16)] + '\t\t\t' \
                'PF 2 Key [29]: ' + pkindex[int(arr[29],16)] + '\r\n' \
                'Mic PF 1 Key [30]: ' + pkindex[int(arr[30],16)] + '\t\t\t' \
                'Mic PF 2 Key [31]: ' + pkindex[int(arr[31],16)] + '\r\n' \
                'Mic PF 3 Key [32]: ' + pkindex[int(arr[32],16)] + '\t\t\t' \
                'Mic PF 4 Key [33]: ' + pkindex[int(arr[33],16)] + '\r\n' \
                'Mic Key Lock [34]: ' + onoffindex[int(arr[34])] + '\t\t\t' \
                'Scan Resume [35]: ' + srindex[int(arr[35])] + '\r\n' \
                'APO [36]: ' + apoindex[int(arr[36])] + '\t\t\t\t' \
                'Ext Data Band [37]: ' + dbindex[int(arr[37])] + '\r\n' \
                'Ext Data Speed [38]: ' + edsindex[int(arr[38])] + '\t\t' \
                'SQC Source [39]: ' + sqcindex[int(arr[39])] + '\r\n' \
                'Auto PM Store [40]: ' + onoffindex[int(arr[40])] + '\t\t\t' \
                'Display Partion Bar [41]: ' + onoffindex[int(arr[41])]

# get channel contents
def getChannel(channel='000'):
                channel = channel.zfill(3)
                answer = cmdRadio('ME',channel)
                if answer['cmd'] == 'success':
                                rxfrequency = Decimal(int(answer['result'][1]))/1000000
                                offsetfrequency = Decimal(int(answer['result'][11]))/1000000
                                name = getMN(channel)
                                return 'Channel: ' + channel + '\r\n' \
                                + name + '\r\n' \
                                'RX Frequency: ' + '%.4f' % rxfrequency + '\r\n' \
                                'Shift: ' + shiftwindex[int(answer['result'][3])] + '\r\n' \
                                'Tone Status: ' + onoffindex[int(answer['result'][5])] + '\r\n' \
                                'CTCSS Status: ' + onoffindex[int(answer['result'][6])] + '\r\n' \
                                'DCS Status: ' + onoffindex[int(answer['result'][7])] + '\r\n' \
                                'Tone Frequency: ' + '%.1f' % Decimal(str(plindex[int(answer['result'][8])])) + '\r\n' \
                                'CTCSS Frequency: ' + '%.1f' % Decimal(str(plindex[int(answer['result'][9])])) + '\r\n' \
                                'DCS Code: ' + str(dcsindex[int(answer['result'][10])]) + '\r\n' \
                                'Mode: ' + modeindex[int(answer['result'][12])] + '\r\n' \
                                'TX Step: ' + stepindex[int(answer['result'][14])] + ' KHz\r\n'
                else:
                                return 'Channel: ' + channel

# select channel
def setChannel(channel='000'):
                return cmdRadio('MR',BAND + ',' + str(channel.zfill(3)))

def getASL():
                #return 'Connected: <NONE>'
                answer = aslnodes()
                if answer['cmd'] == 'success':
                                return 'Connected: ' + str(','.join(answer['result']))
                else:
                                return 'Connected: <NONE>'


def MAIN():
                global ASLNODES
                global ser
                global BAND
                global args

                if args.nodelistres:
                                print(nodelistrestart())
                                return
                if args.aslres:
                                print(aslrestart())
                                return
                if args.asl49:
                                print(asl49())
                                return
                if args.asl50:
                                print(asl50())
                                return
                if args.nodes:
                                print(getASL())
                ser = getSer()
                answer = cmdRadio('VM', BAND + ',1') # Toggle it back to Memory mode
                if answer['cmd'] != 'success':
                                print("VM command failed :" + str(answer))
                if args.frequency and not args.memory:
                                #if args.frequency >= 440 and args.frequency <= 450:
                                #    print("ERROR: This remote base is limited to 2M frequenciees.")
                                #    return
                                setBC([BAND,BAND])  # set ptt & ctrl band to A
                                setmenu(['37', BAND])  # set external data band to A
                                cmdRadio('CD','0')  # set to frequency channel mode
                                answer = cmdRadio('ME','000')
                                if answer['cmd'] == 'success':
                                                arr = answer['result']
                                                frequency = arr[1]
                                                step = arr[2]
                                                shift = arr[3]
                                                tone = '0' #arr[5]              # Default to off unless otherwise specified (-t 110.9)
                                                ctcss = '0' #arr[6]             # Default to off unless otherwise specified (-t 110.9 --ctcss)
                                                dcs = '0' #arr[7]               # Default to off unless otherwise specified (-d 351)
                                                tonefreq = arr[8]
                                                ctcssfreq = arr[9]
                                                dcscode = '0' #arr[10]  # Default to off unless specified (-d 351)
                                                shiftsize = arr[11]
                                                mode = '0' # arr[12]    # Default is 'FM'
                                                txfrequency = arr[13]
                                                txstepsize = arr[14]
                                                lockout = arr[15]
                                                if(args.frequency >= 108 and args.frequency <= 136):
                                                                mode = '2'              # aircraft AM
                                                if(args.frequency > 300):
                                                                shiftsize = '05000000'
                                                                step = uhfstep
                                                else:
                                                                shiftsize = '00600000'
                                                                step = vhfstep
                                                if args.save:
                                                                channel = args.save.zfill(3)
                                                else:
                                                                channel = '000'
                                                frequency = str(int(args.frequency * 1000000)).zfill(10)
                                                if args.tone:
                                                                tone = '1'
                                                                dcs = '0'
                                                                tonefreq = str(plindex.index(args.tone))
                                                if args.ctcss:
                                                                tone = '0'
                                                                dcs = '0'
                                                                ctcss = '1'
                                                                if args.ctcsstone:
                                                                                ctcssfreq = str(plindex.index(args.ctcsstone))
                                                                else:
                                                                                ctcssfreq = tonefreq
                                                if args.dcs:
                                                                tone = '0'
                                                                ctcss = '0'
                                                                dcs = '1'
                                                                dcscode = str(dcsindex.index(args.dcs))
                                                if args.mode:
                                                                mode = str(modeindex.index(args.mode.upper()))
                                                if args.shift:
                                                                if args.shift == 'p':
                                                                                shift = '1'
                                                                elif args.shift == 'm':
                                                                                shift = '2'
                                                                elif args.shift == 'n':
                                                                                shift = '2'
                                                                elif args.shift == 's':
                                                                                shift = '0'
                                                                                shiftsize = '0'
                                                                else:
                                                                                shift = '0'
                                                                                shiftsize = '0'
                                                else:   # shift not provided so use Texas band plan
                                                                if(args.frequency >= 145.1 and args.frequency <= 145.5):
                                                                                shift = '2'
                                                                elif(args.frequency >= 146.62 and args.frequency < 147):
                                                                                shift = '2'
                                                                elif(args.frequency >= 147 and args.frequency <= 147.38):
                                                                                shift = '1'
                                                                elif(args.frequency >= 441.3 and args.frequency <= 441.375):
                                                                                shift = '1'
                                                                elif(args.frequency >= 441.5 and args.frequency <= 441.975):
                                                                                shift = '1'
                                                                elif(args.frequency >= 442 and args.frequency <= 444.975):
                                                                                shift = '1'
                                                                else:
                                                                                shift = '0'
                                                                                shiftsize = '0'
                                                if(args.input and shift != '0'):
                                                                if(shift == '1'):
                                                                                frequency = str(int(frequency)+int(shiftsize)).zfill(10)
                                                                elif(shift == '2'):
                                                                                frequency = str(int(frequency)-int(shiftsize)).zfill(10)
                                                                shift = '0'
                                                # Assemble the memory write command for channel 0
                                                command = channel + ',' + \
                                                                frequency + ',' + \
                                                                str(step) + ',' + \
                                                                str(shift) + ',0,' + \
                                                                str(tone) + ',' + \
                                                                str(ctcss) + ',' + \
                                                                str(dcs) + ',' + \
                                                                str(tonefreq) + ',' + \
                                                                str(ctcssfreq) + ',' + \
                                                                str(dcscode) + ',' + \
                                                                str(shiftsize) + ',' + \
                                                                str(mode) + ',' + \
                                                                '0000000000,0,0'
                                                answer = cmdRadio('ME',command) # save the channel
                                                #if answer['cmd'] == 'success':
                                                        #print(answer)
                                                        #print(getChannel(channel))
                                                if args.mn:
                                                        answer = cmdRadio('MN',channel + ',' + "{:<6}".format(args.mn[:6]))
                                                        if answer['cmd'] == 'success':
                                                                print('Channel: ' + channel + ', ' + getMN(channel))
                                                        else:
                                                                print('MN Failed: ' + answer['result'])
                                                answer = setChannel(channel)
                                                print(getChannel(channel))
                                                print(getSQ())
                                                print(getBY())
                                                print(getPC())
                elif args.memory and not args.frequency:
                                setBC([BAND,BAND]) # set ptt & ctrl band to A
                                setmenu(['37', BAND])  # set external data band to A
                                cmdRadio('CD','0')  # set to frequency channel mode
                                answer = cmdRadio('VM',BAND + ',0')
                                if answer['cmd'] != 'success':
                                                print(answer)
                                answer = cmdRadio('VM',BAND + ',1')
                                if answer['cmd'] != 'success':
                                                print(answer)
                                answer = setChannel(args.memory)
                                if answer['cmd'] == 'success':
                                        #print(answer)
                                        #print(getChannel(args.memory))
                                        channel = args.memory.zfill(3)
                                        if args.mn:
                                                answer = cmdRadio('MN',channel + ',' + "{:<6}".format(args.mn[:6]))
                                                if answer['cmd'] == 'success':
                                                        print('Channel: ' + channel + ', ' + getMN(channel))
                                                else:
                                                        print('MN Failed: ' + answer['result'])
                                        print(getChannel(channel))
                                        print(getSQ())
                                        print(getBY())
                                        print(getPC())
                                else:
                                        print('Channel ' + args.memory.zfill(3) + ' not found or something failed. result=' + answer['result'])
                elif args.clear:
                        if(args.clear.zfill(3) == '000'):
                                print("Channel 000 is not allowed to be cleared")
                        else:
                                channel = args.clear.zfill(3)
                                answer = cmdRadio('MR', BAND + ',' + channel)
                                if answer['cmd'] != 'success':
                                        print("MR command failed " + channel + " " + str(answer))
                                        return
                                #print(getChannel(channel))
                                answer = cmdRadio('ME', channel + ',C')
                                print(answer)
                if args.nodes:
                                #print(getASL())
                                print(getBY())
                if args.squelch:
                                if args.squelch == 's':
                                                print(getSQ())
                                                print(getBY())
                                else:
                                                answer = setSQ(args.squelch)
                                                if answer['cmd'] == 'success':
                                                        print(getSQ())
                                                        print(getBY())
                if args.power:
                                answer = setPC(args.power)
                                if answer['cmd'] == 'success':
                                        print(getPC())
                                #print(setPC(args.power))
                if args.menu:
                        # show menu settings
                        print(showmenu())
                if args.setmenu:
                        print('Setting Menu item ' + str(args.setmenu[0]) + ' to ' + str(args.setmenu[1]))
                        answer = setmenu(args.setmenu)
                        if answer['cmd'] == 'success':
                                print(showmenu())
                        else:
                                print(answer)
                if args.bc:
                        answer = setBC(args.bc)
                        print(answer)
                if args.dumpch:
                        dumpchannels(str(bandindex.index(args.dumpch.upper())))
                if args.up:
                                answer = cmdRadio('UP')
                                if answer['cmd'] == 'success':
                                                answer = getMR()
                                                if answer['cmd'] == 'success':
                                                                print(getChannel(answer['result'][1]))
                                                                print(getBY())
                if args.dw:
                                answer = cmdRadio('DW')
                                if answer['cmd'] == 'success':
                                                answer = getMR()
                                                if answer['cmd'] == 'success':
                                                                print(getChannel(answer['result'][1]))
                                                                print(getBY())
                if args.rx:
                                answer = cmdRadio('RX')
                                if answer['cmd'] == 'success':
                                                print('PTT: Unkeyed')
                                else:
                                                print('PTT: ')
                if args.tx:
                                answer = cmdRadio('TX')
                                print(str(answer))
                                if answer['cmd'] == 'success':
                                                print('PTT: Keyed')
                                else:
                                                print('PTT: ')
                                sleep(5)
                                answer = cmdRadio('RX')
                                if answer['cmd'] == 'success':
                                                print('PTT: Unkeyed')
                                else:
                                                print('PTT: ')
                if args.ss:
                        # show s-meter settings
                        print(showss('0','0'))
                if len(argv) == 1:
                        answer = getMR()
                        if answer['cmd'] == 'success':
                                print(getChannel(answer['result'][1]))
                        print(getSQ())
                        print(getBY())
                        print(getPC())

                ser.close()

global args
parser = ArgumentParser(add_help=True, exit_on_error=True)
#parser = ArgumentParser(description='Command arguments to control the remote base radio.',add_help=True)
parser.add_argument("-f", "--frequency", help="VFO frequency in MHz", type=float)
parser.add_argument("-s", "--shift", help="Repeater offset. If not specified will autoset from Texas bandplan", nargs='?', const="", type=str)
parser.add_argument("--input", help="Convert frequency to repeater input frequency and simplex mode.", action="store_true")
parser.add_argument("-t", "--tone", help="PL Tone in Hz", nargs='?', type=float)
parser.add_argument("--ctcsstone", help="PL RX Tone in Hz", nargs='?', type=float)
parser.add_argument("--ctcss", help="Enable Tone Squelch", action="store_true")
parser.add_argument("-d", "--dcs", help="DCS Code", nargs='?', type=float)
parser.add_argument("--mode", help="Mode/Modulation type", nargs='?', const='', type=upperstr )
parser.add_argument("--step", help="Step size KHz: 5, 6.25, 8.33, 10, 12.5, 15, 20, 25, 30, 50, 100", nargs='?', type=str)
parser.add_argument("--save", help="Save to channel n", nargs='?', const='0', type=str)
parser.add_argument("--mn", help="set memory name on saved channel (0 to 6 alphanumeric characters)", type=str)
parser.add_argument("--clear", help="Clear channel n", type=str)
parser.add_argument("-m", "--memory", help="Recall memory channel", nargs='?', type=str)
parser.add_argument("--up", help="Move UP 1 channel", action="store_true")
parser.add_argument("--dw", help="Move DoWn 1 channel", action="store_true")
parser.add_argument("--squelch", help="Show/Set Noise Squelch Level [(00 to 31)|p|n|s]", nargs='?', const='s', type=str)
parser.add_argument("-p", "--power", help="Show/Set Power Level [h|l|e|s]",      nargs='?', const='e', type=str)
parser.add_argument("--nodes", help="Show connected Allstar nodes",      action="store_true")
parser.add_argument("--menu", help="Show radio menu settings", action="store_true")
parser.add_argument("--ss", help="Show radio S-Meter Squelch", action="store_true")
parser.add_argument("--bc", help="Show radio PTT and CTRL Band [0=A,1=B] [0=A,1=B]", nargs=2, type=str)
parser.add_argument("--setmenu", help="Set menu values", nargs=2, type=str)
parser.add_argument("--dumpch", help="Dump channels to file from Band [A|B]", nargs='?', const='A', type=str)
parser.add_argument("--pause", help="Pause for N seconds when intersting events occur.", nargs='?', const=0, type=int)
parser.add_argument("--rx", help="Enable Receive/Unkey", action="store_true")
parser.add_argument("--tx", help="Enable Transmit/Key", action="store_true")
parser.add_argument("--nodelistres", help="Restart nodelist", action="store_true")
parser.add_argument("--aslres", help="Restart asterisk", action="store_true")
parser.add_argument("--asl49", help="Disable incoming allstar connections using the cop 49 function. ", action="store_true")
parser.add_argument("--asl50", help="Enable incoming allstar connections using the cop 50 function", action="store_true")

if environ.get('QUERY_STRING') == None:
        args = parser.parse_args()
        MAIN()
else:
        from urllib.parse import unquote
        print("Content-Type: text/html;charset=utf-8\r\n")
        print("<html><head></head><body><pre>\r\n")
        query_string = unquote(environ.get('QUERY_STRING'))
        args = parser.parse_args(split(query_string))
        MAIN()
        print("</pre></body></html>\r\n")
