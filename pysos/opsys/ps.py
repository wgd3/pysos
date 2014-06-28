def get_ps_info(target):
	print colors.HEADER_BOLD + 'PS' + colors.ENDC
	retval = parse_ps_file(target)	
	usage = defaultdict(list)
	bad_proc = defaultdict(list)
	bad_procs = 0 
	header = '\t' + colors.BLUE + colors.BOLD + '{:^6}\t{:^6}\t{:^5} {:^5}  {:^7}  {:^7}  {:^4} {:^4}  {:^5}{:^8} {:<8}'.format('USER', 'PID', '%CPU', \
	'%MEM', 'VSZ-MB', 'RSS-MB', 'TTY', 'STAT', 'START', 'TIME', 'COMMAND') + colors.ENDC
	print '\t' + colors.WHITE + 'Total processes : ' + colors.ENDC + str(len(retval)) +'\n'
	# get top usage by user
	for item in retval:
		value = retval[retval.index(item)]
		if usage.has_key(value[0]):
			usage[value[0]][0] += float(value[2])
			usage[value[0]][1] += float(value[3])
			usage[value[0]][2] += float(value[5])
		else:
			usage[value[0]] = [float(value[2]), float(value[3]), float(value[5])]
	
	print '\t' + colors.WHITE + 'Top Users of CPU and MEM : ' + colors.ENDC
	print '\t ' + colors.BLUE + colors.BOLD + '{:7}  {:5}  {:5}  {:7}'.format('USER', '%CPU', '%MEM', 'RSS') + colors.ENDC
	report_usage = sorted(usage.items(), reverse=True, key=lambda x: x[1][2])
	for i in xrange(0,4):
		value = report_usage[i]
		print '\t {:<8}  {:<5} {:^5}  {:5.2f} GB'.format(value[0], value[1][0], value[1][1], int(value[1][2]) / 1048576)
	print ''
	# search for defunct and trouble processes
	for item in retval:
		value = retval[retval.index(item)]
		if any('<defunct>' in item for item in value) or any('D' in item for item in value[7]):
			bad_procs += 1
			bad_proc[bad_procs] = value
	if bad_procs > 0:
		print '\t' + colors.WHITE + 'Uninterruptable Sleep and Defunct Processes : ' + colors.ENDC
		print header
		for each in range(bad_procs):
			print_ps_info(bad_proc[bad_procs], 1, single=True)
	
	# sort by CPU usage	
	print '\t' + colors.WHITE + 'Top CPU processes : ' + colors.ENDC
	print header
	retval.sort(reverse=True, key=lambda x: float(x[2]))
	print_ps_info(retval, 5)
	
	# sort by MEM usage
	# Known bug: if retval is not refreshed, sorting by memory breaks. I have no idea why
	print '\t' + colors.WHITE + 'Top Memory processes : ' + colors.ENDC
	print header
	retval = parse_ps_file(target)
	retval.sort(reverse=True, key=lambda x: float(x[5]))	
	print_ps_info(retval, 5)	

def parse_ps_file(target):
	retval = []
	with open(target + 'ps', 'r') as psfile:
		psfile.next()
		for line in psfile:
			proc = line.split()
			nfields = len(line.split()) -1
			retval.append(line.split(None, nfields))
	return retval

def print_ps_info(retval, num, single=False):
	for i in xrange(0,num):
		if single:
			ps = retval
		else:
			ps = retval[i]
		ps[4] = int(ps[4]) / 1024
		ps[5] = int(ps[5]) / 1024
		cmd = ''
		for i in xrange(10, 13):
			try:
				cmd = cmd + ' ' + str(ps[i]).strip('\n')
			except:
				pass
		print '\t{:^8} {:^6}\t{:^5} {:^5}  {:<7.0f}  {:<7.0f}  {:^5} {:^4} {:^6} {:<7}{}'.format(ps[0], ps[1], ps[2], ps[3], ps[4], ps[5], ps[6], ps[7], ps[8], ps[9], cmd[0:50])
	print ''
