import os
import time
import threading
import alsaaudio
import wave

class OctoAudio(threading.Thread):
    def __init__(self, settings):
        super(OctoAudio, self).__init__()

        self.settings = settings

        # Set parameters
        self.periodsize = self.settings.get_buffersize()
        self.devicename = self.settings.get_audiodevice()

        self.filepath = False
        self.active = False
        self._destroy = False

        if self.settings.get_verbose():
            self.__list_cards()

    def __list_cards(self):
        print("Available Sound Cards:")
        for i in alsaaudio.card_indexes():
            (name, longname) = alsaaudio.card_name(i)
            print("  {:d}: {} ({})".format(i, name, longname))

        print("Available Devices:")
        devs = alsaaudio.pcms()
        for i in range(len(devs)):
            print("  {:d}: {}".format(i, devs[i]))
        print()

    def __setup_device(self, channels, framerate, format):
        try:
            device = alsaaudio.PCM(
                type=alsaaudio.PCM_PLAYBACK,
                mode=alsaaudio.PCM_NORMAL,
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

    def run(self):
        while self._destroy == False:
            if self.active == True and self.filepath:

                with wave.open(self.filepath, 'rb') as wav:
                    format = None
                    if wav.getsampwidth() == 1:
                        format = alsaaudio.PCM_FORMAT_U8
                    elif wav.getsampwidth() == 2:
                        format = alsaaudio.PCM_FORMAT_S16_LE
                    elif wav.getsampwidth() == 3:
                        format = alsaaudio.PCM_FORMAT_S24_3LE
                    elif wav.getsampwidth() == 4:
                        format = alsaaudio.PCM_FORMAT_S32_LE
                    else:
                        if self.settings.get_verbose():
                            print('Unsupported wave file format: {}'.format(wav.getsampwidth()))
                        self.active = False
                        break

                    if self.settings.get_verbose():
                        print("Wave File Parameters:")
                        print("  Channels = {:d}".format(wav.getnchannels()))
                        print("  Sample Rate = {:d}".format(wav.getframerate()))
                        print("  Format = {}".format(format))
                        print("  Buffer Size = {}".format(self.periodsize))

                    device = self.__setup_device(wav.getnchannels(), wav.getframerate(), format)

                    data = wav.readframes(self.periodsize)
                    while data and self.active and not self._destroy:
                        device.write(data)
                        data = wav.readframes(self.periodsize)
                    wav.close()

                    if self.settings.get_verbose():
                        print("Wave file writing complete.")

                self.active = False
            time.sleep(self.settings.get_threaddelay())

    def play(self):
        self.active = True

    def stop(self, delay=True):
        self.active = False
        if delay:
            time.sleep(self.settings.get_threaddelay())

    def load(self, filepath):
        if self.active == True:
            self.stop()
        self.filepath = os.path.abspath(filepath)

    def destroy(self):
        self._destroy = True

    def close(self):
        self.destroy()
