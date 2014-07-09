from config import colors 
from opsys import *


def get_rhevm_info(target, check_db):
	# grab / print basic information first
	print colors.SECTION + colors.BOLD + "RHEV-M Information" + colors.ENDC
	print '\n'

	# Find RHEVM rpm
	rhevm_ver = find_rpm(target, "rhevm-3")
	print colors.HEADER_BOLD + "\t Version: " + colors.CYAN+ rhevm_ver + colors.ENDC
	
	rhevm_check = check_rpm_ver(rhevm_ver)

	if rhevm_check:
		print colors.RED + colors.BOLD + '\n\t WARNING : ' + colors.ENDC + '{} : {}'.format(rhevm_ver[0:(rhevm_ver.find('.el'))],rhevm_check)
	
	# Find simplified version for debug purposes
	if "-3.0" in rhevm_ver:
		simpleVer = "3.0"
	elif "-3.1" in rhevm_ver:
		simpleVer = "3.1"
	elif "-3.2" in rhevm_ver:
		simpleVer = "3.2"
	else:
		simpleVer = "Could not be found" 
	
	# Try to find database
	database = False
	fullPath = os.path.abspath(target)
	
	lcRoot = os.path.dirname(fullPath)
	
	if os.path.isdir(lcRoot + "/database"):
		database = True
		dbDir = lcRoot + "/database"
		
	# The following is only possible if we found the db above
	if database:
		print colors.HEADER_BOLD + "\t Database: " + colors.ENDC +"Found. Can give database overview with --db"

		# Find errors first
		parse_manager_logs(target)

		if check_db:	
			
			# Compensate for 3.0 / 3.x database differences
			if simpleVer == "3.1" or simpleVer == "3.2":
				# Eval manager before moving on to db analysis
				rhev_eval_db(dbDir)
			elif simpleVer == "3.0":
				print colors.WARN + "\t Not ready to parse 3.0 databases yet, may not be trustworthy!!" + colors.ENDC
			else:
				print colors.WARN + "\t Database version could not be found without RPM information." + colors.ENDC
				rhev_eval_db(dbDir)
		else:
			pass	
		
	else:
		print colors.WARN + "Database not found" + colors.ENDC
		
		# Find errors first
		parse_manager_logs(target)
	
	
# Method for evaluating the database for env information
# This method should expect to be passed the directory containing the database
def rhev_eval_db(dbDir):
	
	
	if os.path.exists(dbDir + "/sos_pgdump.tar"):
		dbTar = dbDir + "/sos_pgdump.tar"
		
		
		masterDB = Database(dbTar)
		
		# create DC list
		dc_list = masterDB.get_data_centers()
		
		print ""
		print colors.SECTION + colors.BOLD + "RHEV Database Information" + colors.ENDC
		print ""
		
		print '\n\t' + colors.BOLD + colors.GREEN + '[Data Centers Managed By RHEV-M]' + colors.ENDC 
		dc_table = Table(dc_list,"name","uuid","compat")
		dc_table.display()
		
				
		####### End of Data Center Parsing #######
		
		print '\n\t' + colors.BOLD + colors.GREEN + '[Storage Domains In All Data Centers]' + colors.ENDC
		sd_list = masterDB.get_storage_domains()
		sd_table = Table(sd_list,"name","uuid","storage_type","master")
		sd_table.display()
		


	####### End of Storage Domain Parsing ######
		
		# Generating clusters for host reference
		cluster_list = masterDB.get_clusters()
		
		host_list = masterDB.get_hosts()

		hostDirs = []
		hostNameLen = 5
		# look for all files in the parent of the passed 'dbDir', and if it is a dir then attempts to parse
		rootDir = os.path.dirname(dbDir)
		
		for d in os.listdir(rootDir):
			
			if os.path.isdir(rootDir+"/"+d):
				hostDirs.append(d)
				
		
		
		for h in host_list:
			for d in dc_list:
				if h.get_uuid() == d.get_spm_uuid():
					h.set_spm_status(True)
				else:
					h.set_spm_status(False)

			for c in cluster_list:
				if c.get_uuid() == h.get_host_dc_uuid():
					
					for d in dc_list:
						
						if c.get_dc_uuid() == d.get_uuid():
							h.set_host_dc_name(d.get_name())
							
					
			# try and find release version
			hostDirName = h.get_name().split(".")
		
			for dir in hostDirs:
				
				names = dir.split("-")

				if names[0] == hostDirName[0]:
				
					# this is a stupid hack, using '..' in the path name. stop being lazy and find a better alternative
					releaseFile = open(dbDir+"/../"+dir+"/etc/redhat-release")
					releaseVer = releaseFile.readlines()
					if "Hypervisor" in releaseVer[0]:
						host_release = releaseVer[0].split("(")[1]
						# strip the newline character at the end of the line
						host_release = host_release.replace("\n","")
						host_release = host_release.rstrip(")")
						h.set_release_ver(host_release)
					else:
						host_release = releaseVer[0].split()[6]
						h.set_release_ver(host_release)
		

		print '\n\t' + colors.BOLD + colors.GREEN + '[Hypervisors In All Data Centers]' + colors.ENDC
		host_table = Table(host_list,"name","uuid","host_dc_name","host_type", "release_ver", "spm_status")
		host_table.display()
		
		
	else:
		print colors.WARN + "Could not find a database file"
		
