import time
import rtmidi
from rtmidi.midiutil import open_midiinput
from rtmidi.midiutil import open_midioutput
from rtmidi.midiconstants import (CHANNEL_PRESSURE, CONTROLLER_CHANGE, NOTE_OFF, NOTE_ON, PITCH_BEND, POLY_PRESSURE, PROGRAM_CHANGE)

class OctoMidiHandler(object):
    def __init__(self, port, channel, callback):
        self.port = port
        self.channel = channel
        self.callback = callback

        self._wallclock = time.time()

    def __call__(self, event, data=None):
        message, deltatime = event
        self._wallclock += deltatime

        if event[0] < 0xF0:
            channel = (event[0] & 0xF) + 1
            status = event[0] & 0xF0
        else:
            status = event[0]
            channel = None

        data1 = data2 = None
        num_bytes = len(event)

        if num_bytes >= 2:
            data1 = event[1]
        if num_bytes >= 3:
            data2 = event[2]

        print("[%s] @%i CH:%2s %02X %s %s", self.port, self._wallclock, channel or '-', status, data1, data2 or '')

        self.parse_event(status, channel, data1, data2)

    def parse_event(status, channel, data1, data2):
        if status == NOTE_ON and (self.channel == channel or self.channel == "all") and data2 != 0x00:
            self.callback(data1)

class OctoMidi:
    def __init__(self, channel, in_port=False, out_port=False):
        self.channel = channel
        self.in_port = in_port
        self.out_port = out_port

    def set_callback(self, callback):
        self.callback = callback

    def open(self):
        # Initialize MidiIn
        if self.in_port:
            try:
                self.midiin, self.in_port = open_midiinput(in_port)
            except (EOFError, KeyboardInterrupt):
                self.midiin = rtmidi.MidiIn()
                self.midiin.open_virtual_port("Octopy Virtual Input")
        else:
            self.midiin = rtmidi.MidiIn()
            available_ports = self.midiin.get_ports()
            if available_ports:
                self.midiin.open_port(0)
                self.in_port = 0
            else:
                self.midiin.open_virtual_port("Octopy Virtual Input")
                self.in_port = "Octopy Virtual Input"

        # Initialize MidiOut
        if self.out_port:
            try:
                self.midiout, port_name = open_midioutput(out_port, "output")
            except (EOFError, KeyboardInterrupt):
                self.midiout = rtmidi.MidiOut()
                self.midiout.open_virtual_port("Octopy Virtual Output")
        else:
            self.midiout = rtmidi.MidiOut()
            available_ports = self.midiout.get_ports()
            if available_ports:
                self.midiout.open_port(0)
            else:
                self.midiout.open_virtual_port("Octopy Virtual Output")

        # Register MidiIn Callback
        self.midiin.set_callback(OctoMidiHandler(self.in_port, self.channel, self.callback))

    def close(self):
        self.midiin.close_port()
        del self.midiin

        self.midiout.close_port()
        del self.midiout
