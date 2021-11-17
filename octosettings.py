import os
from argparse import Namespace
import configparser

class OctoSettings:
    localconfig = 'config.ini'
    userconfig = '~/octopy.ini'

    def __init__(self):
        self.data = self.get_defaults()
        self.set(self.parse_config(os.path.expanduser(self.userconfig)))

    def set(self, settings):
        if type(settings) is Namespace:
            settings = vars(settings)
        if not type(settings) is dict:
            return

        for key, value in settings.items():
            if key in self.data and settings[key] != self.get_defaults()[key]:
                self.data[key] = value

    def get(self, key=''):
        if key != '':
            if key in self.data:
                return self.data[key]
            else:
                return False
        return self.data

    def get_defaults(self):
        if hasattr(self, 'defaults') and type(self.defaults) is dict:
            return self.defaults
        self.defaults = self.parse_config(os.path.dirname(os.path.realpath(__file__)) + '/' + self.localconfig)
        return self.defaults

    def get_default(self, key):
        settings = self.get_defaults()
        if settings[key]:
            return settings[key]
        return False

    def get_verbose(self):
        return self.data['verbose']
    def get_threaddelay(self):
        return self.data['threaddelay']
    def get_keyboardcontrol(self):
        return self.data['keyboardcontrol']
    def get_statusled(self):
        return self.data['statusled']
    def set_statusled(self, value):
        self.data['statusled'] = value

    def get_audiodevice(self):
        return self.data['audiodevice']
    def get_buffersize(self):
        return self.data['buffersize']
    def get_bufferpreload(self):
        return self.data['bufferpreload']

    def get_localmedia(self):
        return self.data['localmedia']
    def get_storagemedia(self):
        return self.data['storagemedia']
    def get_storagemount(self):
        return self.data['storagemount']
    def get_preloadmedia(self):
        return self.data['preloadmedia']

    def get_midiindevice(self):
        return self.data['midiindevice']
    def get_midioutdevice(self):
        return self.data['midioutdevice']
    def get_serialport(self):
        return self.data['serialport']

    def get_midiinchannel(self):
        return self.data['midiinchannel']
    def set_midiinchannel(self, value):
        self.data['midiinchannel'] = value
    def get_midioutchannel(self):
        return self.data['midioutchannel']
    def set_midioutchannel(self, value):
        self.data['midioutchannel'] = value
    def set_midichannels(self, input, output):
        self.set_midiinchannel(input)
        self.set_midioutchannel(output)

    def parse_config(self, path):
        data = {}
        if not os.path.exists(path):
            if self.get_verbose():
                print("Could not locate config file at {}.".format(path))
            return data

        config = configparser.ConfigParser()
        config.read(path)

        if 'Application' in config:
            if 'Verbose' in config['Application']:
                data['verbose'] = config['Application'].getboolean('Verbose')
            if 'ThreadDelay' in config['Application']:
                data['threaddelay'] = config['Application'].getfloat('ThreadDelay')
            if 'KeyboardControl' in config['Application']:
                data['keyboardcontrol'] = config['Application'].getboolean('KeyboardControl')
            if 'StatusLed' in config['Application']:
                data['statusled'] = config['Application'].getint('StatusLed')

        if 'Media' in config:
            if 'Local' in config['Media']:
                data['localmedia'] = config['Media']['Local']
            if 'Storage' in config['Media']:
                data['storagemedia'] = config['Media']['Storage']
            if 'Mount' in config['Media']:
                data['storagemount'] = config['Media']['Mount']
            if 'Preload' in config['Media']:
                data['preloadmedia'] = config['Media'].getboolean('Preload')

        if 'Audio' in config:
            if 'Device' in config['Audio']:
                data['audiodevice'] = config['Audio']['Device']
            if 'BufferSize' in config['Audio']:
                data['buffersize'] = config['Audio'].getint('BufferSize')
            if 'BufferPreload' in config['Audio']:
                data['bufferpreload'] = config['Audio'].getint('BufferPreload')

        if 'Midi' in config:
            if 'InDevice' in config['Midi']:
                data['midiindevice'] = config['Midi']['InDevice']
            if 'InChannel' in config['Midi']:
                data['midiinchannel'] = config['Midi'].getint('InChannel')
            if 'OutDevice' in config['Midi']:
                data['midioutdevice'] = config['Midi']['OutDevice']
            if 'OutChannel' in config['Midi']:
                data['midioutchannel'] = config['Midi'].getint('OutChannel')
            if 'SerialPort' in config['Midi']:
                data['serialport'] = config['Midi']['SerialPort']

        return data
