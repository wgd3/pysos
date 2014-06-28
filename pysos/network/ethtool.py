def get_ethtool_info(target):
	# get list of all devices
	dev_list = []
	dev_info = {}
	with open(target +'proc/net/dev', 'r') as devfile:
		for line in devfile:
			if 'Inter' not in line:
				if ' face' not in line:
					index = line.find(':')
					dev = str(line[0:index]).strip()
					if 'lo' not in dev:
						dev_list.append(dev)
						
	# for each device found, get ethtool reported info
	for device in dev_list:
		link_state, link_speed, an_state = get_full_eth(target, device)
		driver, drv_ver, firmware_ver = get_ethi_info(target, device)
		rxring, rxjumbo = get_ring_info(target, device)
		dev_info[device] = [link_state, link_speed, an_state, rxring, rxjumbo, driver, drv_ver, firmware_ver]
	print colors.SECTION + colors.BOLD +  'Ethtool' + colors.ENDC
	print colors.WHITE + colors.BOLD + '\t {:^10}    {:^20}  {:^8}  {:^15}   {:^15}'.format('Device', 'Link', 'Auto-Neg', 'Ring', 'Driver Info')
	print '\t ' + '=' * 10 + '\t ' + '=' * 17 + '  ' + '=' * 10 + '\t ' + '=' * 10 + '\t ' + '=' * 15 + colors.ENDC
	for item in sorted(dev_info):
		if ';' not in item:
			value = dev_info[item]
			if 'bond' in item:
				linecolor = colors.GREEN
			elif 'eth' in item or 'em' in item:
				linecolor = colors.BLUE
			else:
				linecolor = colors.PURPLE
			print '\t' + linecolor + item + '\t\t ' + '{:<8}'.format(value[0]) + '{:<9}'.format(value[1]) + '   {:3}'.format(value[2]) + '\t  %4s%3s' %(value[3], value[4]) + '\t  ' + '{:<8}'.format(value[5]) + ' ver: {:5}  fw: {:8}'.format(value[6], value[7])


def get_full_eth(target, device):
	link_speed = ''
	an_state = 'off'
	link_state = ''
	if os.path.isfile(target +  'sos_commands/networking/ethtool_' + device):
		with open(target + 'sos_commands/networking/ethtool_' + device, 'r') as efile:
			for line in efile:
				if 'Link detected: no' in line:
					link_state = 'UNKNOWN'
				if 'Link detected: yes' in line:
					link_state = 'UP'
				if 'Speed:' in line:
					link_speed = line.split()[1]
				if 'Auto-negotiation:' in line:
					an_state = line.split()[1]
	return link_state, link_speed, an_state
	
					
def get_ethi_info(target, device):
	driver = ''
	drv_ver = ''
	firmware_ver = 'unknown'
	if os.path.isfile(target +  'sos_commands/networking/ethtool_-i_' + device):
		with open(target + 'sos_commands/networking/ethtool_-i_' + device, 'r') as efile:
			for line in efile:
				if 'driver:' in line:
					driver = line.split()[1]
					driver = driver.strip()
				if re.match('^version:', line):

					try: 
						drv_ver = line.split()[1]
					except:
						drv_ver = ''
				if 'firmware-version:' in line:
					try:
						firmware_ver = line.split()[1]
					except:
						firmware_ver = 'unknown'
	return driver, drv_ver, firmware_ver							
