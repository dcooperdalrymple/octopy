# Copyright 2015 Adafruit Industries.
# Author: Tony DiCola
# Updated: 2023-02-16 by Cooper Dalrymple
# License: GNU GPLv2

import os
import shutil
import subprocess
import time

class OMXPlayer:

    def __init__(self, settings = None):
        """Create an instance of a video player that runs omxplayer in the
        background.
        """
        self.process = None
        self.settings = settings
        self.extensions = ['avi', 'mov', 'mkv', 'mp4', 'm4v']

        if self.settings is not None and self.settings.get_verbose():
            print("Using OMXPlayer video player.")

    def get_extensions(self):
        return self.extensions

    def play(self, path):
        """Play the provided movie file, optionally looping it repeatedly."""
        self.stop(3)  # Up to 3 second delay to let the old player stop.
        # Assemble list of arguments.
        args = ['omxplayer']
        args.append('--loop')
        args.append(path)

        # Run omxplayer process and direct standard output to /dev/null.
        self.process = subprocess.Popen(args, stdout=open(os.devnull, 'wb'), close_fds=True)

    def is_playing(self):
        """Return true if the video player is running, false otherwise."""
        if self.process is None:
            return False
        self.process.poll()
        return self.process.returncode is None

    def stop(self, block_timeout_sec=0):
        """Stop the video player.  block_timeout_sec is how many seconds to
        block waiting for the player to stop before moving on.
        """
        # Stop the player if it's running.
        if self.process is not None and self.process.returncode is None:
            # There are a couple processes used by omxplayer, so kill both
            # with a pkill command.
            subprocess.call(['pkill', '-9', 'omxplayer'])
        # If a blocking timeout was specified, wait up to that amount of time
        # for the process to stop.
        start = time.time()
        while self.process is not None and self.process.returncode is None:
            if (time.time() - start) >= block_timeout_sec:
                break
            time.sleep(0)
        # Let the process be garbage collected.
        self.process = None

    @staticmethod
    def exists():
        return shutil.which('omxplayer') is not None
