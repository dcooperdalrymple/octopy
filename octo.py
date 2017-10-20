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
	print 'usage: octo.py [-d <device>] [-b <buffersize>] [-l <localmedia>] [-m <storagemedia>] [-c <midichannel>]'
	sys.exit(2)

def handle_midi(note):
	audio.stop()
	if note >= 0 and note < len(files.getfiles()):
		print "Lets play a file!"
		print "FILE:" + files.getfiles()[note]
		audio.load(files.getfiles()[note])
		audio.play()

if __name__ == '__main__':

	device = 'default'
	buffersize = 512
	localmedia = './media'
	storagemedia = False
	midichannel = 1

	opts, args = getopt.getopt(sys.argv[1:], 'dbmlch')
	for o, a in opts:
		if o == '-d':
			device = a
		elif o == '-b':
			buffersize = a
		elif o == '-m':
			storagemedia = a
		elif o == '-l':
			localmedia = a
		elif o == '-c':
			midichannel = a
		elif o == '-h':
			usage()

	# Initialize and build file list (local and storage)
	files = OctoFiles(localmedia)
	if storagemedia:
		usb = OctoUsb(storagemedia)
		if usb.getpath():
			files.append(usb.getfiles())

	print files.getfiles()

	# Initialize Audio
	audio = OctoAudio(device, buffersize, files.getfiles()[2])
        audio.start()

	# Initialize Midi
	midi = OctoMidi(midichannel)
	midi.set_callback(handle_midi)
	midi.open()

	# Wait for keyboard interrupt
	print "Entering main loop. Press Control-C to exit."
	try:
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		print ""
	finally:
		print "Exit."
		audio.destroy()
		midi.close()
