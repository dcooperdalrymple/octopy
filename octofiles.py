import os
import subprocess

class OctoFile:
	def __init__(self, path):
		self.dir = os.path.dirname(path)
		self.name = os.path.splitext(os.path.basename(path))[0]
		self.wavepath = self.find_wave()
		self.midipath = self.find_midi()

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

	def get_type(self):
		if self.has_wave() and self.has_midi():
			return "WAV+MID"
		elif self.has_wave():
			return "WAV"
		elif self.has_midi():
			return "MID"
		else:
			return "NONE"

	def get_description(self):
		return "{} {} (found in '{}')".format(self.name, self.get_type(), self.dir)

	def has_wave(self):
		return self.wavepath != False

	def has_midi(self):
		return self.midipath != False

class OctoFiles:
	def __init__(self, dirpath):
		self.path = dirpath
		self.files = []
		self.__locate_files()

	def __add_file(self, path):
		if path.endswith(".wav") or path.endswith(".mid"):
			file = OctoFile(path)
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

	def print(self):
		if not self.files:
			print("No audio files were found.\n")
			return

		print("Available Song Files:")
		for i in range(len(self.files)):
			print("  {:d}: {}".format(i+1, self.files[i].get_description()))
		print()

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
		for (dirpath, dirnames, filenames) in os.walk(self.mount):
			for x in filenames:
				if x.endswith(".wav") or x.endswith(".mid"):
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
