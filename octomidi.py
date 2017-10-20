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

        status = event[0][0]
        note = event[0][1]
        velocity = event[0][2]

#        print "Midi Received: [Status:" + str(status) + ", Note:" + str(note) + ", Velocity:" + str(velocity) + "]"
        self.parse_event(status, note, velocity)

    def parse_event(self, status, note, velocity):
        if status == 153 and velocity > 0:
            self.callback(note)

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
            print available_ports
            if available_ports:
                self.midiin.open_port(1)
                self.in_port = 1
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
            print available_ports
            if available_ports:
                self.midiout.open_port(1)
            else:
                self.midiout.open_virtual_port("Octopy Virtual Output")

        # Register MidiIn Callback
        self.midiin.set_callback(OctoMidiHandler(self.in_port, self.channel, self.callback))

    def close(self):
        self.midiin.close_port()
        del self.midiin

        self.midiout.close_port()
        del self.midiout
