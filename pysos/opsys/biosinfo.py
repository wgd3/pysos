def get_bios_info(target, local):
	total_cores = 0
	total_threads = 0
	cpus_populated = 0
	mem_arrays = 0
	fam_count = 0
	ver_count = 0
	total_mem = 0
	dimm_count = 0
	empty_dimms = 0
	core_count = 0
	thread_count = 0
	if local:
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
		with open(dmi_file, 'r') as dfile:
			# first the main iterables that have distinct leading names
			for line in dfile:
				if 'Vendor:' in line:
					bios_vendor = line.split()[1]
				if 'Release Date:' in line:
					bios_date = line.split()[2]
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
				if 'Product Name:' in line:
					index = line.find(':')
					server_type = line[index+1:len(line)].rstrip('\n')
				if 'UUID:' in line:
					serv_uuid = line.split()[1]
			# now, some ugly badness to get items that have the same leading header
				if 'Family:' in line:
					if fam_count == 0:
						fam_count += 1
					else:
						cpu_family = line.split()[1]
						
						
			# this. this right here is horrible. I'm bad and I should feel bad.
			# ...and also I'm lazy.
				if 'Version:' in line and 'Specification Version:' not in line:
					if ver_count == 0:
						bios_ver = line.split()[1]
						ver_count +=  1
					elif ver_count == 1:
						sys_ver = line.split()[1]
						ver_count += 1
					elif ver_count == 2:
						chas_ver = line.split()[1]
						ver_count += 1
					else:
						index = line.find(':')
						cpu_ver = line[index+1:len(line)].strip()
						
						
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
		print '\t\t' + colors.BLUE + 'Vendor  : ' + colors.ENDC + bios_vendor
		print '\t\t' + colors.BLUE + 'Server  :' + colors.ENDC + server_type
		print '\t\t' + colors.BLUE + 'UUID    : ' + colors.ENDC + serv_uuid
		print '\t' + colors.HEADER_BOLD + 'CPU' + colors.ENDC
		print '\t\t' + colors.WHITE + '{} CPU sockets populated, {} cores / {} threads per core'.format(cpus_populated, core_count, thread_count) + colors.ENDC
		print '\t\t' + colors.WHITE + '{} total cores - {} total threads'.format(total_cores, total_threads) + colors.ENDC
		print '\t\t' + colors.BLUE + 'Family  : ' + colors.ENDC + cpu_family
		print '\t\t' + colors.BLUE + 'Clock   : ' + colors.ENDC + cpu_freq 
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
