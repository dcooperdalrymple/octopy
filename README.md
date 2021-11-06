# Octopy

Multi-channel midi-capable audio/midi player on the Raspberry Pi platform using Python 3.

_By D. Cooper Dalrymple, 2021_

## Requirements

* Python 3.x
* pyalsaaudio
* python-rtmidi
* wave
* mido

## Installation

On Unix systems, ensure that all dependencies are met by typing `sudo apt-get install libasound2-dev libjack-dev` and `pip3 install pyalsaaudio python-rtmidi wave mido` in the terminal. Then, type `python3 octo.py` in the top level directory to run the program. Type `python3 octo.py -h` for command information.

If you'd like to automatically mount and search an external storage device such as a USB drive, install the pip packages and run octo.py with sudo. Then use the name of the device (such as "sda1") with the -m argument.

## Usage

All discovered sound/midi files are listed in alphabetical order when you first run the program with the `--verbose` flag set. When a midi note is received on the selected channel (or on all channels by default) that corresponds with number value of the song, it will begin playing along the wave file and midi data depending on what is available (both, only midi, or only wave). If any files were playing previously, they are immediately stopped before the new file begins playing. If the a midi note is received with the note value of 0, it stops all currently playing streams.

This setup may not be ideal for use with a keyboard, but a properly configured midi pad device (such as the Akai LPD8) where each midi note is configured for the desired song and one of the pads is reserved as a stop pad should do the job. Organizing your files to begin with a number signifying the desired MIDI note (with a leading-zero ideally) will help with keeping everything in the proper order.
