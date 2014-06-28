def get_netdev_info(target):
	dev_info = {}
	with open(target +'proc/net/dev', 'r') as devfile:
		for line in devfile:
			if 'Inter' not in line:
				if ' face' not in line:
					index = line.find(':')
					key = line[0:index]
					dev_info[key] = line[index+1:len(line)].lstrip(' ').rstrip('\n')
					
		
	print colors.SECTION + colors.BOLD + 'Netdev' + colors.ENDC
	tab = '    '
	print colors.WHITE + colors.BOLD + '\t' + 'Interface' + tab + 'RxGBytes' + tab + 'RxPackets'	+ tab + 'RxErrs'\
	 + tab + 'RxDrop' + tab + 'TxGBytes' + tab + 'TxPackets' + tab + 'TxErrs' + tab + 'TxDrop'\
	 + tab + 'TxOvers' + colors.ENDC
	spacer = '  ' + '=' * 10 + '  '
	print colors.WHITE + tab + '   ' + '=' * 11 + spacer + '=' * 11 + '  ' + '=' * 8 + '  '\
	+ '=' * 8 + spacer + '=' * 11 + '  ' + '=' * 8 + '  ' + '=' * 8 + '  ' + '=' * 9 + colors.ENDC
	for item in sorted(dev_info):
		value = dev_info[item].split()
		for num in 0, 1, 4, 5:
			if value[num] == '':
				value[num] = 1
		if 'eth' in item or 'em' in item:
			linecolor = colors.BLUE
		elif 'vlan' in item:
			linecolor = colors.CYAN
		elif 'bond' in item:
			linecolor = colors.GREEN
		elif 'vnet' in item:
			linecolor = colors.WHITE
		else:
			linecolor = colors.PURPLE
		print linecolor + '\t' + '{:<10}'.format(item) + tab + '%6.2f' % round(int(value[0]) / (1024 * 1024 * 1024), 2)\
		+ tab + ' %7.0f' % round((int(value[1]) / (1000000)), 2) + ' m' + tab + '{:>4}'.format(value[2])\
		+ tab + '{:>6}'.format(value[3]) + tab + '%7.2f' % round(int(value[8]) / (1024 * 1024 * 1024), 2)\
		+ tab + '  %7.0f' % round((int(value[9]) / (1000000 )), 2) + ' m' + tab + '{:>4}'.format(value[10])\
		+ tab + '{:>6}'.format(value[11]) + tab + '{:>6}'.format(value[12]) + colors.ENDC
			
			
