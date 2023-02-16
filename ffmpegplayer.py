import os
import shutil
import subprocess
import time

class FFmpegPlayer:

    def __init__(self, settings = None):
        """Create an instance of a video player that runs ffplay from ffmpeg in the
        background.
        """
        self.process = None
        self.settings = settings
        self.extensions = ['avi', 'mov', 'mkv', 'mp4', 'm4v']

        if self.settings is not None and self.settings.get_verbose():
            print("Using FFmpeg video player.")

    def get_extensions(self):
        return self.extensions

    def play(self, path):
        """Play the provided movie file, optionally looping it repeatedly."""
        self.stop(3) # Up to 3 second delay to let the old player stop.

        # Assemble list of arguments.
        args = ['ffplay']
        args.append('-fs') # Fullscreen
        args.append('-an') # Disable audio
        args.append('-sn') # Disable subtitles
        args.append('-noborder') # Borderless window
        args.extend(['-loop', '0']) # Loop forever
        args.extend(['-loglevel', 'quiet']) # Disable verbose output
        args.append(path)

        # Run ffplay process and direct standard output to /dev/null.
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
            subprocess.call(['pkill', '-9', 'ffplay'])
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
        return shutil.which('ffplay') is not None
