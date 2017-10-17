#!/usr/bin/env python

# Octopy: 8 channel midi-activated audio player on the Raspberry Pi platform

import sys
import wave
import getopt
import alsaaudio

from octofiles import OctoFiles

def usage():
	print 'usage: octo.py [-d <device>] [-b <buffersize>] [-m <storagemedia>]'
	sys.exit(2)

if __name__ == '__main__':

	device = 'default'
	buffersize = 512
	storagemedia = 'sda1'

	opts, args = getopt.getopt(sys.argv[1:], 'dbm:h:')
	for o, a in opts:
		if o == '-d':
			device = a
		elif o == '-b':
			buffersize = int(a)
		elif o == '-m':
			storagemedia = a
		elif o == '-h':
			usage()


	files = OctoFiles(storagemedia)
