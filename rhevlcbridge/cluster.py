'''
Created on Dec 27, 2013

@author: wallace
'''

class Cluster():
	'''
	This class will represent hosts in an environment
	'''
	
	uuid = ""
	name = ""
	cpu_type = ""
	dc_uuid = ""
		
	def __init__(self, csvList):
		'''
		This constructor assumes it is being passed a comma separated list consisting of all elements in a line from the dat file
		'''
		details = csvList
		if len(details) > 2:
			self.uuid = details[0]
			self.name = details[1]
			self.cpu_type = details[3]
			self.dc_uuid = details[10]
			
	def get_test(self):
		return self.dc_uuid

	def get_dc_uuid(self):
		return self.dc_uuid


	def set_dc_uuid(self, value):
		self.__dc_uuid = value


	def del_dc_uuid(self):
		del self.__dc_uuid


	def get_uuid(self):
		return self.uuid


	def get_name(self):
		return self.name


	def get_cpu_type(self):
		return self.cpu_type


	def set_uuid(self, value):
		self.uuid = value


	def set_name(self, value):
		self.name = value


	def set_cpu_type(self, value):
		self.cpu_type = value


	def del_uuid(self):
		del self.uuid


	def del_name(self):
		del self.name


	def del_cpu_type(self):
		del self.cpu_type

	uuid = property(get_uuid, set_uuid, del_uuid, "uuid's docstring")
	name = property(get_name, set_name, del_name, "name's docstring")
	cpu_type = property(get_cpu_type, set_cpu_type, del_cpu_type, "cpu_type's docstring")
	dc_uuid = property(get_dc_uuid, set_dc_uuid, del_dc_uuid, "dc_uuid's docstring")
	
		


		