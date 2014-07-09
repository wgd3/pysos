import os,math

def get_status(target, status, local=False):


	if not local:
		statuses = {}
		statuses['hostname'] = 'sos_commands/general/hostname'
		statuses['release'] = 'etc/redhat-release'
		statuses['runlevel'] = 'sos_commands/startup/runlevel'
		statuses['uptime'] = 'sos_commands/general/uptime'
		statuses['kernel'] = "sos_commands/kernel/uname_-a"
		statuses['cmdline'] = 'proc/cmdline'
		statuses['date'] = 'date'
	else:
		statuses = {}
		stats = {}
		statuses['release'] = 'etc/redhat-release'
		statuses['cmdline'] = 'proc/cmdline'
		statuses['kernel'] = 'proc/version'
		for stat in statuses:
			if os.path.isfile(target + statuses[stat]):
				with open(target + statuses[stat], 'r') as rfile:
					for line in rfile:
						statuses[stat] = line.rstrip('\n')
			else:
				statuses[stat] = 'not found!'
		for item in ['runlevel', 'uptime', 'date', 'hostname']:
			process = subprocess.Popen(item, stdout=subprocess.PIPE)
			stdout, stderr = process.communicate()
			stats[item] = stdout.rstrip('\n')
		
		try:
			for item in stats:
				statuses[item] = stats[item]
		except:	
			pass
	# get everything shoved into the statuses dictionary
	if status == 'all':
		for key, path in statuses.items():
			fullpath = '%s%s' %(target, path)
			if os.path.isfile(fullpath):
				with open(fullpath, 'r') as rfile:
					for line in rfile:
						result = line.rstrip('\n')
						statuses[key] = result
			else:
				statuses[key] =  colors.RED  + path + ' not found!' + colors.ENDC


		return statuses
	else:
		if not local:
			if os.path.isfile(target + statuses[status]):
				with open(target + statuses[status], 'r') as rfile:
					for line in rfile:
						statuses[status] = line.rstrip('\n')
						return line.rstrip('\n')
			else:
				return 'not found!'
		else:
			return statuses[status]
