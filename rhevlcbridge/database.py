'''
Created on Dec 27, 2013

@author: wallace
'''
import tarfile, os
from rhevlcbridge.host import Host # Surely there is a better way to do this
from rhevlcbridge.storagedomain import StorageDomain
from rhevlcbridge.datacenter import DataCenter


class Database():
	'''
	This class should be created by passing the sos_pgdump.tar file to it
	
	It will serve the purpose of pulling information from the tar file without the need to upload to a dbviewer
	'''

	''' Start declaring variables for the class'''
	dbDir = ""
	tarFile = ""
	dat_files = [] # this is a list for all the wanted dat files
	data_centers = []
	storage_domains = []
	hosts = []

	def __init__(self, dbFile):
		'''
		Constructor
		'''
		self.dbDir = os.path.dirname(dbFile)+"/"
		tarFile = tarfile.open(dbFile)
		self.unpack(tarFile, self.dbDir)
		
		# Now that we're unpacked, move on to gathering information
		self.data_centers = self.gatherDataCenters()
		self.storage_domains = self.gatherStorageDomains()
		self.hosts = self.gatherHosts()

	def get_data_centers(self):
		return self.data_centers


	def get_storage_domains(self):
		return self.storage_domains


	def get_hosts(self):
		return self.hosts


	
	def unpack(self, tarFile, dbDir):
		# Start with extraction
		#print "Extracting..."
		tarFile.extractall(dbDir)
		
		# then set most of the needed variables for future functions
		#print "Setting dat files..."
		self.dat_files = ["data_center_dat",
					 "storage_domain_dat",
					 "host_dat"]
		
		#print self.dat_files[0]
		self.dat_files[0] = self.dat_files[0] +","+ self.findDat(" storage_pool ", dbDir+"restore.sql")
		#print "Found dat file: " + self.dat_files[0]
		#print "Passing this to the function: " + self.dat_files[0].split(",")[1]
		self.dat_files[1] = self.dat_files[1] +","+ self.findDat(" storage_domain_static ", dbDir+"restore.sql")
		self.dat_files[2] = self.dat_files[2] +","+ self.findDat(" vds_static ", dbDir+"restore.sql")	
		
		
	def findDat(self,table,restFile):
		'''
		Subroutine to find the dat file name in restore.sql
		''' 
		openFile = open(restFile, "r")
		lines = openFile.readlines()
	
		# print "Looking for " + table
	
		for n in lines:
			if n.find(table) != -1:
				if n.find("dat") != -1:
					datInd = n.find("PATH")
					datFileName =  n[datInd+7:datInd+15]
					if datFileName.endswith("dat"):
						#print "Found dat line for " + table
						#logging.warning('Return dat file: ' +datFileName)
						return datFileName
	


	def gatherDataCenters(self):
		'''
		This method returns a list of comma-separated details of the Data Center
		'''
		dc_list = []
		#print self.dbDir
		#print self.dat_files[0]
		dat_file = self.dbDir+self.dat_files[0].split(",")[1]
		openDat = open(dat_file,"r")
		
		lines = openDat.readlines()		
		
		for l in lines:
			if len(l.split("\t")) > 1:
				newDC = DataCenter(l.split("\t"))
				dc_list.append(newDC)
			
		openDat.close()
		return dc_list
	
	def gatherStorageDomains(self):
		'''
		This method returns a list of comma-separated details of the Storage Domains
		'''
		sd_list = []
		dat_file = self.dbDir+self.dat_files[1].split(",")[1]
		#print dat_file
		openDat = open(dat_file,"r")
		
		lines = openDat.readlines()
		
		for l in lines:
			if len(l.split("\t")) > 1:
				#print "Line: " + l
				newSD = StorageDomain(l.split("\t"))
				sd_list.append(newSD)
			
		openDat.close()
		return sd_list
	
	def gatherHosts(self):
		'''
		This method returns a list of comma-separated details of the Data Center
		'''
		host_list = []
		dat_file = self.dbDir+self.dat_files[2].split(",")[1]
		#print dat_file
		openDat = open(dat_file,"r")
		
		lines = openDat.readlines()
		
		for l in lines:
			if len(l.split("\t")) > 1:
				newHost = Host(l.split("\t"))
				#print "New Host Name: " + newHost.get_name()
				host_list.append(newHost)
			
		openDat.close()
		return host_list
	
	
	data_centers = property(get_data_centers, None, None, None)
	storage_domains = property(get_storage_domains, None, None, None)
	hosts = property(get_hosts, None, None, None)
	
	