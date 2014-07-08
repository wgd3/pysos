import os, re

def get_rhn(target, local, channels=False):
	
	# Don't care about channels, looking for sub/sat/etc info
	if not channels:
		if os.path.isfile(target + 'etc/sysconfig/rhn/up2date'):
			with open(target + 'etc/sysconfig/rhn/up2date', 'r') as rhnfile:
				for line in rhnfile:
					if re.match('^serverURL=.*', line):
						index = line.find('=')
						return line[index+1:len(line)].rstrip('\n')
		else:
			return colors.WARN + 'Up2date file not found' + colors.ENDC
	
	# Get dem channels		
	else:
		chans = {}
		with open(target + 'sos_commands/yum/yum_-C_repolist', 'r') as yfile:
			
			for line in yfile:
				if not line.startswith(('repo','Loaded', 'This')):
					repo = line.split()[0]
					index = line.find(' ')
					index2 = line.find('(')
					name = line[index+1:index2-1]
					chans[repo] = name
			
			return chans
				
			
			
		
	
