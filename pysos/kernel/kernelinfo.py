from opsys.findrpm import *
from opsys.chkconfig import *
from opsys.getstats import *
from config import *
import os
from sysctls import *

def check_initrd(target, kernel, local):
	if local:
		for path,dirs,files in os.walk('boot'):
			if 'initrd' in files:
				index1 = '-'
				index2 = 'kdump'
				initrd = files[index1+1:index2]
				if str(initrd) in str(kernel):
					return str(initrd)
		return 	colors.WARN + 'no initrd matching running kernel found' + colors.ENDC
	
	else:
		initrd_path = target + 'sos_commands/bootloader/ls_-laR_.boot'

		if not os.path.isfile(initrd_path):
			return colors.WARN + 'missing ' + target +'sos_commands/bootloader/ls_-laR_.boot' + colors.ENDC
		else:
			with open(target + 'sos_commands/bootloader/ls_-laR_.boot') as kfile:
				for line in kfile:
					if 'initrd' in line:
						index = line.find('initrd')
						line = line[index:len(line)].strip('\n')
						idx1 = line.index('-')
						idx2 = line.index('k')
						initrd = line[idx1+1:idx2]
						if str(initrd) in str(kernel):
							return str(initrd)
				return colors.WARN + 'no initrd matching running kernel found' + colors.ENDC	

def crash_space(target, crashpath):
			
	with open(target + 'df', 'r') as df:
		crash = {}
		for line in df:
			if line.strip('\n').endswith(crashpath):
				
				crash['mount'] = crashpath
				splits = len(line.split())
				crash['free'] = str(int(line.split()[splits-3]) / 1024) + ' GB'
				return crash
		df.seek(0)
		for line in df:
			if line.strip('\n').endswith('/'):
				crash['mount'] = 'root'
				splits = len(line.split())
				crash['free'] = str(int(line.split()[splits-3]) / 1024 / 1024) + ' GB'
				return crash



def get_kernel_info(target, local):
	
	# get kexec version, service enablement, initrd.img, kdump path
	kernel = get_status(target, 'kernel', local).split()[2]
	kexec_ver = find_rpm(target, 'kexec-tools', local)
	kdump_status = find_chkconfig(target, 'kdump')
	initrd = check_initrd(target, kernel, local)
	
	# cmdline setting for crashkernel
	cmdline = get_status(target, 'cmdline')
	if 'crashkernel' in cmdline:
		index = cmdline.find('crashkernel')
		crashkern = cmdline[index:-1].split()[0]
	else:
		crashkern = colors.WARN + 'crashkernel setting not configured' + colors.ENDC	
		
	# parse kdump.conf for settings, then extrapolate others (more to come)
	config = []
	if os.path.isfile(target + 'etc/kdump.conf'):
		with open(target + 'etc/kdump.conf', 'r') as kfile:
			for line in kfile:
				if not line.startswith("#") and not line.startswith('\n'):
						config.append(line.rstrip('\n'))
		for item in config:
			if 'path' in item:
				crashpath = item.split()[1]
		
		crash_info = crash_space(target, crashpath)

	else:
		config.append(str(colors.WARN + 'kdump.conf not found' + colors.ENDC))
		mount_at = colors.WARN + 'Unknown' + colors.ENDC
		size = colors.WARN + 'Unknown' + colors.ENDC
	
	# find all panic related sysctl's, and split it up when we go to print it
	
	panic_ctl = find_sysctl(target, 'panic')	
						
	print colors.SECTION + colors.BOLD + 'Kdump ' + colors.ENDC
	print colors.HEADER_BOLD + '\t Running Kernel      :  ' + colors.ENDC + kernel
	print colors.HEADER_BOLD + '\t kexec-tools version :  ' + colors.ENDC + kexec_ver
	print colors.HEADER_BOLD + '\t Service enablement  :  ' + colors.ENDC + kdump_status
	print colors.HEADER_BOLD + '\t kdump initrd.img    :  ' + colors.ENDC + initrd
	print colors.HEADER_BOLD + '\t Memory Reservation  :  ' + colors.ENDC + crashkern
	print colors.HEADER_BOLD + '\t kdump.conf          : ' + colors.ENDC
	for item in config:
		print '\t\t\t\t%s' %item
	print ''
	print colors.BLUE + colors.BOLD + '\t\t Crash Path   : ' + colors.ENDC + crash_info['mount']
	print colors.BLUE + colors.BOLD + '\t\t Free Space   : ' + colors.ENDC + crash_info['free']		
	print colors.HEADER_BOLD + '\t Kernel Panic sysctl : ' + colors.ENDC
	for item in panic_ctl:
		if item.split()[2] == '0':
			ctl = ' = 0 ' + '[disabled]' + colors.ENDC
		elif item.split()[2] == '1':
			ctl = ' = 1 ' + colors.BOLD + '[enabled]' + colors.ENDC
		else:
			ctl = ' = %s ' %item.split()[2]
		print '\t\t\t\t {:<31} {}'.format(item.split()[0], ctl)
