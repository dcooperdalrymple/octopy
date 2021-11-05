from argparse import Namespace

class OctoSettings:
    def __init__(self):
        self.set(OctoSettings.get_defaults())

    def set(self, settings):
        if type(settings) is Namespace:
            settings = vars(settings)
        if not type(settings) is dict:
            return

        if 'verbose' in settings:
            self.set_verbose(settings['verbose'])
        if 'device' in settings:
            self.set_device(settings['device'])
        if 'buffersize' in settings:
            self.set_buffersize(settings['buffersize'])
        if 'localmedia' in settings:
    	    self.set_localmedia(settings['localmedia'])
        if 'storagemedia' in settings:
            self.set_storagemedia(settings['storagemedia'])
        if 'midiindevice' in settings:
            self.set_midiindevice(settings['midiindevice'])
        if 'midiinchannel' in settings:
            self.set_midiinchannel(settings['midiinchannel'])
        if 'midioutdevice' in settings:
            self.set_midioutdevice(settings['midioutdevice'])
        if 'midioutchannel' in settings:
            self.set_midioutchannel(settings['midioutchannel'])

    def get_defaults():
        return {
            'verbose': False,
            'device': 'default',
            'buffersize': 512,
            'localmedia': './media',
            'storagemedia': False,
            'midiindevice': 1,
            'midiinchannel': 0,
            'midioutdevice': 1,
            'midioutchannel': 0,
        }
    def get_default(key):
        settings = OctoSettings.get_defaults()
        if settings[key]:
            return settings[key]
        return False

    def get_verbose(self):
        return self.verbose
    def set_verbose(self, value):
        self.verbose = value

    def get_device(self):
        return self.device
    def set_device(self, value):
        self.device = value

    def get_buffersize(self):
        return self.buffersize
    def set_buffersize(self, value):
        self.buffersize = value

    def get_localmedia(self):
        return self.localmedia
    def set_localmedia(self, value):
        self.localmedia = value

    def get_storagemedia(self):
        return self.storagemedia
    def set_storagemedia(self, value):
        self.storagemedia = value

    def get_midiindevice(self):
        return self.midiindevice
    def set_midiindevice(self, value):
        self.midiindevice = value

    def get_midiinchannel(self):
        return self.midiinchannel
    def set_midiinchannel(self, value):
        self.midiinchannel = value

    def get_midioutdevice(self):
        return self.midioutdevice
    def set_midioutdevice(self, value):
        self.midioutdevice = value

    def get_midioutchannel(self):
        return self.midioutchannel
    def set_midioutchannel(self, value):
        self.midioutchannel = value

    def set_midichannels(self, input, output):
        self.set_midiinchannel(input)
        self.set_midioutchannel(output)
