import os, re, datetime
from config import colors

def sel_check(target, local):
	# checking for how SELinux starts
	if not local:
		selfile = target + 'etc/selinux/config'
	else:
		selfile = '/etc/selinux/config'
	if os.path.isfile(selfile):
		with open(target + 'etc/selinux/config', 'r') as selfile:
			for line in selfile:
				if re.match("SELINUX=", line):
					index = line.find("=")
					selstate = line[index+1:len(line)].rstrip('\n')
					return selstate
			if not selstate:
				selstate = colors.WARN + 'SELinux state unknown' + colors.ENDC
				return selstate
	else:
		return 'Unknown. etc/selinux/config file not found'
