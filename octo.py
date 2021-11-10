#!/usr/bin/env python3
# vim:fileencoding=ISO-8859-1
#
# Title: Octopy
# Description: Multi-channel midi-activated audio player with synchronized midi output on the Raspberry Pi platform
# Author: D Cooper Dalrymple (https://dcdalrymple.com/)
# Created: 2017-10-19
# Updated: 2021-11-09

try:
    import sys
    import getopt
    import time
    import argparse
    import threading

    # Libraries included in other files
    import os
    import configparser
    import subprocess
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
from octomanager import OctoManager

from getch import _Getch

def handle_midi(note):
    if note > 0 and files.getfiles() and note <= len(files.getfiles()):
        manager.stop()

        file = files.getfiles()[note-1]
        if settings.get_verbose():
            print("File Selected: " + file.get_description())

        manager.load(file)
        manager.start()

    elif note == 0:
        manager.stop()

if __name__ == '__main__':

    settings = OctoSettings()

    parser = argparse.ArgumentParser(description="Octopy")
    parser.add_argument('--verbose', action='store_true', default=settings.get('verbose'))
    parser.add_argument('--audiodevice', type=str, default=settings.get('audiodevice'), metavar='Audio Device Index')
    parser.add_argument('--buffersize', type=int, default=settings.get('buffersize'), metavar='Buffer Size')
    parser.add_argument('--localmedia', type=str, default=settings.get('localmedia'), metavar='Relative Media Directory')
    parser.add_argument('--storagemedia', type=str, default=settings.get('storagemedia'), metavar='External Storage Media Directory')
    parser.add_argument('--midiindevice', type=str, default=settings.get('midiindevice'), metavar='Midi Input Device')
    parser.add_argument('--midiinchannel', type=int, default=settings.get('midiinchannel'), metavar='Midi Input Channel Filter', help='Used for selecting song playback')
    parser.add_argument('--midioutdevice', type=str, default=settings.get('midioutdevice'), metavar='Midi Output Device')
    parser.add_argument('--midioutchannel', type=int, default=settings.get('midioutchannel'), metavar='Midi Output Channel', help='When > 0, force a midi channel. Otherwise, use original midi message channels.')

    settings.set(parser.parse_args())

    # Initialize and build file list (local and storage)
    files = OctoFiles(settings)
    if settings.get_storagemedia():
        usb = OctoUsb(settings)
        if usb.getpath():
            files.append(usb.getfiles())

    if settings.get_verbose():
        files.print()

    # Initialize Audio
    audio = OctoAudio(settings)

    # Initialize Midi
    midi = OctoMidi(settings)
    midi.set_callback(handle_midi)
    midi.open()

    # Setup Audio/Midi Manager
    manager = OctoManager(settings, audio, midi)

    # Wait for keyboard interrupt
    if settings.get_verbose():
        print("Entering main loop. Press 1-9 to play file. Press 0 to stop. Press Q or Control-C to exit.\n")
    try:
        getch = _Getch()
        while True:
            if settings.get_keyboardcontrol():
                ch = getch()
                if ch.isnumeric():
                    handle_midi(int(ch))
                elif ch == "q" or ord(ch) in [3,26]: # 3=Ctrl+C, 26=Ctrl+Z
                    break
            else:
                time.sleep(1)
    except KeyboardInterrupt:
        print()
    finally:
        print("Exiting Octopy.")

        manager.stop()
        audio.close()
        midi.close()
