import os
import time
import threading
import alsaaudio
import wave

from octofiles import OctoFile

class OctoAudio():
    def __init__(self, settings):
        self.settings = settings

        # Set parameters
        self.periodsize = self.settings.get_buffersize()
        self.devicename = self.settings.get_audiodevice()

        self.filepath = False
        self.preloaded = False
        self.wav = False
        self.device = False

        if self.settings.get_verbose():
            self.__list_cards()

    def __list_cards(self):
        print("Available Sound Cards:")
        for i in alsaaudio.card_indexes():
            (name, longname) = alsaaudio.card_name(i)
            print("  {:d}: {} ({})".format(i, name, longname))

        print("Available Audio Devices:")
        devs = alsaaudio.pcms()
        for i in range(len(devs)):
            print("  {:d}: {}".format(i, devs[i]))

        print("Desired Audio Device: {}\n".format(self.devicename))

    def __setup_device(self, channels, framerate, format):
        try:
            device = alsaaudio.PCM(
                type=alsaaudio.PCM_PLAYBACK,
                mode=alsaaudio.PCM_NONBLOCK,
                device=self.devicename,
                periodsize=self.periodsize,
                channels=channels,
                rate=framerate,
                format=format
            )
        except (alsaaudio.ALSAAudioError):
            if self.settings.get_verbose():
                print("Unable to initialize sound card.")
            return False

        if self.settings.get_verbose():
            print("Selected Sound Card: {}\n".format(device.cardname()))

        return device

    def stop(self):
        if self.wav and not self.preloaded:
            self.wav.close()
        self.wav = False
        self.device = False

    def load(self, filepath):
        self.stop()

        if isinstance(filepath, OctoFile):
            if not filepath.has_wave():
                return False
            self.filepath = os.path.abspath(filepath.wavepath)
            if filepath.is_wave_loaded():
                self.wav = filepath.wavefile
                self.wav.rewind()
                self.preloaded = True
                if self.settings.get_verbose():
                    print("Using preloaded wave data.")
            else:
                self.preloaded = False
        else:
            self.filepath = os.path.abspath(filepath)
            self.preloaded = False

        if not self.wav:
            try:
                self.wav = wave.open(self.filepath, 'rb')
            except Exception as e:
                if self.settings.get_verbose():
                    print('Unable to open wave file: {}.'.format(self.filepath))
                    print(repr(e))
                self.filepath = False
                self.wav = False
                return False

        format = None
        if self.wav.getsampwidth() == 1:
            format = alsaaudio.PCM_FORMAT_U8
        elif self.wav.getsampwidth() == 2:
            format = alsaaudio.PCM_FORMAT_S16_LE
        elif self.wav.getsampwidth() == 3:
            format = alsaaudio.PCM_FORMAT_S24_3LE
        elif self.wav.getsampwidth() == 4:
            format = alsaaudio.PCM_FORMAT_S32_LE
        else:
            if self.settings.get_verbose():
                print('Unsupported wave file format: {}.'.format(self.wav.getsampwidth()))
            self.wav = False
            return False

        if self.settings.get_verbose():
            print("Wave File Parameters:")
            print("  Channels = {:d}".format(self.wav.getnchannels()))
            print("  Sample Rate = {:d}".format(self.wav.getframerate()))
            print("  Format = {}".format(format))
            print("  Buffer Size = {}".format(self.periodsize))

        self.device = self.__setup_device(self.wav.getnchannels(), self.wav.getframerate(), format)
        if not self.device:
            self.wav = False
            self.device = False
            return False

        return True

    def is_loaded(self):
        return self.wav

    def get_duration(self):
        if not self.is_loaded():
            return False
        return self.wav.getnframes() / float(self.wav.getframerate())

    def get_period_duration(self):
        if not self.is_loaded():
            return 0
        return self.periodsize / float(self.wav.getframerate())

    def write_buffer(self):
        if not self.wav or not self.device:
            return False

        data = self.wav.readframes(self.periodsize)
        if not data:
            return False

        self.device.write(data)
        return True

    def close(self):
        self.stop()
