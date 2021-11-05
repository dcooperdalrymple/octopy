# Octopy

Multi-channel midi-capable audio/midi player on the Raspberry Pi platform using Python 3.

_By D. Cooper Dalrymple, 2021_

## Requirements

* Python 3.9+
* pyalsaaudio
* python-rtmidi
* wave
* mido

## Installation

On Unix systems, ensure that all dependencies are met by typing `sudo apt-get install libasound2-dev libjack-dev` and `pip3 install pyalsaaudio python-rtmidi wave mido` in the terminal. Then, type `python3 octo.py` in the top level directory to run the program. Type `python octo.py -h` for command information.

## Usage

All discovered sound/midi files are listed in alphabetical order when you first run the program with the `--verbose` flag set. When a midi note is received on the selected channel (or on all channels by default) that corresponds with number value of the song, it will begin playing along with it's corresponding midi file if available. If any files were playing previously, they are immediately stopped before the new file begins playing. If the a midi note is received with the value of 0, it stops all currently playing streams.

This setup may not be ideal for use with a keyboard, but a properly configured midi pad device (such as the Akai LPD8) where each midi note is configured for the desired song and one of the pads is reserved as a stop pad should do the job. Organizing your files to begin with a number signifying the desired MIDI note (with a leading-zero ideally) will help with keeping everything in the proper order.
