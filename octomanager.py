import os
import math
import time
import threading

class OctoManager(threading.Thread):
    def __init__(self, settings, audio, midi):
        super(OctoManager, self).__init__()

        self.settings = settings
        self.audio = audio
        self.midi = midi

        self.file = False

        self.active = False
        self.stopped = False

    def load(self, file):
        self.file = file

    def run(self):
        self.active = True
        self.stopped = False

        if not self.file:
            self.active = False
            self.stopped = True
            if self.settings.get_verbose():
                print("Manager couldn't run, missing file.")
            return

        if self.file.has_wave():
            if self.settings.get_verbose():
                print("Loading wave file.")
            if not self.audio.load(self.file.wavepath):
                self.active = False
                self.stopped = True
                return

        if self.file.has_midi():
            if self.settings.get_verbose():
                print("Loading midi file.")
            if not self.midi.load(self.file.midipath):
                self.active = False
                self.stopped = True
                return

        starttime = time.time()
        duration = max(self.audio.get_duration(), self.midi.get_duration())
        endtime = starttime + duration
        currenttime = starttime
        deltatime = 0

        buffer_duration = self.audio.get_period_duration()
        if buffer_duration > 0:
            total_buffers = math.ceil(duration / buffer_duration)
        else:
            total_buffers = 0
        current_buffer = 0

        # Preload first 3 buffers
        if self.audio.is_loaded() and self.settings.get_bufferpreload() > 0:
            for i in range(self.settings.get_bufferpreload()):
                self.audio.write_buffer()

        while self.active and deltatime <= duration:
            currenttime = time.time()
            deltatime = currenttime - starttime

            # Check if we need an audio buffer write
            if self.audio.is_loaded() and current_buffer < total_buffers:
                while current_buffer < total_buffers and deltatime >= (current_buffer + 1) * buffer_duration:
                    if not self.audio.write_buffer():
                        current_buffer = total_buffers
                    else:
                        current_buffer += 1

            # Check if we need to write a midi message
            if self.midi.is_loaded():
                while deltatime >= self.midi.get_next_message_time():
                    self.midi.send_next_message()

            # See how long we need to sleep
            if self.audio.is_loaded() and self.midi.is_loaded():
                delay = min(self.midi.get_current_message_time(), (current_buffer+1)*buffer_duration) - deltatime
            elif self.audio.is_loaded():
                delay = (current_buffer+1)*buffer_duration - deltatime
            elif self.midi.is_loaded():
                delay = self.midi.get_current_message_time() - deltatime
            if delay > 0:
                time.sleep(delay)

        self.midi.stop()
        self.audio.stop()

        self.stopped = True

    def stop(self):
        if not self.active:
            return
        self.active = False
        while not self.stopped:
            time.sleep(self.settings.get_threaddelay())
        print('Audio and midi halted.')
        self.file = False
