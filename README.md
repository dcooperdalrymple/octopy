# Octopy

Multi-channel midi-capable audio/midi player on the Raspberry Pi platform using Python 3.

_By D. Cooper Dalrymple, 2021_

## Requirements

* Python 3.x
* pyalsaaudio
* python-rtmidi
* pyserial
* wave
* mido

## Installation

### Dependencies

On Unix systems, ensure that all dependencies are met by typing `sudo apt-get install libasound2-dev libjack-dev` and `pip3 install pyalsaaudio python-rtmidi pyserial wave mido` in the terminal.

### Configuration

A configuration file can be used for configuring the default settings for the program. All of the default settings are set by `config.ini` in the `octopy` directory. Copy this file to `~/octopy.ini` to override its values.

### Media

If you'd like to automatically mount and search an external storage device such as a USB drive, install the pip packages and run octo.py with sudo. Then use the name of the device (such as "sda1") with the -m argument or configure Media -> Storage in the user config file. Only files in the top-level directory will be scanned when building the database.

### Running

Type `python3 octo.py` in the top level directory to run the program. Type `python3 octo.py --help` for command information. The command arguments will override any settings defined by the configuration files.

## Usage

### File Playback

All discovered sound/midi files are listed in alphabetical order when you first run the program with the `--verbose` flag set. When a midi note is received on the selected channel (or on all channels by default) that corresponds with number value of the song, it will begin playing along the wave file and midi data depending on what is available (both, only midi, or only wave). If any files were playing previously, they are immediately stopped before the new file begins playing. If the a midi note is received with the note value of 0, it stops all currently playing streams.

This setup may not be ideal for use with a keyboard, but a properly configured midi pad device (such as the Akai LPD8) where each midi note is configured for the desired song and one of the pads is reserved as a stop pad should do the job. Organizing your files to begin with a number signifying the desired MIDI note (with a leading-zero ideally) will help with keeping everything in the proper order.

### MIDI Support

This software supports both USB midi devices or GPIO midi over the Raspberry Pi's serial interface. [See this page](https://www.samplerbox.org/article/midiinwithrpi) for information about configuring the serial port on your Pi.

### Audio Support

Any ALSA-enabled playback interface can be used. See the listed "Available Audio Devices" when you run the program with verbose enabled. A DAC hat such as the HiFiBerry DAC can also be used for audio playback ([see for details](https://www.hifiberry.com/firststeps/)).
