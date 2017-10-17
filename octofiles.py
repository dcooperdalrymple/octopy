import os
import subprocess

class OctoFiles:
	def __init__(self, dirpath):
		self.path = dirpath
		self.files = []
		self.__locate_files()

	def __locate_files(self):
		for (dirpath, dirnames, filenames) in os.walk(self.path):
			for x in filenames:
				if x.endswith(".wav"):
					self.files.append(os.path.join(dirpath, x))
			break

	def append(self, add_files):
		if add_files:
			self.extend(add_files)

	def getfiles(self):
		if not self.files:
			return False
		else:
			return self.files

class OctoUsb:
	def __init__(self, storagemedia):
		self.media = storagemedia
		self.mount = "~/thumb"
		self.files = []
		self.found = self.__check_media()
		if self.found:
			self.__mount_media()
			self.__list_files()

	def __check_media(self):
		output = subprocess.Popen("lsblk -o name -n -s -l", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

		for out in output.stdout:
			if self.media in out:
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
				if x.endswith(".wav"):
					self.files.append(os.path.join(dirpath, x))
			break
		return True

	def getpath():
		if self.found:
			return self.mount
		else:
			return False

	def getfiles():
		if not self.files:
			return False
		else:
			return self.files
