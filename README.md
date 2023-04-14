# Octopy

Multi-channel midi-capable audio/midi player on the Raspberry Pi platform using Python 3.

_By [D. Cooper Dalrymple](https://dcdalrymple.com/), 2021 - 2023_

## What is this and what is it for?

Octopy is intended to be used to play audio tracks synchronized with midi tracks and video output when triggered by midi for the purpose of live music performances. This way, midi-controlled devices (drum machines, keyboards, etc) can be sequenced with a backing track and controlled by a simple and fitting midi device all within a small package, no laptops and fancy DAWs required.

This software could also be configured to play midi files into a midi sound device such as the MT32 or simply play back audio files for other purposes triggered from a device in another location. It is not required that both audio, midi, & video files are provided for each track.

## Requirements

### Hardware

#### Compatible Devices:

* Raspberry Pi 3 or greater _- Raspberry Pi 1 experiences stuttering in midi and audio output (Model 3 A+ used for testing)_
* Linux-based x86-64/ARM computer _- This software has not been optimized for Windows or Mac_

#### Compatible Raspberry Pi Hats:

* HiFiBerry Audio Hats _- Tested with the [DAC+ Standard](https://www.hifiberry.com/shop/boards/hifiberry-dacplus-rca-version/)_
* Serial-based MIDI Hats _- ie: [OSA MIDI Board](https://www.osaelectronics.com/product/midi-board-for-raspberry-pi/) ([custom board](https://www.smbaker.com/raspberry-pi-midi-hat-building-a-raspberry-pi-midi-jukebox) used for testing)_

### Software

* Linux-based OS _- ideally Raspberry Pi OS Lite_
* Python 3.x with pyalsaaudio, python-rtmidi, pyserial, wave, and mido modules
* ALSA
* JACK Audio Connection Kit
* [PyGame](https://www.pygame.org/news)
* Video Player: [pyvidplayer](https://github.com/ree1261/pyvidplayer) (ARM/x86), [OMXPlayer](https://github.com/popcornmix/omxplayer) (ARM), [MPV](https://mpv.io/) (ARM/x86), [FFmpeg](https://www.ffmpeg.org/) (x86), or [hello video](https://github.com/adafruit/pi_hello_video) (ARM)

## Installation

### Dependencies

On Ubuntu/Debian/Raspbian systems, ensure that all dependencies are met by typing `sudo apt-get install libasound2-dev libjack-dev` and `pip3 install pyalsaaudio python-rtmidi pyserial wave mido pygame` in the terminal. At least one of the 3 aforementioned video playback handlers must also be installed if you plan on using video files.

#### PyVidPlayer

This is the preferred video playback method (especially for headless operation) because it renders directly to the pygame output buffer. The typical installation process is as follows (from within the `octopy` directory):

```
sudo apt-get install libmediainfo-dev libavcodec-dev libavfilter-dev libavdevice-dev libavformat-dev libavutil-dev libswscale-dev libswresample-dev libpostproc-dev ffmpeg
git submodules init
git submodules update
pip3 install -r pyvidplayer/requirements.txt
```

Notes:
* If you have trouble installing the recommended python package versions, try directly installing the packages listed in `pyvidplayer/requirements.txt` without the specified version number.
* It may also be necessary to create an empty `__init__.py` file within the `pyvidplayer` directory to allow the module to be loaded.

#### OMXPlayer

This video playback utility will only work on Raspbian devices. Follow the instructions at the [popcornmix/omxplayer repository](https://github.com/popcornmix/omxplayer) for installation. This utility supports the following formats: `avi, mov, mkv, mp4, m4v`.

#### MPV

MPV is supported on both Raspbian and x86 systems (Linux, Windows, & Mac). Follow the instructions on the [MPV website](https://mpv.io/installation/) for installation. On Linux and Raspbian systems, it should be as simple as running: `sudo apt-get install mpv`.

#### FFmpeg

FFmpeg supports a wider range of video playback formats, but is typically only compatible with x86-based systems. If using a ubuntu/debian-based system, install FFmpeg with this command: `sudo apt-get install ffmpeg`.

#### hello video

Raspberry Pi hello video playback utility will only work on Raspbian devices. Follow the instructions at the [adafruit/pi_hello_video repository](https://github.com/adafruit/pi_hello_video) for installation. This utility only supports the `h264` format.

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
