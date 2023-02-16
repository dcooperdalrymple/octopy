import os
import subprocess

import wave
from mido import MidiFile

class OctoFile:
    def __init__(self, path, settings = False):
        self.dir = os.path.dirname(path)
        self.name = os.path.splitext(os.path.basename(path))[0]
        self.settings = settings

        self.wavepath = self.find_wave()
        self.wavefile = False

        self.midipath = self.find_midi()
        self.midifile = False
        self.midimsgs = False
        self.midilength = 0

        self.videopath = self.find_video()

    def find_wave(self):
        path = os.path.join(self.dir, self.name + '.wav')
        if os.path.isfile(path):
            return path
        return False

    def find_midi(self):
        path = os.path.join(self.dir, self.name + '.mid')
        if os.path.isfile(path):
            return path
        return False

    def find_video(self):
        exts = ['avi', 'mov', 'mkv', 'mp4', 'm4v']
        for ext in exts:
            path = os.path.join(self.dir, self.name + '.' + ext)
            if os.path.isfile(path):
                return path
        return False

    def get_type(self):
        types = []
        if self.has_wave():
            types.append("WAV")
        if self.has_midi():
            types.append("MID")
        if self.has_video():
            types.append("VID")
        if not types:
            return "NONE"
        return "+".join(types)

    def get_description(self):
        return "{} {} (found in '{}')".format(self.name, self.get_type(), self.dir)

    def has_wave(self):
        return self.wavepath != False
    def is_wave_loaded(self):
        return self.has_wave() and self.wavefile

    def has_midi(self):
        return self.midipath != False
    def is_midi_loaded(self):
        return self.has_midi() and self.midifile and self.midimsgs

    def has_video(self):
        return self.videopath != False
    def is_video_loaded(self):
        return self.has_video()

    def load(self):
        if self.has_wave():
            filepath = os.path.abspath(self.wavepath)
            try:
                self.wavefile = wave.open(filepath, 'rb')
            except Exception:
                if self.settings and self.settings.get_verbose():
                    print('Unable to open wave file: {}.'.format(filepath))
                self.wavefile = False
                return False

        if self.has_midi():
            filepath = os.path.abspath(self.midipath)
            try:
                self.midifile = MidiFile(filepath)
            except Exception:
                if self.settings and self.settings.get_verbose():
                    print('Unable to open midi file: {}.'.format(filepath))
                self.midifile = False
                self.midimsgs = False
                return False

            self.midimsgs = []
            for msg in self.midifile:
                self.midimsgs.append(msg)

            self.midilength = self.midifile.length

        if self.has_video():
            # OMX will handle video, don't need to load manually
            pass

        return True

class OctoFiles:
    def __init__(self, settings):
        self.settings = settings
        self.path = os.path.expanduser(self.settings.get_localmedia())
        self.files = []
        self.__locate_files()

    def __add_file(self, path):
        exts = ['wav', 'mid', 'avi', 'mov', 'mkv', 'mp4', 'm4v']
        for ext in exts:
            if path.endswith("." + ext):
                file = OctoFile(path, self.settings)
                for f in self.files:
                    if f.name == file.name:
                        return
                self.files.append(file)

    def __locate_files(self):
        for (dirpath, dirnames, filenames) in os.walk(self.path):
            for filename in sorted(filenames):
                self.__add_file(os.path.join(dirpath, filename))
            break

    def append(self, files):
        if files:
            for path in files:
                self.__add_file(path)

    def getfiles(self):
        if not self.files:
            return False
        else:
            return self.files

    def loadfiles(self):
        if not self.files:
            return False

        if self.settings.get_verbose():
            print("Preloading media files:")
        i = 0
        for file in self.files:
            i += 1
            if file.load() and self.settings.get_verbose():
                print("  {:d}: {} ({}): Successfully loaded.".format(i, file.name, file.get_type()))
            elif self.settings.get_verbose():
                print("  {:d}: {} ({}): Failed to load.".format(i, file.name, file.get_type()))
        if self.settings.get_verbose():
            print()

        return True

    def print(self):
        if not self.files:
            print("No song files were found.\n")
            return

        print("Available Song Files:")
        for i in range(len(self.files)):
            print("  {:d}: {}".format(i+1, self.files[i].get_description()))
        print()

    def sort(self):
        self.files.sort(key=lambda x: x.name, reverse=False)
        return True

class OctoUsb:
    def __init__(self, settings):
        self.media = settings.get_storagemedia()
        self.mount = settings.get_storagemount()
        self.files = []
        self.found = self.__check_media()
        if self.found:
            self.__mount_media()
            self.__list_files()

    def __check_media(self):
        output = subprocess.Popen("lsblk -o name -n -s -l", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        for out in output.stdout:
            if self.media in str(out):
                return True

        return False

    def __mount_media(self):
        if not os.path.exists(self.mount):
            os.makedirs(self.mount)
        elif os.path.ismount(self.mount):
            subprocess.call("umount " + self.mount, shell=True)
        subprocess.call("mount /dev/" + self.media + " " + self.mount, shell=True)
        return True

    def __list_files(self):
        exts = ['wav', 'mid', 'avi', 'mov', 'mkv', 'mp4', 'm4v']
        for (dirpath, dirnames, filenames) in os.walk(self.mount):
            for x in filenames:
                for ext in exts:
                    if x.endswith("." + ext):
                        self.files.append(os.path.join(dirpath, x))
            break
        return True

    def getpath(self):
        if self.found:
            return self.mount
        else:
            return False

    def getfiles(self):
        if not self.files:
            return False
        else:
            return self.files
