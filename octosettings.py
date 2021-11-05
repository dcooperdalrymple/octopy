from argparse import Namespace

class OctoSettings:
    def __init__(self):
        self.data = OctoSettings.get_defaults()

    def set(self, settings):
        if type(settings) is Namespace:
            settings = vars(settings)
        if not type(settings) is dict:
            return

        self.data = self.data.copy().update(settings)

    def get_defaults():
        return {
            'verbose': False,
            'device': 'default',
            'buffersize': 256,
            'localmedia': './media',
            'storagemedia': False,
            'midiindevice': 1,
            'midiinchannel': 0,
            'midioutdevice': 1,
            'midioutchannel': 0,
            'threaddelay': 0.05,
        }
    def get_default(key):
        settings = OctoSettings.get_defaults()
        if settings[key]:
            return settings[key]
        return False

    def get_verbose(self):
        return self.data.verbose

    def get_device(self):
        return self.data.device
    def get_buffersize(self):
        return self.data.buffersize
    def get_localmedia(self):
        return self.data.localmedia
    def get_storagemedia(self):
        return self.data.storagemedia

    def get_midiindevice(self):
        return self.data.midiindevice
    def get_midioutdevice(self):
        return self.data.midioutdevice

    def get_midiinchannel(self):
        return self.data.midiinchannel
    def set_midiinchannel(self, value):
        self.data.midiinchannel = value
    def get_midioutchannel(self):
        return self.data.midioutchannel
    def set_midioutchannel(self, value):
        self.data.midioutchannel = value
    def set_midichannels(self, input, output):
        self.set_midiinchannel(input)
        self.set_midioutchannel(output)

    def get_threaddelay(self):
        return self.data.threaddelay
