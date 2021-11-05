import time
import rtmidi
from rtmidi.midiutil import open_midiinput
from rtmidi.midiutil import open_midioutput
from rtmidi.midiconstants import (CHANNEL_PRESSURE, CONTROLLER_CHANGE, NOTE_OFF, NOTE_ON, PITCH_BEND, POLY_PRESSURE, PROGRAM_CHANGE)

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

        status = message[0]
        note = message[1]
        velocity = message[2]
        if self.verbose:
            print("Midi Received = [ Status: 0x{:x}, Note: {:d}, Velocity: {:d} ]".format(status, note, velocity))

        self.parse_event(status, note, velocity)

    def parse_event(self, status, note, velocity):
        if status & 0xf0 == NOTE_ON and (self.channel <= 0 or status & 0x0f == self.channel) and velocity > 0:
            self.callback(note)

class OctoMidi:
    def __init__(self, settings):
        self.settings = settings
        self.inchannel = self.settings.get_midiinchannel()
        self.outchannel = self.settings.get_midioutchannel()
        self.in_port = self.settings.get_midiindevice()
        self.out_port = self.settings.get_midioutdevice()

    def set_callback(self, callback):
        self.callback = callback

    def open(self):
        # Initialize MidiIn
        self.midiin = rtmidi.MidiIn(rtapi=rtmidi.API_LINUX_ALSA)
        try:
            in_ports = self.midiin.get_ports()
            if self.settings.get_verbose():
                print("Available Midi Input Devices:")
                for i in range(0, len(in_ports)):
                    print("  {:d}: {}".format(i, in_ports[i]))
            self.midiin.open_port(self.in_port)
        except (EOFError, KeyboardInterrupt, rtmidi._rtmidi.InvalidPortError, TypeError):
            self.midiin = rtmidi.MidiIn().open_virtual_port("Octopy Virtual Input")
            self.in_port = "Octopy Virtual Input"
        if self.settings.get_verbose():
            print("Selected Midi Input Device: {}\n".format(self.in_port))

        # Initialize MidiOut
        self.midiout = rtmidi.MidiOut(rtapi=rtmidi.API_LINUX_ALSA)
        try:
            out_ports = self.midiout.get_ports()
            if self.settings.get_verbose():
                print("Available Midi Output Devices:")
                for i in range(0, len(out_ports)):
                    print("  {:d}: {}".format(i, out_ports[i]))
            self.midiout.open_port(self.out_port)
        except (EOFError, KeyboardInterrupt, rtmidi._rtmidi.InvalidPortError, TypeError):
            self.midiout.open_virtual_port("Octopy Virtual Output")
            self.out_port = "Octopy Virtual Output"
        if self.settings.get_verbose():
            print("Selected Midi Output Device: {}\n".format(self.out_port))

        # Register MidiIn Callback
        self.midiin.set_callback(OctoMidiHandler(self.in_port, self.inchannel, self.callback, self.settings.get_verbose()))

    def close(self):
        self.midiin.close_port()
        del self.midiin

        self.midiout.close_port()
        del self.midiout
