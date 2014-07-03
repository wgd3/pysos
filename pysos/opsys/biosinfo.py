import os, re
from config import *

def parse_dmi(dmifile, to_check):
	with open(dmifile, 'r') as dfile:
		handle_regex = re.compile('^%s\s'%to_check)
		newline = re.compile('^$')
		lines = dfile.readlines()
		for x in range(0,len(lines)):
			line = lines[x]
			if handle_regex.findall(line):
				
			# Found header for section
				section = {}
				section['info'] = [] 
				while True:
					line = lines[x+1]
			# repeat until we hit newline
					  
					if not newline.findall(line):
						 section['info'].append(line.strip().strip('\t'))
						 x += 1
					else:
						break
					
				info = {}
				for item in section['info']:
					try:
						key = item.split(':')[0]
						value = item.split(':')[1]
						info[key] = value
					except:
						pass
				return info


def get_bios_info(target, local):
	total_cores = 0
	total_threads = 0
	cpus_populated = 0
	mem_arrays = 0
	total_mem = 0
	dimm_count = 0
	empty_dimms = 0
	core_count = 0
	thread_count = 0
	if local:
		import tempfile, subprocess
		temp_file = tempfile.NamedTemporaryFile(delete=False)
		command = subprocess.Popen(['dmidecode'], stdout=subprocess.PIPE)
		output = command.stdout.read()
		for line in output:
			temp_file.write(line)
		temp_file.close()
		dmi_file = temp_file.name
	else:
		dmi_file = target + 'dmidecode'
	
	if os.path.isfile(dmi_file):
		# first get the static information
		
		bios_info = parse_dmi(dmi_file, 'BIOS')
		sys_info = parse_dmi(dmi_file, 'System')
		cpu_info = parse_dmi(dmi_file, 'Processor')
		
		bios_vendor = bios_info['Vendor']
		bios_date = bios_info['Release Date']
		bios_ver = bios_info['Version']
		
		sys_vendor = sys_info['Manufacturer']
		sys_type = sys_info['Product Name']
		sys_uuid = sys_info['UUID']
		
		cpu_family = cpu_info['Family']
		cpu_ver = cpu_info['Version']
		
		with open(dmi_file, 'r') as dfile:
			# main iterables that have distinct leading names
			for line in dfile:
				if 'Thread Count:' in line:
					total_threads += int(line.split()[2])
					thread_count = line.split()[2]
				if 'Core Count:' in line:
					total_cores += int(line.split()[2])
					core_count = line.split()[2]
				if 'Maximum Capacity:' in line:
					index = line.find(':')
					max_mem = line[index+1:len(line)].strip()
				if 'Number Of Devices:' in line:
					dimm_count += int(line.split()[3])
				if re.match('\tSize:', line):
					if 'No Module Installed' in line:
						empty_dimms += 1
					else:
						size = int(line.split()[1])
						total_mem += size
				if 'Status: Populated' in line:
					cpus_populated += 1
				if 'Current Speed' in line:
					cpu_freq = line.split()[2]
				if 'Physical Memory Array' in line:
					mem_arrays +=  1
						
		mem_max_format = int((int(max_mem.split()[0]) * mem_arrays))
		if mem_max_format >= 1024:
			mem_max_format = str((mem_max_format / 1024)) + ' TB'
		else:
			mem_max_format = str(mem_max_format) + ' GB'				
		print colors.SECTION + 'DMI Decode' + colors.ENDC
		print '\t' + colors.HEADER_BOLD + 'BIOS' + colors.ENDC
		print '\t\t' + colors.BLUE + 'Vendor  : ' + colors.ENDC + bios_vendor
		print '\t\t' + colors.BLUE + 'Version : ' + colors.ENDC + bios_ver
		print '\t\t' + colors.BLUE + 'Release : ' + colors.ENDC + bios_date
		print '\t' + colors.HEADER_BOLD + 'System' + colors.ENDC
		print '\t\t' + colors.BLUE + 'Vendor  : ' + colors.ENDC + sys_vendor
		print '\t\t' + colors.BLUE + 'Server  : ' + colors.ENDC + sys_type
		print '\t\t' + colors.BLUE + 'UUID    : ' + colors.ENDC + sys_uuid
		print '\t' + colors.HEADER_BOLD + 'CPU' + colors.ENDC
		print '\t\t' + colors.WHITE + '{} CPU sockets populated, {} cores / {} threads per core'.format(cpus_populated, core_count, thread_count) + colors.ENDC
		print '\t\t' + colors.WHITE + '{} total cores - {} total threads'.format(total_cores, total_threads) + colors.ENDC
		print '\t\t' + colors.BLUE + 'Family  : ' + colors.ENDC + cpu_family
		print '\t\t' + colors.BLUE + 'Clock   :  ' + colors.ENDC + cpu_freq 
		print '\t\t' + colors.BLUE + 'Model   : ' + colors.ENDC + cpu_ver
		print '\t' + colors.HEADER_BOLD + 'Memory' + colors.ENDC
		print '\t\t' + colors.WHITE + '{} of {} DIMMs populated'.format((dimm_count - empty_dimms), dimm_count) + colors.ENDC
		print '\t\t' + colors.BLUE + 'Total   : ' + colors.ENDC + str(total_mem) + ' MB' + '  ({} GB)'.format((total_mem / 1024))
		print '\t\t' + colors.BLUE + 'Max Mem : ' + colors.ENDC + mem_max_format
		print '\t\t' + colors.GREEN + '{} total memory controllers, {} maximum per controller'.format(mem_arrays, max_mem) + colors.ENDC 			
		
	else:
		print colors.SECTION + 'DMI Decode' + colors.ENDC
		print '\t' + colors.WARN + 'DMIDECODE INFORMATION NOT AVAILABLE' + colors.ENDC
	
	try:
		os.remove(temp_file.name)
	except:
		pass
