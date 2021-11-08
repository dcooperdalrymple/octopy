#!/usr/bin/env python3
# vim:fileencoding=ISO-8859-1
#
# Title: Octopy
# Description: Multi-channel midi-activated audio player with synchronized midi output on the Raspberry Pi platform
# Author: D Cooper Dalrymple (https://dcdalrymple.com/)
# Created: 2017-10-19
# Updated: 2021-11-05

try:
	import sys
	import getopt
	import time
	import argparse

	# Libraries included in other files
	import os
	import configparser
	import subprocess
	import threading
	import alsaaudio
	import wave
	import time
	import rtmidi
	from rtmidi.midiutil import open_midiinput
	from rtmidi.midiutil import open_midioutput
	from rtmidi.midiconstants import (CHANNEL_PRESSURE, CONTROLLER_CHANGE, NOTE_OFF, NOTE_ON, PITCH_BEND, POLY_PRESSURE, PROGRAM_CHANGE)
	from mido import MidiFile
except ImportError as err:
	print("Could not load {} module.".format(err))
	raise SystemExit

from octosettings import OctoSettings
from octofiles import OctoFiles
from octofiles import OctoUsb
from octomidi import OctoMidi
from octoaudio import OctoAudio

def handle_midi(note):
	audio.stop()
	midi.stop()
	if note > 0 and note <= len(files.getfiles()):
		file = files.getfiles()[note-1]
		if settings.get_verbose():
			print("File Selected: " + file.get_description())

		audio.stop()
		midi.stop()

		if file.has_wave():
			audio.load(file.wavepath)
			audio.play()

		if file.has_midi():
			midi.load(file.midipath)
			midi.play()
	elif note == 0:
		audio.stop(False)
		midi.stop(False)

if __name__ == '__main__':

	settings = OctoSettings()

	parser = argparse.ArgumentParser(description="Octopy")
	parser.add_argument('-v', '--verbose', action='store_true', default=settings.get_default('verbose'))
	parser.add_argument('-d', '--device', type=str, default=settings.get_default('audiodevice'), metavar='Audio Device Index')
	parser.add_argument('-b', '--buffersize', type=int, default=settings.get_default('buffersize'), metavar='Buffer Size')
	parser.add_argument('-l', '--localmedia', type=str, default=settings.get_default('localmedia'), metavar='Relative Media Directory')
	parser.add_argument('-m', '--storagemedia', type=str, default=settings.get_default('storagemedia'), metavar='External Storage Media Directory')
	parser.add_argument('-id', '--midiindevice', type=str, default=settings.get_default('midiindevice'), metavar='Midi Input Device')
	parser.add_argument('-ic', '--midiinchannel', type=int, default=settings.get_default('midiinchannel'), metavar='Midi Input Channel Filter', help='Used for selecting song playback')
	parser.add_argument('-od', '--midioutdevice', type=str, default=settings.get_default('midioutdevice'), metavar='Midi Output Device')
	parser.add_argument('-oc', '--midioutchannel', type=int, default=settings.get_default('midioutchannel'), metavar='Midi Output Channel', help='When > 0, force a midi channel. Otherwise, use original midi message channels.')

	settings.set(parser.parse_args())

	# Initialize and build file list (local and storage)
	files = OctoFiles(settings.get_localmedia())
	if settings.get_storagemedia():
		usb = OctoUsb(settings.get_storagemedia())
		if usb.getpath():
			files.append(usb.getfiles())

	if settings.get_verbose():
		files.print()

	# Initialize Audio
	audio = OctoAudio(settings)
	audio.start()

	# Initialize Midi
	midi = OctoMidi(settings)
	midi.set_callback(handle_midi)
	midi.open()
	midi.start()

	# Wait for keyboard interrupt
	if settings.get_verbose():
		print("Entering main loop. Press Control-C to exit.")
	try:
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		print()
	finally:
		print("Exit.")
		audio.close()
		midi.close()
