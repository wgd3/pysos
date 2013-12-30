'''
Created on Dec 27, 2013

@author: wallace
'''

class DataCenter():
	'''
	This class will represent hosts in an environment
	'''
	
	uuid = ""
	name = ""
	compat = ""
	spm_name = ""
	
	def __init__(self, csvList):
		'''
		This constructor assumes it is being passed a comma separated list consisting of all elements in a line from the dat file
		'''
		details = csvList
		if len(details) > 2:
			self.uuid = details[0]
			self.name = details[1]
			self.compat = details[8]
			self.spm_name = details[7]

	def get_uuid(self):
		return self.uuid


	def get_name(self):
		return self.name
		

	def get_compat(self):
		return self.compat


	def get_spm_name(self):
		return self.spm_name


	def set_uuid(self, value):
		self.uuid = value


	def set_name(self, value):
		self.name = value


	def set_compat(self, value):
		self.compat = value


	def set_spm_name(self, value):
		self.spm_name = value


	def del_uuid(self):
		del self.uuid


	def del_name(self):
		del self.name


	def del_compat(self):
		del self.compat


	def del_spm_name(self):
		del self.spm_name

	uuid = property(get_uuid, set_uuid, del_uuid, "uuid's docstring")
	name = property(get_name, set_name, del_name, "name's docstring")
	compat = property(get_compat, set_compat, del_compat, "compat's docstring")
	spm_name = property(get_spm_name, set_spm_name, del_spm_name, "spm_name's docstring")
						

	