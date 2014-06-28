def find_sysctl(target, sysctl):
	sysctls = []
	if os.path.isfile(target +'sos_commands/kernel/sysctl_-a'):
		with open(target + 'sos_commands/kernel/sysctl_-a', 'r') as sysfile:
			for line in sysfile:
				if sysctl in line:
					sysctls.append(line.rstrip('\n'))
	return sysctls

def get_sysctl_info(target):
	
	vm_sysctls = find_sysctl(target, 'vm.')
	vm_prints = ['dirty', 'hugepage', 'panic', 'overcommit', 'swappiness']
	
	net_sysctls = find_sysctl(target, 'net.')
	net_prints = ['core.netdev_budget', 'core.netdev_max_backlog', 'ipv4.tcp_mem', 'ipv4.ip_forward', 'ipv4.icmp_echo_ignore_all',\
	 'ipv4.tcp_rmem', 'ipv4.tcp_wmem', 'ipv4.tcp_max_orphans']
	
	kernel_sysctls = find_sysctl(target, 'kernel.')
	kernel_prints = ['tainted', 'panic', 'pid_max', 'threads-max', 'shmall', 'shmmax', 'shmmni']
	
	print colors.SECTION + colors.BOLD + 'Sysctls' + colors.ENDC
	
	for section in (['kernel', kernel_sysctls, kernel_prints], ['net', net_sysctls, net_prints]\
	, ['vm', vm_sysctls, vm_prints]):
		print colors.HEADER_BOLD + '\t %s' %section[0] + colors.ENDC
		
		for item in section[1]:
			for each in section[2]:
				if each in item:
					item = str(item)
					indexname = item.find('.')
					index = item.find('=')
					print colors.BLUE + colors.BOLD + '\t %33s' %item[indexname+1:index-1] + colors.ENDC + ' = ' + item[index+1:len(item)]
