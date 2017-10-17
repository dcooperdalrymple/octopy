import os
import threading
import alsaaudio
from wavefile import WaveReader

class OctoAudio(threading.Thread):
    def __init__(self, devicename, buffersize, filepath):
        super(OctoAudio, self).__init__()

        # Set parameters
        self.periodsize = buffersize
        self.filepath = os.path.abspath(filepath)
        self.active = True

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

    def play(self):
        self.start()

    def stop(self):
        self.active = False
