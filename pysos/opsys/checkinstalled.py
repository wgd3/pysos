import os
from config import *
from checkrpm import *

def check_installed(target, rpm, local=False):
	print colors.SECTION + 'Package Check' + colors.ENDC
	print ''
	
	if local:
		import tempfile, subprocess
		temp_file = tempfile.NamedTemporaryFile(delete=False)
		command = subprocess.Popen(['rpm -qa'], stdout=subprocess.PIPE)
		output = command.stdout.read()
		for line in output:
			temp_file.write(line)
		temp_file.close()
		rfile = tem_file.name
	else:
		rfile = target + 'installed-rpms'
	
	if not os.path.isfile(rfile):
		print colors.RED + colors.BOLD + '\t Installed RPMs file not found' + colors.ENDC
		return False
	
	if rpm == 'all':
		with open(rfile, 'r') as rfile:
			for line in rfile:
				ver = line.split()[0]
				package = check_rpm_ver(ver, all_test=True)
				if package:
					print '\t' + colors.RED + colors.BOLD +' {:10} : '.format(ver) + colors.ENDC +' {:20}'.format(package[0]) \
					+ colors.WHITE + '  KCS :' + colors.ENDC +' {:7}'.format(package[1]) + colors.WHITE + '  BZ :' + colors.ENDC \
					+' {:7}'.format(package[2])
	else:
		with open(rfile, 'r') as rfile:
			for line in rfile:
				if rpm in line:
					ver = line.split()[0]
					package = check_rpm_ver(ver, stand_alone=True)
					if type(package) is list:
						print '\t' + colors.RED + colors.BOLD +'{:10} : '.format(ver) + colors.ENDC +' {:20}'.format(package[0]) \
					+ colors.WHITE + '  KCS :' + colors.ENDC +' {:7}'.format(package[1]) + colors.WHITE + '  BZ :' + colors.ENDC \
					+' {:7}'.format(package[2])
					else:
						print '\t' + colors.BLUE + '{:50} :'.format(ver) + colors.ENDC + ' {:>15}'.format(package)
