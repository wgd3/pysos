from opsys import *
from opsys.chkconfig import *
from config import *
import os
from sysctls import *

def check_initrd(target):
	initrd = colors.WARN + 'initrd.img not found in sos_commands/bootloader/ls_-laR_.boot' + colors.ENDC
	if not os.path.isfile(target + 'sos_commands/bootloader/ls_-laR_.boot'):
		initrd = colors.WARN + 'missing ' + target +'sos_commands/bootloader/ls_-laR_.boot' + colors.ENDC
		return str(initrd)
		
	with open(target + 'sos_commands/bootloader/ls_-laR_.boot') as kfile:
		for line in kfile:
			if 'initrd' in line:
				initrd = line.split()[-1]
				return initrd
	return initrd

def get_kernel_info(target, local):
	
	# get kexec version, service enablement, initrd.img, kdump path
	kexec_ver = find_rpm(target, 'kexec-tools', local)
	kdump_status = find_chkconfig(target, 'kdump')
	initrd = check_initrd(target)
	
	# cmdline setting for crashkernel
	cmdline = get_status(target, 'cmdline')
	if 'crashkernel' in cmdline:
		index = cmdline.find('crashkernel')
		state = cmdline[index:-1].split()[0]
	else:
		state = colors.WARN + 'crashkernel setting not configured' + colors.ENDC	
		
	# parse kdump.conf for settings, then extrapolate others (more to come)
	config = []
	if os.path.isfile(target + 'etc/kdump.conf'):
		with open(target + 'etc/kdump.conf', 'r') as kfile:
			for line in kfile:
				if not line.startswith("#") and not line.startswith('\n'):
						config.append(line.rstrip('\n'))
	
		# set these to default of the / filesystem.
		filesys = '/'
		mount_at = '/'
		size = int(0)
		for item in config:
			if 'path' in item:
				crashpath = item.split()[1]
				index = crashpath.find('/')
				filesys = crashpath[index:len(crashpath)]
				mount_at = "/"
			with open(target + 'df', 'r') as df:
				for line in df:
					if len(line.split()) == 4:
						if line.split()[4] == mount_at:	
							size = str((round((int(line.split()[0]) / 1048576), 0)) + ' GB')
							
							break
					elif len(line.split()) == 6:
						if line.split()[5] == mount_at:	
							size = str(str(round((int(line.split()[1]) / 1048576), 0)) + ' GB')
							
							break	

	else:
		config.append(str(colors.WARN + 'kdump.conf not found' + colors.ENDC))
		mount_at = colors.WARN + 'Unknown' + colors.ENDC
		size = colors.WARN + 'Unknown' + colors.ENDC
	
	# find all panic related sysctl's, and split it up when we go to print it
	
	panic_ctl = find_sysctl(target, 'panic')	
						
	print colors.SECTION + colors.BOLD + 'Kdump ' + colors.ENDC
	print colors.HEADER_BOLD + '\t kexec-tools version :  ' + colors.ENDC + kexec_ver
	print colors.HEADER_BOLD + '\t Service enablement  :  ' + colors.ENDC + kdump_status
	print colors.HEADER_BOLD + '\t kdump initrd.img    :  ' + colors.ENDC + initrd
	print colors.HEADER_BOLD + '\t Memory Reservation  :  ' + colors.ENDC
	print colors.BLUE + colors.BOLD + '\t\t kernel arg   : ' + colors.ENDC + state
	print colors.BLUE + colors.BOLD + '\t\t GRUB conf    : ' + colors.ENDC
	print colors.HEADER_BOLD + '\t kdump.conf          : ' + colors.ENDC
	for item in config:
		print '\t\t\t        %s' %item
	print colors.BLUE + colors.BOLD + '\t\t path mount   : ' + colors.ENDC + mount_at
	print colors.BLUE + colors.BOLD + '\t\t avail space  :' + colors.ENDC + ' %s' %size		
	print colors.HEADER_BOLD + '\t Kernel Panic sysctl : ' + colors.ENDC
	for item in panic_ctl:
		kern = colors.BLUE + colors.BOLD + item.split()[0] + colors.ENDC
		if item.split()[2] == '0':
			ctl = ' = 0 ' + '[disabled]' + colors.ENDC
		elif item.split()[2] == '1':
			ctl = ' = 1 ' + colors.BOLD + '[enabled]' + colors.ENDC
		else:
			ctl = ' = %s ' %item.split()[2]
		print '\t\t\t\t {:<31} {}'.format(item.split()[0], ctl)
