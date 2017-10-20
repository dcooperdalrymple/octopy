import os
import time
import threading
import alsaaudio
from wavefile import WaveReader

class OctoAudio(threading.Thread):
    def __init__(self, devicename, buffersize, filepath=False):
        super(OctoAudio, self).__init__()

        # Set parameters
        self.periodsize = buffersize
        self.filepath = os.path.abspath(filepath)
        self.active = False
        self._destroy = False

        # Setup device
        self.__list_cards()
        self.__setup_device(devicename)

    def __list_cards(self):
        print "Available sound cards:"
        for i in alsaaudio.card_indexes():
            (name, longname) = alsaaudio.card_name(i)
            print("  %d: %s (%s)" % (i, name, longname))

    def __setup_device(self, devicename):
        self.device = alsaaudio.PCM(device=devicename)
        self.device.setformat(alsaaudio.PCM_FORMAT_FLOAT_LE)
        self.device.setperiodsize(self.periodsize)

    def run(self):
        while self._destroy == False:
            if (self.active == True) and (self.filepath):
                with WaveReader(self.filepath) as wav:
                    print "Title:", wav.metadata.title
                    print "Artist:", wav.metadata.artist
                    print "Channels:", wav.channels
                    print "Format: 0x%x"%wav.format
                    print "Sample Rate:", wav.samplerate

                    # Set device attributes
                    self.device.setchannels(wav.channels)
                    self.device.setrate(wav.samplerate)

                    data = wav.buffer(self.periodsize)
                    nframes = wav.read(data)
                    while (nframes) and (self.active):
                        self.device.write(data[:,:nframes])
                        nframes = wav.read(data)
                    wav.close()
                self.active = False
            time.sleep(0.1)

    def play(self):
        self.active = True

    def stop(self):
        self.active = False
        time.sleep(0.1)

    def load(self, filepath):
        if self.active == True:
            self.stop()
        self.filepath = os.path.abspath(filepath)

    def destroy(self):
        self._destroy = True
