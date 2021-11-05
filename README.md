# Octopy

Multi-channel midi-capable audio/midi player on the Raspberry Pi platform using Python 3.

_By D. Cooper Dalrymple, 2021_

## Requirements

* Python 3.x
* pyalsaaudio
* python-rtmidi
* wave

## Installation

On Unix systems, ensure that all dependencies are met by typing `sudo apt-get install libasound2-dev libjack-dev` and `pip3 install pyalsaaudio python-rtmidi wave` in the terminal. Then, type `python3 octo.py` in the top level directory to run the program. Type `python octo.py -h` for command information.
