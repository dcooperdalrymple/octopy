#!/usr/bin/env python

# Simple wav playing test with pyalsaaudio and py-wavereader

import sys
import getopt
import alsaaudio

import sys
from wavefile import WaveReader


if __name__ == '__main__':

	device = 'default'

	opts, args = getopt.getopt(sys.argv[1:], 'd:')
	for o, a in opts:
		print o
		if o == '-d':
			device = a

	if not args:
		print "usage: playwav.py [-d <device>] <file>"
		sys.exit(2)

	# List cards
	print "Available sound cards:"
	for i in alsaaudio.card_indexes():
		(name, longname) = alsaaudio.card_name(i)
		print(" %d: %s (%s)" % (i, name, longname))

	with WaveReader(args[0]) as r :

		# Print info
		print "Title:", r.metadata.title
		print "Artist:", r.metadata.artist
		print "Channels:", r.channels
		print "Format: 0x%x"%r.format
		print "Sample Rate:", r.samplerate

		device = alsaaudio.PCM(device=device)

		# Set attributes
		device.setchannels(r.channels);
		device.setrate(r.samplerate);
		device.setformat(alsaaudio.PCM_FORMAT_S32_LE)

		periodsize = 512
		device.setperiodsize(periodsize)

		data = r.buffer(periodsize)
		nframes = r.read(data)
		while nframes :
			sys.stdout.write("."); sys.stdout.flush()
			device.write(data[:,:nframes])
			nframes = r.read(data)
