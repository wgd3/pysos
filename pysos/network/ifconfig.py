def get_ip_info(target, local=False):
	interfaces = {}
	int_info = defaultdict(list)
	if local:
		mem_file = tempfile.NamedTemporaryFile(delete=False)
		command = subprocess.Popen(['ip', '-o', 'addr'], stdout=subprocess.PIPE)
		output = command.stdout.read()
		for line in output:
			mem_file.write(line)
		mem_file.close()
		ip_file = mem_file.name
		
		temp_file = tempfile.NamedTemporaryFile(delete=False)
		command = subprocess.Popen(['brctl', 'show'], stdout=subprocess.PIPE)
		output = command.stdout.read()
		for line in output:
			temp_file.write(line)
		temp_file.close()
		br_file = temp_file.name
	else:
		ip_file = target + 'ip_addr'
		br_file = target + 'sos_commands/networking/brctl_show'
	
	# get bridge associations
	if os.path.isfile(br_file):
		brfile = True
		with open(br_file, 'r') as bfile:
			bridge_list = list()
			bridges = {}
			bridge_output = bfile.read()
			
			# KNOWN ISSUE:
			# With the below regex, if the bridge only has a single interface on it
			# it will not be captured
			for bridge_lines in re.findall(r'(?m)^\S.*\n(?:\t*\n)+', bridge_output):
				bridge, _ = bridge_lines.split(None, 1)
				bridges[bridge] = re.findall(r'(?m)\S+$', str(bridge_lines))
				bridge_list.append(bridge)
	else:
		brfile = False
	
	if os.path.isfile(ip_file):
		ipfile = True
		with open(ip_file, 'r') as f:
		    lines = [line for line in f if line.strip()]
		    # group by line number
		    for key, group in groupby(lines, lambda x: x.split()[1]):
		        interface = []
		        for thing in group:
		            # append lines without repeating part
		            interface += thing.split()[2:]
		        if interface:
					dev = str(key).rstrip(':')
					interfaces[dev] = interface	
			
		    for key in interfaces:
				bridge_member = ''
				try:
					for item in bridge_list:
						if key in bridges[item]:
							bridge_member = item
				except:
					pass
					
				try:
					index = interfaces[key].index('mtu')
					mtu = interfaces[key][index+1]
				except:
					mtu = ''
				try:
					index = interfaces[key].index('master')
					slaveof = interfaces[key][index+1]
				except:
					slaveof = ''
				try:
					index = interfaces[key].index('inet')
					ipaddr = interfaces[key][index+1]
				except:
					ipaddr = ''
				int_info[key].append([ipaddr, slaveof, mtu])
				try:
					index = interfaces[key].index('link/ether')
					hwaddr = interfaces[key][index+1]
				except:
					hwaddr = ''
				
				slaves = list()
				slaves.append(slaveof)
				slaves.append(bridge_member)
				int_info[key] = ([ipaddr, slaves, mtu, hwaddr])
	
	else:
		ipfile = False
	print colors.SECTION + colors.BOLD + 'IP ' + colors.ENDC
	if not brfile:
		print colors.RED + colors.BOLD + '\t BRIDGE INFORMATION NOT FOUND' + colors.ENDC
		print''
		
	if 	ipfile:

		print colors.WHITE + colors.BOLD + '\t {:^15}        {:^20}      {:^11}   {:^12} {:^24}'.format('INT','IP ADDR', 'MEMBER OF','MTU', ' HW ADDR')
		print '\t' + '=' * 16 + ' ' * 6 + '=' * 23 + ' ' * 4 + '=' * 13 + ' ' * 5 + '=' * 5 + '\t' + '=' * 19 + colors.ENDC
	
	else:
		print colors.RED + colors.BOLD + '\t NO IP ADDR FILE FOUND. CANNOT PARSE' + colors.ENDC
			

	for key in sorted(int_info):
		slavelist = ''
		value = int_info[key]
		key = str(key).rstrip(':')
		for item in value[1]:
			slavelist = slavelist + item
		if 'eth' in key or 'em' in key:
			linecolor = colors.BLUE
		elif 'vlan' in key:
			linecolor = colors.CYAN
		elif 'bond' in key:
			linecolor = colors.GREEN
		elif 'vnet' in key:
			linecolor = colors.WHITE
		else:
			linecolor = colors.PURPLE
		print '\t' + linecolor + '{:<15s}'.format(key) + '{:^36s}{:<16s}{:<5} \t {:<5}'.format(value[0],slavelist,value[2],value[3]) + colors.ENDC
	
	try:
		os.remove(temp_file.name)
		os.remove(mem_file.name)
	except:
		pass
			
