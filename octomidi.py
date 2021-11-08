import os
import time
import threading

import serial

import rtmidi
from rtmidi.midiutil import open_midiinput
from rtmidi.midiutil import open_midioutput
from rtmidi.midiconstants import (CHANNEL_PRESSURE, CONTROLLER_CHANGE, NOTE_OFF, NOTE_ON, PITCH_BEND, POLY_PRESSURE, PROGRAM_CHANGE)

from mido import MidiFile

class OctoMidiHandler(object):
    def __init__(self, port, channel, callback, verbose=False):
        self.port = port
        self.channel = channel
        self.callback = callback
        self.verbose = verbose

        self._wallclock = time.time()

    def __call__(self, event, data=None):
        message, deltatime = event
        self._wallclock += deltatime

        if len(message) < 3:
            return

        status = message[0]
        note = message[1]
        velocity = message[2]
        if self.verbose:
            print("Midi Received = [ Status: 0x{:x}, Note: {:d}, Velocity: {:d} ]".format(status, note, velocity))

        self.parse_event(status, note, velocity)

    def parse_event(self, status, note, velocity):
        if status & 0xf0 == NOTE_ON and (self.channel <= 0 or status & 0x0f == self.channel) and velocity > 0:
            self.callback(note)

class OctoMidi(threading.Thread):
    def __init__(self, settings):
        super(OctoMidi, self).__init__()

        self.settings = settings

        self.inchannel = self.settings.get_midiinchannel()
        self.outchannel = self.settings.get_midioutchannel()
        self.in_port = self.settings.get_midiindevice()
        self.out_port = self.settings.get_midioutdevice()

        self.midifilepath = False
        self.active = False
        self._destroy = False

    def set_callback(self, callback):
        self.callback = callback

    def open(self):
        if (self.in_port == 'gpio' or self.out_port == 'gpio') and os.path.exists(self.settings.get_serialport()):
            self.serial = serial.Serial(self.settings.get_serialport(), baudrate=38400)
        else:
            self.serial = False
            if self.in_port == 'gpio':
                self.in_port = 'default'
            if self.out_port == 'gpio':
                self.out_port = 'default'

        # Initialize MidiIn
        if self.in_port != 'gpio':
            self.midiin = rtmidi.MidiIn(rtapi=rtmidi.API_LINUX_ALSA)
            try:
                in_ports = self.midiin.get_ports()
                if self.settings.get_verbose():
                    print("Available Midi Input Devices:")
                    for i in range(0, len(in_ports)):
                        print("  {:d}: {}".format(i, in_ports[i]))

                port_index = -1
                for i in range(0, len(in_ports)):
                    if self.in_port in in_ports[i]:
                        port_index = i
                        break
                if port_index < 0:
                    raise rtmidi._rtmidi.InvalidPortError("Port name not found")

                self.midiin.open_port(port_index)
                self.in_port = in_ports[port_index]
            except (EOFError, KeyboardInterrupt, rtmidi._rtmidi.InvalidPortError, TypeError):
                self.midiin = rtmidi.MidiIn().open_virtual_port("Octopy Virtual Input")
                self.in_port = "Octopy Virtual Input"
        if self.settings.get_verbose():
            print("Selected Midi Input Device: {}\n".format(self.in_port))

        # Initialize MidiOut
        if self.out_port != 'gpio':
            self.midiout = rtmidi.MidiOut(rtapi=rtmidi.API_LINUX_ALSA)
            try:
                out_ports = self.midiout.get_ports()
                if self.settings.get_verbose():
                    print("Available Midi Output Devices:")
                    for i in range(0, len(out_ports)):
                        print("  {:d}: {}".format(i, out_ports[i]))

                port_index = 0
                for i in range(0, len(out_ports)):
                    if self.out_port in out_ports[i]:
                        port_index = i
                        break
                if port_index < 0:
                    raise rtmidi._rtmidi.InvalidPortError("Port name not found")

                self.midiout.open_port(port_index)
                self.out_port = out_ports[port_index]
            except (EOFError, KeyboardInterrupt, rtmidi._rtmidi.InvalidPortError, TypeError):
                self.midiout.open_virtual_port("Octopy Virtual Output")
                self.out_port = "Octopy Virtual Output"
        if self.settings.get_verbose():
            print("Selected Midi Output Device: {}\n".format(self.out_port))

        # Register MidiIn Callback
        self.handler = OctoMidiHandler(self.in_port, self.inchannel, self.callback, self.settings.get_verbose())
        if self.in_port != 'gpio':
            self.midiin.set_callback(self.handler)
        elif self.serial:
            self.watcher_thread = threading.Thread(target=self.watcher)
            self.watcher_thread.start()

    def run(self):
        while self._destroy == False:
            if self.active == True and self.midifilepath:

                mid = MidiFile(self.midifilepath)
                if self.settings.get_verbose():
                    print("Midi File Parameters")
                    print("  Type = {:d}".format(mid.type))
                    print("  Length = {:2f}s".format(mid.length))
                    print("  Tracks = {:d}".format(len(mid.tracks)))
                    print("  Ticks Per Beat = {:d}".format(mid.ticks_per_beat))

                for msg in mid.play():
                    if not self.active or self._destroy:
                        break

                    if self.outchannel > 0:
                        msg.channel = self.outchannel

                    if self.out_port == 'gpio':
                        self.midiout.send_message(msg.bytes())
                    elif self.serial:
                        self.serial.write(msg.bytes())
                        self.serial.flush()

                self.active = False
            time.sleep(self.settings.get_threaddelay())

    def watcher(self):
        message = []
        status = 0
        deltatime = time.time()
        while self._destroy == False:
            data = self.serial.read()
            if data:
                for elem in data:
                    message.append(elem)

                # Running status
                if len(message) == 1:
                    if (message[0] & 0xf0) != 0:
                        status = message[0]
                    else:
                        message = [status, message[0]]

                length = self.get_midi_length(message)
                if length <= len(message):
                    deltatime = time.time() - deltatime
                    event = message, deltatime
                    self.handler(event)
                    message = []
                    deltatime = time.time()

    def get_midi_length(self, message):
        if len(message) == 0:
            return 255
        opcode = message[0]
        if opcode >= 0xf4:
            return 1
        if opcode in [0xf1, 0xf3]:
            return 2
        if opcode == 0xf2:
            return 3
        if opcode == 0xf0:
            if message[-1] == 0xf7:
                return len(message)

        opcode = opcode & 0xf0
        if opcode in [0x80, 0x90, 0xa0, 0xb0, 0xe0]:
            return 3
        if opcode in [0xc0, 0xd0]:
            return 2

        return 255

    def play(self):
        self.active = True

    def panic(self):
        for channel in range(16):
            self.midiout.send_message([rtmidi.midiconstants.CONTROL_CHANGE, rtmidi.midiconstants.ALL_SOUND_OFF, 0])
            self.midiout.send_message([rtmidi.midiconstants.CONTROL_CHANGE, rtmidi.midiconstants.RESET_ALL_CONTROLLERS, 0])
            time.sleep(0.05)

    def stop(self, delay=True):
        self.active = False
        self.panic()
        if delay:
            time.sleep(self.settings.get_threaddelay())

    def load(self, path):
        if self.active == True:
            self.stop()
        self.midifilepath = os.path.abspath(path)

    def destroy(self):
        self._destroy = True

    def close(self):
        self.destroy()

        if self.in_port != 'gpio':
            self.midiin.close_port()
            del self.midiin

        if self.out_port != 'gpio':
            self.midiout.close_port()
            del self.midiout

        if (self.in_port == 'gpio' or self.out_port == 'gpio') and self.serial:
            self.serial.close()
            del self.serial
