import os
import shutil
import subprocess
import time

class VideoPlayer:

    def __init__(self, settings = None):
        self.path = None
        self.settings = settings

        if self.settings is not None and self.settings.get_verbose():
            print("Using {} video player.\n".format(self.__class__.__name__))

    def load(self, path):
        if not self.exists():
            return False
        self.path = path
        return True

    def is_loaded(self):
        return self.path is not None

    def play(self):
        return self.is_loaded()

    def is_playing(self):
        return self.is_loaded()

    def stop(self, clear=True):
        # Stop the video player. timeout is how many seconds to block waiting for the player to stop before moving on.
        if clear:
            self.path = None
        return True

    @staticmethod
    def get_extensions(self):
        return []

    @staticmethod
    def exists():
        return True

class VideoPlayerProcess(VideoPlayer):

    def __init__(self, settings = None):
        self.process = None
        super().__init__(settings)

    def load(self, path):
        self.stop(self.get_default_timeout())
        super().load(path)

    def play(self):
        if not super().play():
            return False

        self.stop(self.get_default_timeout(), False)

        # Run process and direct standard output to /dev/null
        self.process = subprocess.Popen(self.get_arguments(), stdout=open(os.devnull, 'wb'), close_fds=True)

        return True

    def get_arguments(self):
        args = [self.get_command()]
        args.append(self.path)
        return args

    def is_playing(self):
        if self.process is None:
            return False
        self.process.poll()
        return self.process.returncode is None

    def stop(self, timeout=0, clear=True):
        # Stop the video player. timeout is how many seconds to block waiting for the player to stop before moving on.

        # Stop the player if it's running.
        if self.process is not None and self.process.returncode is None:
            subprocess.call(['pkill', '-9', self.get_command()])

        # If a blocking timeout was specified, wait up to that amount of time for the process to stop.
        start = time.time()
        while self.process is not None and self.process.returncode is None:
            if (time.time() - start) >= timeout:
                break
            time.sleep(0)

        # Let the process be garbage collected.
        self.process = None

        return super().stop(clear)

    @staticmethod
    def get_command():
        pass

    @staticmethod
    def get_default_timeout():
        return 3

    @classmethod
    def exists(cls):
        return shutil.which(cls.get_command()) is not None
