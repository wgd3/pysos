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
		details = []
		
		for d in csvList:
			details.append(d)
		
		self.uuid = details[0]
		self.name = details[2]
		self.compat = details[8]
		self.spm_name = details[7]

	def get_uuid(self):
		return self.__uuid


	def get_name(self):
		return self.__name


	def get_compat(self):
		return self.__compat


	def get_spm_name(self):
		return self.__spm_name


	def set_uuid(self, value):
		self.__uuid = value


	def set_name(self, value):
		self.__name = value


	def set_compat(self, value):
		self.__compat = value


	def set_spm_name(self, value):
		self.__spm_name = value


	def del_uuid(self):
		del self.__uuid


	def del_name(self):
		del self.__name


	def del_compat(self):
		del self.__compat


	def del_spm_name(self):
		del self.__spm_name

	uuid = property(get_uuid, set_uuid, del_uuid, "uuid's docstring")
	name = property(get_name, set_name, del_name, "name's docstring")
	compat = property(get_compat, set_compat, del_compat, "compat's docstring")
	spm_name = property(get_spm_name, set_spm_name, del_spm_name, "spm_name's docstring")
						

	