import os, re, textwrap
from config import *

def get_cpu_info(target):
	if os.path.isfile(target + 'proc/cpuinfo'):
		processors = int()
		phys_cpus = int()
		core_count = int()
		threads = int()	
		with open(target + 'proc/cpuinfo', 'r') as cfile:
			for line in cfile:
				index = line.find(':')
				if line.startswith('processor'):
					processors += 1
				if 'model name' in line:
					cpu_model = line[index+2:len(line)].rstrip('\n')
					if 'QEMU' in cpu_model:
						phys_cpus = '0 [virt] '
						core_count = processors
						threads = 1
				if line.startswith('physical'):
					phys_cpus = (int(line[index+2:len(line)].rstrip('\n')) + 1)
				if re.match('^cpu cores', line):
					core_count = line[index+2:len(line)].rstrip('\n')
				if line.startswith('siblings'):
					threads = line[index+2:len(line)].rstrip('\n')
				if line.startswith('flags'):
					cpu_flags = line[index+2:len(line)].rstrip('\n')
		print colors.SECTION + colors.BOLD + 'CPU' + colors.ENDC
		print colors.WHITE + colors.BOLD + '\t\t %s logical processors' %processors + colors.ENDC
		print '\t\t %s %s processors' %(phys_cpus, cpu_model)
		print '\t\t %s cores / %s threads per physical processor' %(core_count, threads)
		print '\t\t flags : ' + textwrap.fill(cpu_flags, 80, subsequent_indent='%25s' % ' ')
	else:
		print 'Error parsing proc/cpuinfo'
