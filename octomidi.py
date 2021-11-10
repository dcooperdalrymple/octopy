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

class OctoMidi():
    def __init__(self, settings):
        self.settings = settings

        self.inchannel = self.settings.get_midiinchannel()
        self.outchannel = self.settings.get_midioutchannel()
        self.in_port = self.settings.get_midiindevice()
        self.out_port = self.settings.get_midioutdevice()

        self.midifilepath = False
        self.midifile = False
        self.midimsgs = False
        self.midiindex = 0
        self.miditime = 0

        self._watching = False
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

    def watcher(self):
        message = []
        status = 0
        deltatime = time.time()
        self._watching = True
        while self._destroy == False and self.serial:
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
        self._watching = False

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

    def send_message(self, data):
        if not isinstance(data, bytes):
            data = bytes(data)
        if self.out_port != 'gpio' and self.midiout:
            self.midiout.send_message(data)
        elif self.serial:
            self.serial.write(data)
            self.serial.flush()
        else:
            return False
        return True

    def panic(self):
        for channel in range(16):
            status = rtmidi.midiconstants.CONTROL_CHANGE | (channel & 0x0f)
            self.send_message([status, rtmidi.midiconstants.ALL_SOUND_OFF, 0])
            self.send_message([status, rtmidi.midiconstants.RESET_ALL_CONTROLLERS, 0])
            #time.sleep(self.settings.get_threaddelay())

    def stop(self):
        self.panic()
        self.midifilepath = False
        self.midifile = False
        self.midimsgs = False

    def load(self, path):
        self.stop()

        self.midifilepath = os.path.abspath(path)
        try:
            self.midifile = MidiFile(self.midifilepath)
        except Exception:
            if self.settings.get_verbose():
                print('Unable to open midi file: {}.'.format(self.midifilepath))
            self.midifilepath = False
            self.midifile = False
            self.midimsgs = False
            return False

        self.midimsgs = []
        for msg in self.midifile:
            self.midimsgs.append(msg)

        if self.settings.get_verbose():
            print("Midi File Parameters")
            print("  Type = {:d}".format(self.midifile.type))
            print("  Length = {:2f}s".format(self.midifile.length))
            print("  Tracks = {:d}".format(len(self.midifile.tracks)))
            print("  Messages = {:d}".format(len(self.midimsgs)))
            print("  Ticks Per Beat = {:d}".format(self.midifile.ticks_per_beat))

        self.midiindex = -1
        self.miditime = 0
        return True

    def is_loaded(self):
        return self.midifile and self.midimsgs

    def get_duration(self):
        if not self.is_loaded():
            return 0
        return self.midifile.length

    def get_next_message(self):
        if not self.midimsgs or self.midiindex >= len(self.midimsgs)-1:
            return False

        msg = self.midimsgs[self.midiindex+1]
        self.miditime += msg.time
        self.midiindex += 1

        # Recursively find next real message
        if msg.is_meta:
            return self.get_next_message()

        return msg
    def send_next_message(self):
        msg = self.get_next_message()
        if not msg or msg.is_meta:
            return False
        return self.send_message(msg.bytes())

    def get_current_message_time(self):
        if not self.is_loaded():
            return 0
        return self.miditime
    def get_next_message_time(self, index = None):
        if not self.is_loaded():
            return 0

        if index is None:
            index = self.midiindex

        if index >= len(self.midimsgs) - 1:
            return self.get_duration()

        # Recursively find next real message
        if self.midimsgs[index+1].is_meta:
            return self.get_next_message_time(index+1)

        return self.miditime + self.midimsgs[index+1].time

    def destroy(self):
        self._destroy = True
        while self._watching:
            time.sleep(self.settings.get_threaddelay())

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
