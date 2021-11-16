import os
import math
import time
import threading

class OctoManagerThread(threading.Thread):
    def __init__(self, settings, audio, midi):
        super(OctoManagerThread, self).__init__()

        self.settings = settings
        self.audio = audio
        self.midi = midi

        self.active = False
        self.stopped = False

    def run(self):
        self.active = True
        self.stopped = False

        duration = max(self.audio.get_duration(), self.midi.get_duration())

        buffer_duration = self.audio.get_period_duration()
        if buffer_duration > 0:
            total_buffers = math.ceil(duration / buffer_duration)
        else:
            total_buffers = 0
        current_buffer = 0

        # Preload buffer
        if self.audio.is_loaded() and self.settings.get_bufferpreload() > 0:
            for i in range(self.settings.get_bufferpreload()):
                self.audio.write_buffer()

        starttime = time.time()
        endtime = starttime + duration
        currenttime = starttime
        deltatime = 0

        while self.active and deltatime <= duration:
            currenttime = time.time()
            deltatime = currenttime - starttime

            # Check if we need an audio buffer write
            if self.audio.is_loaded() and current_buffer < total_buffers:
                while current_buffer < total_buffers and deltatime >= (current_buffer + 1) * buffer_duration:
                    if not self.audio.write_buffer():
                        current_buffer = total_buffers
                        break
                    else:
                        current_buffer += 1

            # Check if we need to write a midi message
            if self.midi.is_loaded():
                while deltatime >= self.midi.get_next_message_time():
                    if not self.midi.send_next_message():
                        break

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

        self.active = False
        self.stopped = True

    def stop(self):
        if not self.active:
            return False
        self.active = False
        return True

class OctoManager():
    def __init__(self, settings, audio, midi):
        self.settings = settings
        self.audio = audio
        self.midi = midi

        self.file = False
        self.thread = False

    def load(self, file):
        self.file = file

        if not self.file:
            self.file = False
            if self.settings.get_verbose():
                print("Manager couldn't load, missing file.")
            return False

        if self.file.has_wave():
            if self.settings.get_verbose():
                print("Loading wave file: {}.".format(self.file.wavepath))
            if not self.audio.load(self.file):
                self.file = False
                if self.settings.get_verbose():
                    print("Manager couldn't load, failed to load audio file.")
                return False

        if self.file.has_midi():
            if self.settings.get_verbose():
                print("Loading midi file: {}.".format(self.file.midipath))
            if not self.midi.load(self.file):
                self.file = False
                if self.settings.get_verbose():
                    print("Manager couldn't load, failed to load midi file.")
                return False

        return True

    def start(self):
        if not self.file:
            if self.settings.get_verbose():
                print("Manager couldn't start, missing file or not loaded properly.")
            return

        self.thread = OctoManagerThread(self.settings, self.audio, self.midi)
        self.thread.start()

    def stop(self):
        self.file = False

        if self.thread and self.thread.stopped:
            del self.thread
            self.thread = False
            return True

        if not self.thread or not self.thread.stop():
            return False
        while not self.thread.stopped:
            time.sleep(self.settings.get_threaddelay())

        if self.settings.get_verbose():
            print('Audio and midi halted.')

        del self.thread
        self.thread = False
        return True