# Finds relevant files after dbdump has been extracted
def findDat(table,restFile):
	'''
	Subroutine to find the dat file name in restore.sql
	''' 
	openFile = open(restFile, "r")
	lines = openFile.readlines()
	

	
	for n in lines:
		if n.find(table) != -1:
			if n.find("dat") != -1:
				datInd = n.find("PATH")
				datFileName =  n[datInd+7:datInd+15]
				if datFileName.endswith("dat"):
				
					return datFileName
	
def parse_manager_logs(target):
	'''
	The plan here is to grab the most recent errors from engine.log/rhevm.log, messages, server.log(maybe) and present them in a readable fashion
	
	Passing the parsing duties (heh, duties) to functions to keep things relatively modular
	'''
		
	# grab / print basic information first
	print ""
	print colors.SECTION + colors.BOLD + "Log Files" + colors.ENDC
	print ""
	
	# Gather main log files
	try:
		#print colors.WARN + "\t " + target + "/var/log/ovirt-engine/engine.log"
		engine_log = open(target+"var/log/ovirt-engine/engine.log")
		print colors.WHITE + '\t [engine.log error parsing]' + colors.ENDC
		parse_engine_log(engine_log)
	except IOError:
		print colors.WARN + "\t Could not open the engine.log file" + colors.ENDC
	
	### Holding off on implementing  this for the manager, as we do not often see useful information here
# 	try:
# 		messages_log = open(target+"var/log/messages")
# 		print colors.PURPLE + "\t /var/log/messages: " + colors.GREEN + "loaded"
# 		parse_messages_log(messages_log)
# 	except IOError:
# 		print colors.WARN + "\t Could not open /var/log/messages file"
		
def parse_engine_log(logFile):
	'''
	Goal: Find the most recent error line with verbose information, split it up, and present it
	'''
	
	# Find most recent error line
	lines = logFile.readlines()
	errorLines = []
	for line in lines:
		if "ERROR" in line:

			errorLines.append(line)
	print ''
	
	for x in range(1,4):
		try:
			lastLine = len(errorLines)-x
			errorLine = errorLines[lastLine]
			errorProperties = errorLine.split(" ")
			'''
			0 - Date
			1 - Time
			3 - Command run
			7+ - Message
			'''
			
			print colors.HEADER_BOLD + "\t Time Stamp: " + colors.ENDC + errorProperties[0] + " " + errorProperties[1]	
			print colors.HEADER_BOLD + "\t Command: " + colors.ENDC + errorProperties[3].lstrip("[").rstrip("]")
			
			# Trying to hack this since messages seem to vary in length - basing on last capital letter. deal with it
			errMessParts =  errorProperties[7:]
			errorMessage = ""
			for p in errMessParts:
				#print p
				for c in p:
					if c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
						#print errMessParts.index(p)
						index = errMessParts.index(p)
						errorMessage = ' '.join(errMessParts[index:]).replace("\n","")
						#print errorMessage
				
			print colors.HEADER_BOLD + "\t Message: " + colors.ENDC  + errorMessage
		
			singleOccurance = True
			occurances = 0
			for line in lines:
				if ' '.join(errorProperties[7:]) in line:
					occurances += 1
			if occurances > 1:
				singleOccurance = False
			
			if singleOccurance:
				print colors.HEADER_BOLD + "\t Only occurance of this error: " + colors.WHITE + "Yes" + colors.ENDC
			else:
				print colors.HEADER_BOLD + "\t Only occurance of this error: " + colors.ENDC + colors.RED + "No. Errors appear " + str(occurances) + " times in engine.log starting at " + ' '.join(errorLines[0].split(" ")[0:2]) + colors.ENDC
				
			print ""
		
		except:
			pass

def parse_messages_log(logFile):
	print ""
