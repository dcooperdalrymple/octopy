#!/usr/bin/env python

# Octopy: 8 channel midi-activated audio player on the Raspberry Pi platform

import sys
import getopt
import time

from octofiles import OctoFiles
from octofiles import OctoUsb
from octomidi import OctoMidi
from octoaudio import OctoAudio

def usage():
	print 'usage: octo.py [-d <device>] [-b <buffersize>] [-l <localmedia>] [-m <storagemedia>]'
	sys.exit(2)

if __name__ == '__main__':

	device = 'default'
	buffersize = 512
	localmedia = './media'
	storagemedia = False

	opts, args = getopt.getopt(sys.argv[1:], 'dbmlh')
	for o, a in opts:
		if o == '-d':
			device = a
		elif o == '-b':
			buffersize = int(a)
		elif o == '-m':
			storagemedia = a
		elif o == '-l':
			localmedia = a
		elif o == '-h':
			usage()

	files = OctoFiles(localmedia)

	if storagemedia:
		usb = OctoUsb(storagemedia)
		if usb.getpath():
			files.append(usb.getfiles())

	print files.getfiles()

	audio = OctoAudio(device, buffersize, files.getfiles()[2])
	audio.play()

	midi = OctoMidi()

	# Wait for keyboard interrupt
	print "Entering main loop. Press Control-C to exit."
	try:
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		print ""
	finally:
		print "Exit."
		audio.stop()
		midi.close()
