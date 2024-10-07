#!/usr/bin/env /usr/bin/python3
# d700.py
# This is a greatly modified version of the v71cgi.py script.
# Kenwood TM-D700 Remote Base Controller script.
# This will become the new web control interface script.
# For command line use, try running with the "-h" argument for a list of command options.
# 
# Eventually this script should be convertng to JSON instead of plain text output.
#
# David McAnally WD5M
# April 13, 2024
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
ASLNODE='590981'	# Change to your Allstar node. This is required for --nodes, --cop49 and --cop50.
global ser
BAUD='9600'         # 9600, 19200, 38400, 57600
BAND='0'
vhfstep='0'
uhfstep='4'
JSON = False
ASLNODES = []
# the TM-D700 has a different CTCSS list. Also changed in codes.inc and codes.js
plindex = [0,67,0,71.9,74.4,77,79.7,82.5,85.4,88.5,91.5,94.8,97.4,100,103.5,107.2,
	110.9,114.8,118.8,123,127.3,131.8,136.5,141.3,146.2,151.4,156.7,162.2,167.9,
	173.8,179.9,186.2,192.8,203.5,210.7,218.1,225.7,233.6,241.8,250.3]

dcsindex = [0,23,25,26,31,32,36,43,47,51,53,54,65,71,72,73,74,
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
revindex = ['1','0']
smeterindex = ['Off','1','2','3','4','5','6','7']
# The TM-D700 only supports FM and AM.
modeindex = ['FM','AM']

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
# Consider using something other than time=None if the serial port isn't responsive.
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
	line = line[2:-3]
	return line
def upperstr(string):
	return str(string).upper()
def showss(band='0',ssset='0'):
	# ssset=0 disables S-Meter Squelch
	# ssset=1 enables S-Meter Squelch
	answer = cmdRadio('SSQ','0')
	if answer['cmd'] == 'success':
		arr = answer['result']
		return 'Band: ' + bandindex[int(arr[0])] + '\tS-Meter: ' + smeterindex[int(arr[1])]
	else:
		return "SSQ failed: " + answer['result']
def togglerev():
	answer = cmdRadio('REV')
	if answer['cmd'] == 'success':
		rev = str(answer['result'][0])
	else:
		return "REV: ?"
	rev = rev.strip(' \r\n')
	rev = revindex[int(rev)]
	answer = cmdRadio('REV',rev)
	if answer['cmd'] == 'success':
		return 'Reverse: ' + onoffindex[int(answer['result'][0])]
	else:
		return 'Reverse: ?'
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
	CL = len(cmd.strip())
	if cmdargs:
		ser.write(str.encode(cmd + ' ' + cmdargs + '\r'))
	else:
		ser.write(str.encode(cmd + '\r'))
	response = readser()
	if response[0:CL] != cmd:
		return {'cmd':"failed",'result':response}
	response = response[3:].strip('\r\n')
	arr = response.split(',')
	return {'cmd':"success","result":arr}
# return current memory channel number
def getMC():
	answer = cmdRadio('MC',BAND) 
	if answer['cmd'] == 'success':
		return cmdRadio('MC', BAND + ',' + str(answer['result'][1]))
	else:
		return {'cmd':"failed",'result':answer}
# return channel name
def getMNA(channel='001'):
	answer = cmdRadio('MNA','0,' + channel.zfill(3))
	if answer['cmd'] == 'success':
		return 'Name: ' + str(answer['result'][2])
	else:
		return 'Name: '
# return SQ level
def getSQ(arg=''):
	answer = cmdRadio('SQ',BAND)
	if answer['cmd'] == 'success':
		if arg == 'v':
			return answer['result'][1]
		else:
			return 'SQ: ' + str(int(answer['result'][1],16))
	else:
		return ''
# set CNTRL and PTT Band Normally A and A
def setBC(values):
	ctrl = str(values[0])
	ptt = str(values[1])
	if ctrl == '-1':
		response = cmdRadio('BC')
	else:
		response = cmdRadio('BC', ctrl + ',' + ptt)
	if response['cmd'] != 'success':
		print('BC Failed: ' + response['result'])
	else:
		return response['result']
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
def setPC(power='l'):
	if power == 'e':
		power = '2'
	elif power == 'h':
		power = '0'
	else:
		power = '1'
	return cmdRadio('PC',BAND + ',' + str(power))
# export current channels from radio. Note, D700 only has 1 - 199 channels.
def dumpchannels(band='0'):
	maxch = 200
	maxch = 9
	answer = cmdRadio('VMC','0,2')	# set MR mode
	if answer['cmd'] != 'success':
		print(answer)
		return
	answer = cmdRadio('MC',band + ',' + '001') 	# go to channel 1
	print("Channel, Name, RX Frequency, RX Step, Shift, Reverse, Tone Status, CTCSS Status, DCS Status, Tone Frequency, CTCSS Frequency, DCS Code, Offset Frequency, Mode, TX Frequency, TX Step, Lock Out, SQ Status\r")
	i = 1
	while i < maxch:
		answer = cmdRadio('MC',band) 	# pull channel number
		if answer['cmd'] == 'success':
			arr = answer['result']
			if arr[1] == '001' and i > 1:
				return
		else:
			print("MC failed " + answer)
			return
		answer = cmdRadio('MNA','0,' + str(arr[1].zfill(3)))
		if answer['cmd'] == 'success':
			name = answer['result'][2]
		else:
			name=""
		answer = cmdRadio('BY', band)	# squelch open/closed
		if answer['cmd'] == 'success':
			arrby = answer['result']
			by = arrby[1]
		else:
			by = '?'
		string='0,0'
		txfrequency = '0'
		txstep = '0'
		answer = cmdRadio('MR', '0,1,' + str(arr[1].zfill(3)))
		if answer['cmd'] == 'success':
			txarr = answer['result']
			txfrequency = txarr[0]
			txstep = txarr[1]
		answer = cmdRadio('MR', '0,0,' + str(arr[1].zfill(3)))
		if answer['cmd'] == 'success':
			arr = answer['result']
			rxfrequency = Decimal(int(arr[3]))/1000000
			offsetfrequency = Decimal(int(arr[13]))/1000000
			print(arr[2] + ',' + \
				name + ',' + \
				'%.4f' % rxfrequency + ',' + \
				stepindex[int(arr[4])] + ',' + \
				shiftindex[int(arr[5])] + ',' + \
				onoffindex[int(arr[6])] + ',' + \
				onoffindex[int(arr[7])] + ',' + \
				onoffindex[int(arr[8])] + ',' + \
				onoffindex[int(arr[9])] + ',' + \
				'%.1f' % Decimal(str(plindex[int(arr[10])])) + ',' + \
				'%.1f' % Decimal(str(plindex[int(arr[12])])) + ',' + \
				str(dcsindex[int(arr[11][:-1])]) + ',' + \
				'%.4f' % offsetfrequency + ',' + \
				modeindex[int(arr[14])] + ',' + \
				txfrequency.zfill(11) + ',' + \
				stepindex[int(txstep)] + ',' + \
				onoffindex[int(arr[15])] + ',' + \
				byindex[int(by)])
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
# get VFO contents
def getVR():
	vfoband = '2'
	answer = cmdRadio('FQ')
	if answer['cmd'] == 'success':
		rxfrequency = Decimal(int(answer['result'][0]))/1000000
		step = answer['result'][1]
		if rxfrequency < 144:
			vfoband = '1'
		elif rxfrequency >= 144 and rxfrequency < 220:
			vfoband = '2'
		elif rxfrequency >= 220 and rxfrequency < 440:
			vfoband = '2'
		elif rxfrequency >= 440 and rxfrequency < 1200:
			vfoband = '8'
	answer = cmdRadio('VR',vfoband)
	if answer['cmd'] == 'success':
		rxfrequency = Decimal(int(answer['result'][1]))/1000000
		offsetfrequency = Decimal(int(answer['result'][11]))/1000000
		return 'Channel: 000' + '\r\n' \
		+ 'Name: VFO' + '\r\n' \
		'RX Frequency: ' + '%.4f' % rxfrequency + '\r\n' \
		'Shift: ' + shiftwindex[int(answer['result'][3])] + '\r\n' \
		'Reverse: ' + onoffindex[int(answer['result'][4])] + '\r\n' \
		'Tone Status: ' + onoffindex[int(answer['result'][5])] + '\r\n' \
		'CTCSS Status: ' + onoffindex[int(answer['result'][6])] + '\r\n' \
		'DCS Status: ' + onoffindex[int(answer['result'][7])] + '\r\n' \
		'Tone Frequency: ' + '%.1f' % Decimal(str(plindex[int(answer['result'][8])])) + '\r\n' \
		'DCS Code: ' + str(dcsindex[int(answer['result'][9][:-1])]) + '\r\n' \
		'CTCSS Frequency: ' + '%.1f' % Decimal(str(plindex[int(answer['result'][10])])) + '\r\n' \
		'Mode: ' + modeindex[int(answer['result'][12])] + '\r\n' \
		'TX Step: ' + stepindex[int(answer['result'][2])] + ' KHz'
	else:
		return 'Channel: 000'
# get channel contents
def getChannel(channel='001'):
	channel = channel.zfill(3)
	answer = cmdRadio('MR','0,0,' + channel)
	if answer['cmd'] == 'success':
		rxfrequency = Decimal(int(answer['result'][3]))/1000000
		offsetfrequency = Decimal(int(answer['result'][12]))/1000000
		name = getMNA(channel)
		return 'Channel: ' + channel + '\r\n' \
		+ name + '\r\n' \
		'RX Frequency: ' + '%.4f' % rxfrequency + '\r\n' \
		'Shift: ' + shiftwindex[int(answer['result'][5])] + '\r\n' \
		'Reverse: ' + onoffindex[int(answer['result'][6])] + '\r\n' \
		'Tone Status: ' + onoffindex[int(answer['result'][7])] + '\r\n' \
		'CTCSS Status: ' + onoffindex[int(answer['result'][8])] + '\r\n' \
		'DCS Status: ' + onoffindex[int(answer['result'][9])] + '\r\n' \
		'Tone Frequency: ' + '%.1f' % Decimal(str(plindex[int(answer['result'][10])])) + '\r\n' \
		'DCS Code: ' + str(dcsindex[int(answer['result'][11][:-1])]) + '\r\n' \
		'CTCSS Frequency: ' + '%.1f' % Decimal(str(plindex[int(answer['result'][12])])) + '\r\n' \
		'Mode: ' + modeindex[int(answer['result'][14])] + '\r\n' \
		'TX Step: ' + stepindex[int(answer['result'][4])] + ' KHz'
	else:
		return 'Channel: ' + channel
# select channel
def setChannel(channel='001'):
	return cmdRadio('MC',BAND + ',' + str(channel.zfill(3)))
def getASL():
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
		return
	ser = getSer()
	if args.frequency and not args.memory:
		if int(args.frequency*1000) != (args.frequency*1000):
			frequency = str(int((args.frequency + 0.0025) * 1000000)).zfill(11)
		else:
			frequency = str(int(args.frequency * 1000000)).zfill(11)
		if(args.frequency > 300):
			shiftsize = '005000000'
			step = uhfstep
		else:
			shiftsize = '000600000'
			step = vhfstep
		if args.frequency < 144:
			vfoband = '1'
		elif args.frequency >= 144 and args.frequency < 220:
			vfoband = '2'
		elif args.frequency >= 220 and args.frequency < 440:
			vfoband = '2'
		elif args.frequency >= 440 and args.frequency < 1200:
			vfoband = '8'
		else:
			vfoband = '2'
		setBC([0,0])  # set ptt & ctrl band to A
		answer = cmdRadio('VMC','0,0')	# set VFO mode
		if answer['cmd'] != 'success':
			print('VMC failed '.str(answer))
		answer = cmdRadio('FQ',frequency + ',' + step)
		if answer['cmd'] != 'success':
			print('FQ failed '.str(answer))
		answer = cmdRadio('VR',vfoband)
		if answer['cmd'] == 'success':
			arr = answer['result']
			frequency = arr[1]
			step = arr[2]
			shift = arr[3]
			rev = arr[4]
			tone = '0' #arr[5]		# Default to off unless otherwise specified (-t 110.9)
			ctcss = '0' #arr[6]		# Default to off unless otherwise specified (-t 110.9 --ctcss)
			dcs = '0' #arr[7]		# Default to off unless otherwise specified (-d 351)
			tonefreq = arr[8]
			dcscode = arr[9][:-1]	# Default to off unless specified (-d 351)
			ctcssfreq = arr[10]
			shiftsize = arr[11]
			mode = '0'	#arr[12]	# Default is 'FM'
			if(args.frequency >= 108 and args.frequency <= 136):
				mode = '1'		# aircraft AM
			if(args.frequency > 300):
				shiftsize = '005000000'
				step = uhfstep
			else:
				shiftsize = '000600000'
				step = vhfstep
			if args.tone:
				tone = '1'
				ctcss = '0'
				dcs = '0'
				tonefreq = str(plindex.index(args.tone))
			if args.ctcss:
				tone = '0'
				dcs = '0'
				ctcss = '1'
				if args.ctcsstone:
					ctcssfreq = str(plindex.index(args.ctcsstone))
					tonefreq = ctcssfreq
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
			else:	# shift not provided so use Texas band plan
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
					frequency = str(int(frequency)+int(shiftsize)).zfill(11)
				elif(shift == '2'):
					frequency = str(int(frequency)-int(shiftsize)).zfill(11)
					shift = '0'
			# Assemble the memory write command for VFO
			command = frequency + ',' + \
				str(step) + ',' + \
				str(shift) + ',' + \
				rev + ',' + \
				str(tone) + ',' + \
				str(ctcss) + ',' + \
				str(dcs) + ',' + \
				str(tonefreq.zfill(2)) + ',' + \
				str(dcscode.zfill(3) + '0') + ',' + \
				str(ctcssfreq.zfill(2)) + ',' + \
				str(shiftsize.zfill(9)) + ',' + \
				str(mode)
			answer = cmdRadio('VW',vfoband + ',' + command) # save VFO 
			if answer['cmd'] != 'success':
				print('VW FAILED: ' + answer['result'])
			if args.save:
				channel = args.save.zfill(3)
				answer = cmdRadio('MW','0,0,' + channel + ',' + command + ',0') # save channel 
				if answer['cmd'] != 'success':
					print('MW FAILED: ' + answer['result'])
				if args.mn:
					answer = cmdRadio('MNA','0,' + channel + ',' + "{:<8}".format(args.mn[:8]))
					if answer['cmd'] != 'success':
						print('MNA Failed: ' + answer['result'])
					print(getChannel(channel))
			else:
				channel = '000'
				print(getVR())
		print(getSQ())
		print(getBY())
		print(getPC())
		return
	elif args.memory and not args.frequency:
		setBC([0,0])  # set ptt & ctrl band to A
		if args.memory == '0':
			answer = cmdRadio('VMC','0,0')	# set VFO mode
			if answer['cmd'] != 'success':
				print(str(answer))
			print(getVR())
			print(getSQ())
			print(getBY())
			print(getPC())
			return
		answer = cmdRadio('VMC','0,2')	# set MR mode
		if answer['cmd'] != 'success':
			print(answer)
		answer = setChannel(args.memory)
		if answer['cmd'] == 'success':
			channel = args.memory.zfill(3)
			if args.mn:
				answer = cmdRadio('MN',channel + ',' + "{:<6}".format(args.mn[:6]))
				if answer['cmd'] == 'success':
					print('Channel: ' + channel + ', ' + getMNA(channel))
				else:
					print('MN Failed: ' + answer['result'])
		#	print('getChannel...')
			print(getChannel(channel))
			print(getSQ())
			print(getBY())
			print(getPC())
		else:
			print('Channel ' + args.memory.zfill(3) + ' not found or something failed. result=' + answer['result'])
		return
	if args.nodes:
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
		if args.power != 's':
			answer = setPC(args.power)
		print(getPC())
	if args.bc:
		print(setBC(args.bc))
	if args.dumpch:
		dumpchannels(str(bandindex.index(args.dumpch.upper())))
	if args.up:
		answer = cmdRadio('UP')
		if answer['cmd'] == 'success':
			answer = getMC()
			if answer['cmd'] == 'success':
				print(getChannel(answer['result'][1]))
				print(getBY())
	if args.dw:
		answer = cmdRadio('DW')
		if answer['cmd'] == 'success':
			answer = getMC()
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
	if args.ss:
		print(showss('0','0'))
	if args.tone:
		tonefreq = str(plindex.index(args.tone))
		answer = cmdRadio('TN',str(tonefreq.zfill(2)))
	if args.apo:
		if  args.apo == 's':
			answer = cmdRadio('APO')
			print(str(answer))
		else:
			answer = cmdRadio('APO',str(args.apo))
			print(str(answer))
			return
	if args.ps:
		if  args.ps == 's':
			answer = cmdRadio('PS','-1')
			answer = cmdRadio('PS')
			print(str(answer))
		else:
			answer = cmdRadio('PS','-1')
			answer = cmdRadio('PS',str(args.ps))
			print(str(answer))
		return
	if args.rev:
		print(togglerev())
	if args.radio:
		print(str(args.radio))
		answer = cmdRadio(str(args.radio[0]),str(args.radio[1]))
		print(str(answer))
		return
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
		answer = cmdRadio('SFT',shift)
		print(str(answer))
	if len(argv) == 1:
		answer = cmdRadio('VMC','0')
		if answer['cmd'] == 'success':
                    mode = answer['result'][1]
                    if mode == '2':
                        answer = getMC()
                        if answer['cmd'] == 'success':
                            print(getChannel(answer['result'][1]))
                    elif mode == '0':
                        print(getVR())
		print(getSQ())
		print(getBY())
		print(getPC())
	ser.close()
global args
parser = ArgumentParser(add_help=True)
#parser = ArgumentParser(description='Command arguments to control the remote base radio.',add_help=True)
parser.add_argument("-f", "--frequency", help="VFO frequency in MHz", type=float)
parser.add_argument("-s", "--shift", help="Repeater offset. If not specified will autoset from Texas bandplan", nargs='?', const="", type=str)
parser.add_argument("--input", help="Convert frequency to repeater input frequency and simplex mode.", action="store_true")
parser.add_argument("-t", "--tone", help="PL Tone in Hz", nargs='?', type=float)
parser.add_argument("--ctcsstone", help="PL RX Tone in Hz", nargs='?', type=float)
parser.add_argument("--ctcss", help="Enable Tone Squelch", action="store_true")
parser.add_argument("-d", "--dcs", help="DCS Code", nargs='?', type=float)
parser.add_argument("--mode", help="Mode/Modulation type [FM][AM]", nargs='?', const='', type=upperstr )
parser.add_argument("--step", help="Step size KHz: 5, 6.25, 8.33, 10, 12.5, 15, 20, 25, 30, 50, 100", nargs='?', type=str)
parser.add_argument("--save", help="Save to channel n", nargs='?', const='0', type=str)
parser.add_argument("--mn", help="set memory name on saved channel (0 to 6 alphanumeric characters)", type=str)
parser.add_argument("-m", "--memory", help="Recall memory channel", nargs='?', type=str)
parser.add_argument("--up", help="Move UP 1 channel", action="store_true")
parser.add_argument("--dw", help="Move DoWn 1 channel", action="store_true")
parser.add_argument("--squelch", help="Show/Set Noise Squelch Level [(00 to 31)|p|n|s]", nargs='?', const='s', type=str)
parser.add_argument("-p", "--power", help="Show/Set Power Level [h|l|e|s]",	 nargs='?', const='s', type=str)
parser.add_argument("--nodes", help="Show connected Allstar nodes",	 action="store_true")
parser.add_argument("--ss", help="Show radio S-Meter Squelch", action="store_true")
parser.add_argument("--bc", help="Show radio PTT and CTRL Band [0=A,1=B] [0=A,1=B]", nargs=2, type=str)
parser.add_argument("--dumpch", help="Dump channels to file from Band [A|B]", nargs='?', const='A', type=str)
parser.add_argument("--pause", help="Pause for N seconds when intersting events occur.", nargs='?', const=0, type=int)
parser.add_argument("--rev", help="Toggle repeater frequency reverse shift", action="store_true")
parser.add_argument("--rx", help="Enable Receive/Unkey", action="store_true")
parser.add_argument("--tx", help="Enable Transmit/Key", action="store_true")
parser.add_argument("--ps", help="Power radio 1=on/0=off", nargs='?', const='s', type=str)
parser.add_argument("--apo", help="Auto Power off time 0=off/1=30/2=60 minutes", nargs='?', const='s', type=str)
parser.add_argument("--radio", help="Send command to radio. <cmd> [args]", nargs=2, type=str)
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

exit
