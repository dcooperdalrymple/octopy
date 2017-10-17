import os
import subprocess

class OctoFiles:
	def __init__(self, storagemedia):
		self.media = storagemedia
		self.mount = "~/thumb"
		self.files = []
		if self.__check_media():
			self.__mount_media()
			self.__list_files()

	def __check_media(self):
		output = subprocess.Popen("lsblk -o name -n -s -l", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

		for out in output.stdout:
			print out
			if self.media in out:
				return True

		return False

	def __mount_media(self):
		if not os.path.exists(self.mount):
			os.makedirs(self.mount)
		else:
			subprocess.call("umount " + self.mount, shell=True)
		subprocess.call("mount /dev/" + self.media + " " + self.mount, shell=True)
		return True

	def __list_files(self):
		for (dirpath, dirnames, filenames) in os.walk(self.mount):
			for x in filenames:
				print x
				if x.endswith(".wav"):
					self.files.append(os.path.join(dirpath, x));
			break;
		print self.files
		return True
