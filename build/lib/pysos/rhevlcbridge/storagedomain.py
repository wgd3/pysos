'''
Created on Dec 27, 2013

@author: wallace
'''

class StorageDomain():
	'''
	This class will represent hosts in an environment
	'''
	
	uuid = ""
	name = ""
	storage_type = ""
	master = False
	
	def __init__(self, csvList):
		'''
		This constructor assumes it is being passed a comma separated list consisting of all elements in a line from the dat file
		'''
		details = csvList
		#print details
		if len(details) > 2:
			self.uuid = details[0]
			self.name = details[2]
			#print self.name
			# determine storage medium
			self.storage_type = details[4]
			if self.storage_type == "0":
				self.storage_type = "unknown"
			elif self.storage_type == "1":
				self.storage_type = "NFS"
			elif self.storage_type == "2":
				self.storage_type = "FCP"
			elif self.storage_type == "3":
				self.storage_type = "iSCSI"
			self.master = False
			if details[3] == "0":
				self.master = True					

	def get_uuid(self):
		return self.uuid


	def get_name(self):
		return self.name


	def get_storage_type(self):
		return self.storage_type

	def get_master(self):
		return self.master


	def set_uuid(self, value):
		self.__uuid = value


	def set_name(self, value):
		self.__name = value


	def set_storage_type(self, value):
		self.__storage_type = value


	def set_master(self, value):
		self.__master = value


	def del_uuid(self):
		del self.__uuid


	def del_name(self):
		del self.__name


	def del_storage_type(self):
		del self.__storage_type


	def del_master(self):
		del self.__master

	uuid = property(get_uuid, set_uuid, del_uuid, "uuid's docstring")
	name = property(get_name, set_name, del_name, "name's docstring")
	storage_type = property(get_storage_type, set_storage_type, del_storage_type, "storage_type's docstring")
	master = property(get_master, set_master, del_master, "master's docstring")

		