import os, re
from collections import defaultdict
from config import *

def get_storage_info(target, local):
	disks = defaultdict(list)
	total_space = 0
	num_disks = 0

	disk_file = target + 'proc/partitions'
		
	with open(disk_file, 'r') as dfile:
		for line in dfile:
			if 'emc' not in line:
				if re.match('^ \d*', line):
					dev = str(line.split()[3]).strip()
					# check if dev ends in a number, meaning this would be a partition 
					if not re.search(r'\d+$', dev):	
						disks[dev] = round(((int(line.split()[2])) / 1048576), 0)
						total_space += round(((int(line.split()[2])) / 1048576), 0)
						num_disks += 1
						
					else:
						# cciss devices would all get called partitions in the above. Here we handle them explicitly
						if 'cciss' in dev:
							# cciss partitions format as cxdxpx
							if 'p' in dev:
								pass
							else:
								disks[dev] = round(((int(line.split()[2])) / 1048576), 0)
								total_space += round(((int(line.split()[2])) / 1048576), 0)
								num_disks += 1
	
						else:
							pass
		
	
	print colors.SECTION + colors.BOLD + 'Storage' + colors.ENDC
	print colors.HEADER_BOLD + '\t Whole disks on system :  ' + colors.ENDC + str(num_disks)
	print colors.GREEN + '\t Total amount of storage on system : ' + colors.ENDC + str(total_space) + ' GB' + '  ( %2.2f TB)' %((total_space / 1024))
	print colors.WHITE + '\t {:^25}  {:^10}'.format('Disk', 'Size in GB') 
	print '\t\t' + '=' * 11 + '\t ' + '=' * 15 + colors.ENDC
	for item in sorted(disks):
		print '\t\t{:14}  {:>15}'.format(item, disks[item])
