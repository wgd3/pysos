import os, re
from config import *
from collections import defaultdict

def get_lspci_info(target, local):
	devices = defaultdict(list)
	counter = 0
	if local:
		temp_file = tempfile.NamedTemporaryFile(delete=False)
		command = subprocess.Popen(['lspci'], stdout=subprocess.PIPE)
		output = command.stdout.read()
		for line in output:
			temp_file.write(line)
		temp_file.close()
		lspci_file = temp_file.name
	else:
		lspci_file = target + 'lspci'
		
	if os.path.isfile(lspci_file):
		with open(lspci_file, 'r') as lfile:
			for line in lfile:
				line = line.strip('\n')
				# stop once we go beyond the basic output
				if 'lspci -nvv:' in line:
					break
				if 'lspci:' not in line:
					# don't include the base chipset
					if '00:01' not in line:
						try:
							pci_addr = line.split()[0]
							index = pci_addr.find('.')
							pci_addr = pci_addr[0:index]
							index = line.find(': ')
							dev = line[index+1:len(line)]
							index2 = line.find('.')
							controller = line[index2+2:index]
							if devices.has_key(pci_addr):
								counter += 1
								dev_list = [controller, dev, counter]
								devices[pci_addr] = dev_list
							else:
								counter = 1
								dev_list = [controller, dev, counter]
								devices[pci_addr] = dev_list	
						except:
							pass
					else:
						pass
				else:
					pass
	try:
		os.remove(temp_file.name)
	except:
		pass
		
	print colors.SECTION + colors.BOLD + 'LSPCI' + colors.ENDC
	print ''
	print colors.HEADER_BOLD + '\t Physical Devices' + colors.ENDC

	for item in sorted(devices):
		value = devices[item]
		if 'Serial Attached' in value[0]:
			value[0] = 'SAS'
		if 'Lights-Out' in value[1]:
			value[0] = 'IPMI'
			value[2] = '1'
			value[1] = str(value[1])[0:str(value[1]).find('Lights-Out')+10]
			
		# only display hardware devices we care about. Can expand this as we need to
		show_these = ['VGA', 'Ethernet', 'Network', 'Realtek', 'SCSI', 'SAS', 'IPMI']
		for item in show_these:
			if item in value[0]:
				print colors.BLUE + '\t\t' +  '{:<10} '.format(value[0].split()[0]) + colors.WHITE + '{:^1} ports '.format(value[2]) + colors.ENDC + value[1]
