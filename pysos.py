#!/usr/bin/env python
# xsos re-written in Python
# xsos for BASH originally written by Ryan Sawhill <rsaw@redhat.com>
# xsos Python re-write by Jake Hunsaker <jake@redhat.com>
# rhev plugin written by Wallace Daniel <wdaniel@redhat.com>
#
# ---> yes, my Python probably makes any other programmer's eyes bleed
#      I am well aware of this
#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#    General Public License <gnu.org/licenses/gpl.html> for more details.
#
from __future__ import division
from itertools import groupby
#from rhevlcbridge.database import Database
from rhevlcbridge import *
import os, argparse, textwrap, re, datetime, time, tarfile



# switches
parser = argparse.ArgumentParser(description='Make a sosreport pretty.')
parser.add_argument('target', metavar='TARGET', nargs='+', help='Target directory for xsos. Defaults to current dir.', default='./')
parser.add_argument('-o', "--os", action="store_true", help='Prints OS information')		
parser.add_argument('-m', "--memory", action="store_true", help='Prints memory information')
parser.add_argument('-k', "--kdump", action="store_true", help="Prints kdump information")
parser.add_argument('-c', "--cpu", action="store_true", help='Print CPU information ONLY')
parser.add_argument('-s', "--sysctl", action="store_true", help='Print all sysctl information')
parser.add_argument('-i', "--ip", action="store_true", help='Print IP information')
parser.add_argument('-g', "--bonding", action="store_true", help='Print bonding information')
parser.add_argument('-t', "--test", action="store_true")
parser.add_argument('-n', "--netdev", action="store_true", help='Print proc/net/dev information')
parser.add_argument('-r', "--rhev", action="store_true", help='Print RHEV Information')
parser.add_argument('-e', "--ethtool", action="store_true", help='Prints ethtool information')
args = parser.parse_args()

# Bits that might be reused go in this dict. Hardcoded for the moment, will pull from a config file
# eventually, as this is super fucking ugly and terrible
# Takes form of [key]=path. Then we change path to the value stored therein to call later.
# paths are relative to root of sosreport
statuses = {}
statuses['hostname'] = ['sos_commands/general/hostname']
statuses['release'] = ['etc/redhat-release']
statuses['runlevel'] = ['sos_commands/startup/runlevel']
statuses['uptime'] = ['sos_commands/general/uptime']
statuses['kernel'] = ["sos_commands/kernel/uname_-a"]
statuses['cmdline'] = ['proc/cmdline']
statuses['runlevel'] = ['sos_commands/startup/runlevel']
statuses['systime'] = ['date']


# Define colors - yay color!
# Need more - build out later
class colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    SECTION = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    WHITE = '\033[37m'
    HEADER_BOLD = '\033[95m' + '\033[1m'
    WARN = '\033[33m'
    PURPLE = '\033[35m'
    CYAN = '\033[36m'
    
def find_rpm(target, rpm):
	# from here we will pull specific targets for installed RPMS
	rpm_state = False
	if os.path.isfile(target + 'installed-rpms'):
		with open(target + 'installed-rpms', 'r') as rpmfile:
			for line in rpmfile:
				if rpm in line:
					rpm_state = line.split()[0]
					return rpm_state
		if not rpm_state:
			return colors.WARN + rpm + ' not found' + colors.ENDC
	else:
		return colors.WARN + 'installed rpms file not found!' + colors.ENDC
def find_chkconfig(target, service):
	
	# search for specific config states for a given service
	service_status = False
	if not os.path.isfile(target + 'chkconfig'):
		service_status = colors.WARN + colors.BOLD + 'chkconfig file not found!' + colors.ENDC
		return service_status
	with open(target + 'chkconfig', 'r') as configfile:
		for line in configfile:
			if service in line:
				service_status = line.rstrip('\n')
				return service_status
				
	if not service_status:
		service_status = colors.WARN + '%s not found in chkconfig' %service
		return service_status
	
def get_status(target, status):
	global statuses
	
	# get anything shoved inxsos --to the statuses dictionary
	if status == 'all':
		for key, path in statuses.items():
			fullpath = '%s%s' %(target, path[0])
			if os.path.isfile(fullpath):
				with open(fullpath, 'r') as rfile:
					for line in rfile:
						result = line.rstrip('\n')
						statuses[key] = result
			else:
				statuses[key] =  colors.RED  + path[0] + ' not found!' + colors.ENDC
	else:
		if os.path.isfile(target + statuses[status][0]):
			with open(target + statuses[status][0], 'r') as rfile:
				for line in rfile:
					statuses[status] = line.rstrip('\n')
					return line.rstrip('\n')
def taint_check(target):
	
	# check for kernel taint, well known values go in this dictionary
	t={}
	t['0']="Not tainted. Hooray!"
	t['1']="Proprietary module has been loaded"
	t['2']="Module has been forcibly loaded"
	t['4']="SMP with CPUs not designed for SMP"
	t['8']="User forced a module unload"
	t['16']="System experienced a machine check exception"
	t['32']="System has hit bad_page"
	t['64']="Userspace-defined naughtiness"
	t['128']="Kernel has oopsed before"
	t['256']="ACPI table overridden"
	t['512']="Taint on warning"
	t['1024']="Modules from drivers/staging are loaded"
	t['2048']="Working around severe firmware bug"
	t['4096']="Out-of-tree module has been loaded"
	t['268435456']="Hardware is unsupported"
	t['536870912']="Technology Preview code is loaded"
	
	with open(target + 'proc/sys/kernel/tainted', 'r') as tfile:
		check = tfile.read().splitlines()
		if check[0] in t:
			return t[check[0]]
		else:
			return 'Undefined taint code : %s' %check[0]
			
			
def get_rhn(target):
	if os.path.isfile(target + 'etc/sysconfig/rhn/up2date'):
		with open(target + 'etc/sysconfig/rhn/up2date', 'r') as rhnfile:
			for line in rhnfile:
				if re.match('^serverURL=.*', line):
					return line.rstrip('\n')
	else:
		return 'Up2date file not found'
		
def sel_check(target):
	# checking for how SELinux starts
	with open(target + 'etc/selinux/config', 'r') as selfile:
		for line in selfile:
			if re.match("SELINUX=", line):
				index = line.find("=")
				selstate = line[index+1:len(line)].rstrip('\n')
				return selstate
		if not selstate:
			selstate = colors.RED + 'SELinux state unknown' + colors.ENDC
			return selstate
			
def get_loadavg(target, cpus):
	# get raw loadavg report from sosreport
	with open(target + 'uptime', 'r') as lfile:
		load = lfile.readline()
		index = load.find('e:')
		loadavg = load[index+2:len(load)].rstrip('\n')
		
	# now, calculate percent load from the string
	loads = loadavg.split(',')
	for item in loads:
		index = loads.index(item)
		loadperc = (float(item) / cpus) * 100
		loads[index] = (loads[index] + ' (%.2f%%)') %loadperc
	return str(loads[0] + loads[1] + loads[2])
	
		
def graphit(perc):
	
	# general graphing function, needs to be fed a percentage. 
	tick = u"\u25C6"
	empty = u"\u25C7"	
	filled = round(40 * (perc / 100))
	nofill = 40 - filled
	percf = '%.2f' %perc + ' %'
	graph = tick * int(filled) + empty * int(nofill) + '  %7s' %percf
	return graph
	
def get_os_info(target): 
	
	global statuses
	
	get_status(target, 'all')
	rhnserver = get_rhn(target)
	tainted = taint_check(target)		
	selstate = sel_check(target)
	
	# load info from proc/stat - may separate this out later.
	with open(target + 'proc/stat', 'r') as statfile:
		num_cpus = -1  # to account for "cpu" on line 1, then leading into "cpuX"
		for line in statfile:
			if re.match("btime", line):
				btime = line.split(" ")[1]
				boottime = datetime.datetime.fromtimestamp(int(btime)).strftime('%a %b %d %H:%M:%S'\
				 + colors.WHITE + colors.BOLD + ' UTC ' + colors.ENDC + '%Y')
			if re.match("^cpu", line):
				num_cpus = num_cpus + 1
			if re.match("processes", line):
				num_procs = line.split(" ")[1].rstrip('\n')
			if re.match("procs_running", line):
				run_procs = line.split(" ")[1].rstrip('\n')
		if not boottime:
			boottime = colors.RED + 'Could not find boot time' + colors.ENDC
	

	loadavg = get_loadavg(target, num_cpus)	
				
	# from sys time and boot time calc uptime rather than butcher the uptime string more
	if boottime and btime and ('not found' not in statuses['systime']):
		sys = statuses['systime']			# Python strptime only works for timezone the 
		index = sys.find(sys.split()[-2])	# local computer is set to, so we need to strip the TZ
		systime = str(sys[0:index] + sys[index+3:len(sys)])
		systimesec = time.mktime(datetime.datetime.strptime(systime, "%a %b  %d %H:%M:%S %Y").timetuple())		
		uptime = str(datetime.timedelta(seconds=(int(systimesec) - int(btime))))
	else:
		uptime = colors.RED + colors.BOLD + 'Cannot determine uptime' + colors.ENDC

	# Print it all pretty like.
	print colors.SECTION + colors.BOLD + "OS " + colors.ENDC
	print colors.HEADER_BOLD + '\t Hostname  : ' + colors.ENDC + statuses['hostname']
	print colors.HEADER_BOLD +  '\t Release   : ' + colors.ENDC + statuses['release']
	print colors.HEADER_BOLD + '\t RHN Info  : ' + colors.ENDC + rhnserver
	print colors.HEADER_BOLD + '\t Runlevel  : ' + colors.ENDC + statuses['runlevel']
	print colors.HEADER_BOLD +  '\t SELinux   : ' + colors.ENDC + selstate
	
	print colors.HEADER_BOLD + '\t Kernel    : ' + colors.ENDC
	print '\t   ' + colors.BLUE + colors.BOLD + 'Booted kernel  : ' + colors.ENDC + str(statuses['kernel']).split(" ")[2]
	print '\t   ' + colors.BLUE + colors.BOLD + 'GRUB default   : '
	print '\t   ' + colors.BLUE + colors.BOLD + 'Booted cmdline : ' + colors.ENDC
	print '%15s' % ' ' + textwrap.fill(statuses['cmdline'], subsequent_indent='%15s' % ' ')
	print '\t   ' + colors.BLUE + colors.BOLD + 'Taint-check    : ' + colors.ENDC + str(tainted)
	
	print colors.GREEN + '%9s' % ' ' + colors.BOLD + '~ ' * 20 + colors.ENDC
	
	print colors.HEADER_BOLD  + '\t Sys time  : ' + colors.ENDC + statuses['systime']
	print colors.HEADER_BOLD  + '\t Boot time : ' + colors.ENDC + boottime
	print colors.HEADER_BOLD + '\t Uptime    : ' + colors.ENDC + uptime
	print colors.HEADER_BOLD + '\t Load Avg  : ' + colors.WHITE +'[%s CPUs] ' %(num_cpus) + colors.ENDC \
	 + loadavg
	print colors.HEADER_BOLD + '\t /proc/stat: ' + colors.ENDC
	print '\t   ' + colors.BLUE + colors.BOLD + 'procs_running : ' + colors.ENDC + run_procs + colors.BLUE + colors.BOLD + '   processes (since boot) : ' + colors.ENDC + num_procs

def check_mem(target, scope):				
	# check proc/meminfo for mem-related stats.
	# if scope is 'all', grab everything we care about at once
	if scope == 'all':
		if os.path.isfile(target + 'proc/meminfo'):
			with open(target + 'proc/meminfo', 'r') as meminfo:
				for line in meminfo:
					if 'MemTotal' in line:
						total_mem = round((int(line.split()[1]) / 1024), 2)
					if 'MemFree' in line:
						free_mem = round((int(line.split()[1]) / 1024), 2)
					if 'Buffers' in line:
						buffered_mem = round((int(line.split()[1]) / 1024), 2)
					if re.match ('^Cached:', line):
						cached_mem = round((int(line.split()[1]) / 1024), 2)
						cached_perc = (cached_mem / total_mem) * 100
					if 'HugePages_Total:' in line:
						hugepages = round(int(line.split()[1]) / 1024, 2)
						hugepage_perc = (hugepages / total_mem) * 100
					if 'Dirty:' in line:
						dirty_mem = round((int(line.split()[1]) / 1024), 2)
						dirty_perc = (dirty_mem / total_mem) * 100
					if 'Slab:' in line:
						slab = round((int(line.split()[1]) / 1024), 2)
						slab_perc = (slab / total_mem) * 100
					if 'SwapTotal:' in line:
						swap_total = round((int(line.split()[1]) / 1024), 2)
					if 'SwapFree:' in line:
						swap_free = round(int(line.split()[1]) / 1024, 2)
			if total_mem and free_mem:
				used_mem = round((total_mem - free_mem), 2)	
				perc_used = round(((used_mem / total_mem) * 100), 2)
			if swap_total and swap_free:
				swap_used = swap_total - swap_free
				swap_perc = (swap_used / swap_total) * 100	
			return used_mem, free_mem, total_mem, perc_used, hugepages, hugepage_perc,\
			dirty_mem, dirty_perc, slab, slab_perc, swap_total, swap_free, swap_used, swap_perc,\
			buffered_mem, cached_perc, cached_mem
	else:
		# need to build out selective mem check, if needed
		pass
		
def get_mem_info(target):
	
	# get all of our mem stats from check_mem
	used_mem, free_mem, total_mem, perc_used, hugepages, hugepage_perc, dirty_mem,\
	dirty_perc, slab, slab_perc, swap_total, swap_free, swap_used,\
	swap_perc, buffered_mem, cached_perc, cached_mem  = check_mem(target, 'all')
		
	# generate graphs for memory related stuff	
	usedgraph = graphit(perc_used)
	hugepagegraph = graphit(hugepage_perc)
	slabgraph = graphit(slab_perc)
	dirtygraph = graphit(dirty_perc)
	slabgraph = graphit(slab_perc)
	swapgraph = graphit(swap_perc)
	buffergraph = graphit(((buffered_mem / total_mem) * 100))
	cachedgraph = graphit(cached_perc)
	
	# print this all pretty
	print colors.SECTION + colors.BOLD + "Memory " + colors.ENDC
	print colors.HEADER + colors.BOLD + '\t Memory Statistics graphed : ' + colors.ENDC
	print colors.BLUE + '\t\t Used      : %8.2f GB ' %(used_mem / 1024) + usedgraph + colors.ENDC 
	print colors.PURPLE + '\t\t Buffered  : %8.2f GB ' %(buffered_mem / 1024) + buffergraph + colors.ENDC
	print colors.CYAN + '\t\t Cached    : %8.2f GB ' %(cached_mem / 1024) + cachedgraph + colors.ENDC
	print colors.GREEN + '\t\t Hugepages : %8s MB ' %hugepages + hugepagegraph + colors.ENDC
	print colors.RED + '\t\t Dirty     : %8s MB ' %dirty_mem + dirtygraph + colors.ENDC
	print colors.WHITE + '\t\t SLAB      : %8s MB ' %slab + slabgraph + colors.ENDC

	print colors.HEADER + colors.BOLD + '\t RAM  :' + colors.ENDC
	print '\t\t %6.2f GB total RAM on system' %(int(total_mem) / 1024)
	print colors.BLUE  + '\t\t %6.2f GB (%.2f %%) used' %((used_mem / 1024), perc_used) + colors.ENDC
	print colors.PURPLE + '\t\t %6.2f GB (%.2f %%) buffered' %((buffered_mem / 1024), ((buffered_mem / total_mem) * 100)) + colors.ENDC
	print colors.CYAN + '\t\t %6.2f GB (%.2f %%) cached' %((cached_mem / 1024), cached_perc) + colors.ENDC
	print colors.RED + '\t\t %6.2f MB (%.2f %%) dirty' %(dirty_mem, dirty_perc) + colors.ENDC
	
	print colors.HEADER + colors.BOLD + '\t Misc :'+ colors.ENDC
	print '\t\t %6s MB (%.2f %%) of total RAM used for SLAB' %(slab, slab_perc)
	print '\t\t %6s MB (%.2f %%) of total RAM used for Hugepages' %(hugepages, hugepage_perc)
	
	
	print colors.HEADER + colors.BOLD + '\t Swap :' + colors.ENDC
	print '\t\t %6s MB (%.2f %%) swap space used' %(swap_used, swap_perc)


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
	
def get_kernel_info(target):
	global statuses
	
	# get kexec version, service enablement, initrd.img, kdump path
	kexec_ver = find_rpm(target, 'kexec-tools')
	kdump_status = find_chkconfig(target, 'kdump')
	initrd = check_initrd(target)
	
	# cmdline setting for crashkernel
	if 'proc/cmdline' in statuses['cmdline']:
		cmdline = get_status(target, 'cmdline')
	else: 
		cmdline = statuses['cmdline']
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
		size = ''
		for item in config:
			if 'path' in item:
				crashpath = item.split()[1]
				index = crashpath.find('/')
				filesys = crashpath[index:(crashpath[index+1:len(crashpath)].find('/'))+1]
				mount_at = "/"
			with open(target + 'df', 'r') as df:
				for line in df:
					if line.endswith(filesys):	
						size = int(line.split()[1]) / 1024
						mount = '%s' %filesys
						break
	else:
		config.append(str(colors.WARN + 'kdump.conf not found' + colors.ENDC))
		mount_at = colors.WARN + 'Unknown' + colors.ENDC
		size = colors.WARN + 'Unknown' + colors.ENDC
	
	# find all panic related sysctl's, and split it up when we go to print it
	
	panic_ctl = find_sysctl(target, 'panic')	
						
	print colors.SECTION + colors.BOLD + 'Kdump ' + colors.ENDC
	print colors.HEADER_BOLD + '\t kexec-tools version : ' + colors.ENDC + kexec_ver
	print colors.HEADER_BOLD + '\t Service enablement  : ' + colors.ENDC + kdump_status
	print colors.HEADER_BOLD + '\t kdump initrd.img    : ' + colors.ENDC + initrd
	print colors.HEADER_BOLD + '\t Memory Reservation  : ' + colors.ENDC
	print colors.BLUE + colors.BOLD + '\t\t kernel arg   : ' + colors.ENDC + state
	print colors.BLUE + colors.BOLD + '\t\t GRUB conf    : ' + colors.ENDC
	print colors.HEADER_BOLD + '\t kdump.conf          : ' + colors.ENDC
	for item in config:
		print '\t\t\t        %s' %item
	print colors.BLUE + colors.BOLD + '\t\t path mount   : ' + colors.ENDC + mount_at
	print colors.BLUE + colors.BOLD + '\t\t avail space  : ' + colors.ENDC + size		
	print colors.HEADER_BOLD + '\t Kernel Panic sysctl : ' + colors.ENDC
	for item in panic_ctl:
		kern = colors.BLUE + colors.BOLD + item.split()[0] + colors.ENDC
		if item.split()[2] == '0':
			ctl = ' = 0 ' + '[disabled]' + colors.ENDC
		elif item.split()[2] == '1':
			
			ctl = ' = 1 ' + colors.BOLD + '[enabled]' + colors.ENDC
		else:
			ctl = item.split()[2]
		print '\t\t\t\t {:<31} {}'.format(item.split()[0], ctl)

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
					processors = processors + 1
				if 'model name' in line:
					cpu_model = line[index+2:len(line)].rstrip('\n')
				if line.startswith('physical'):
					phys_cpus = (int(line[index+2:len(line)].rstrip('\n')) + 1)
				if re.match('^cpu cores', line):
					core_count = line[index+2:len(line)].rstrip('\n')
				if line.startswith('siblings'):
					threads = line[index+2:len(line)].rstrip('\n')
				if line.startswith('flags'):
					cpu_flags = line[index+2:len(line)].rstrip('\n')
			if 'QEMU' in cpu_model:
				phys_cpus = '0 [virt] '
				core_count = processors
				threads = 1
		print colors.SECTION + colors.BOLD + 'CPU' + colors.ENDC
		print colors.WHITE + colors.BOLD + '\t\t %s logical processors' %processors + colors.ENDC
		print '\t\t %s %s processors' %(phys_cpus, cpu_model)
		print '\t\t %s cores / %s threads per physical processor' %(core_count, threads)
		print '\t\t flags : ' + textwrap.fill(cpu_flags, 80, subsequent_indent='%25s' % ' ')
	else:
		print 'Error parsing cpuinfo'
	
	
def find_sysctl(target, sysctl):
	sysctls = []
	if os.path.isfile(target +'sos_commands/kernel/sysctl_-a'):
		with open(target + 'sos_commands/kernel/sysctl_-a', 'r') as sysfile:
			for line in sysfile:
				if sysctl in line:
					sysctls.append(line.rstrip('\n'))
	return sysctls
	
def get_sysctl_info(target):
	# this is quite possibly the ugliest function ever written in python.
	# basically, we have a list of 'prints' that this function will parse over
	# if anything in the 'prints' lists is matched to an item in the overall sysctl
	# list, it gets printed. The function that does this, iterates over another list
	# which contains the name of the section, the sysctl list and the prints list.
	# horribly ineffecient, but the only way *I* could think of to properly iterate over
	# each section, while being able to print the section header and values without a separate
	# if clause to print the sysctls for each section.
	#
	# I'm so sorry.
	
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

def test_ip_info(target):
	interfaces = {}
	with open(target + 'ip_addr', 'r') as f:
	    lines = [line for line in f if line.strip()]
	    # group by line number
	    for key, group in groupby(lines, lambda x: x.split()[0]):
	        interface = []
	        for thing in group:
	            # append lines without repeating part
	            interface += thing.split()[2:]
	        if interface:
	            interfaces[key] = interface
	
	    for key, interface in interfaces.items():
	        for x in ['inet', 'inet6', 'state', 'link/ether']:
	            if x in interface:
	                idx = interface.index(x)
	                print '%s %s=%s' % (key, x, interface[idx+1])
							
def get_netdev_info(target):
	dev_info = {}
	with open(target +'proc/net/dev', 'r') as devfile:
		for line in devfile:
			if 'Inter' not in line:
				if ' face' not in line:
					index = line.find(':')
					key = line[0:index]
					dev_info[key] = line[index+1:len(line)].lstrip(' ').rstrip('\n')
					
		
	print colors.SECTION + 'Netdev' + colors.ENDC
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
		print '\t' + '{:<10}'.format(item) + tab + '%6.2f' % round(int(value[0]) / (1024 * 1024 * 1024), 2)\
		+ tab + ' %7.0f' % round((int(value[1]) / (1000000)), 2) + ' m' + tab + '{:>4}'.format(value[2])\
		+ tab + '{:>6}'.format(value[3]) + tab + '%7.2f' % round(int(value[8]) / (1024 * 1024 * 1024), 2)\
		+ tab + '  %7.0f' % round((int(value[9]) / (1000000 )), 2) + ' m' + tab + '{:>4}'.format(value[10])\
		+ tab + '{:>6}'.format(value[11]) + tab + '{:>6}'.format(value[12])
			
					
def get_ip_info(target):
	ip_ints = dict()
	for root, dirs, files in os.walk(target + 'etc/sysconfig/network-scripts'):
		for name in files:
			ipaddr = ''
			hwaddr = ''
			slaveof = ''
			device = ''
			if re.match('^ifcfg-', name):
				config_file = os.path.join(root, name)
				with open(config_file, 'r') as ipfile:
					for line in ipfile:
						line = line.rstrip('\n')
						index = line.find('=')
						if 'DEVICE=' in line or 'NAME=' in line:
							device = line[index+1:len(line)].lstrip('"').rstrip('"')
						if 'IPADDR=' in line:
							ipaddr = line[index+1:len(line)].lstrip('"').rstrip('"')
						if 'HWADDR=' in line:
							hwaddr = line[index+1:len(line)].lstrip('"').rstrip('"')
						if 'MASTER=' in line or 'BRIDGE=' in line :
							slaveof = line[index+1:len(line)].lstrip('"').rstrip('"')
					ip_ints[name] = [device,ipaddr,slaveof,hwaddr]	
	
	print colors.SECTION + colors.BOLD + 'IP ' + colors.ENDC
	print colors.WHITE + colors.BOLD + '\t {:^15}        {:^20}      {:^11}   {:^25}'.format('INT','IP ADDR', 'MEMBER OF','HW ADDR')
	print '\t' + '=' * 16 + ' ' * 6 + '=' * 23 + ' ' * 4 + '=' * 13 + ' ' * 5 + '=' * 19 + colors.ENDC
	for key in sorted(ip_ints):
		value = ip_ints[key]
		if 'eth' in value[0] or 'em' in value[0]:
			print '\t' + colors.BLUE + '{:<15s}'.format(value[0]) + colors.ENDC + '{:^36s}{:<16s} {:>11}'.format(value[1],value[2],value[3])
		elif 'vlan' in value[0]:
			print '\t' + colors.CYAN + '{:<15s}'.format(value[0]) + colors.ENDC + '{:^36s}{:<16s}  {:>11}'.format(value[1],value[2],value[3])
		elif 'bond' in value[0]:
			print '\t' + colors.GREEN + '{:<15s}'.format(value[0]) + colors.ENDC + '{:^36s}{:<16s}  {:>11}'.format(value[1],value[2],value[3])
		else:
			print '\t' + colors.PURPLE + '{:<15s}'.format(value[0]) + colors.ENDC + '{:^36s}{:<16s}  {:>11}'.format(value[1],value[2],value[3])
		
	
def get_bonding_info(target):
	bond_devs = {}
	for root, dirs, files in os.walk(target + 'proc/net/bonding'):
		for name in files:
			phys_devs = []
			hw_addrs = []
			with open(target + 'proc/net/bonding/' + name, 'r') as bfile:
				for line in bfile:
					index= line.find(':')
					if 'Bonding Mode:' in line:
						if '(round-robin)' in line:
							bond_mode = '0 (balance-rr)'
						elif '(active-backup)' in line:
							bond_mode = '1 (active backup)'
						elif '(xor)' in line:
							bond_mode = '2 (balance-xor)'
						elif '(broadcast)' in line:
							bond_mode = '3 (broadcast)'
						elif 'IEEE 802.3ad Dynamic link aggregation' in line:
							bond_mode = '4 (802.3ad - LACP)'
						elif 'transmit load balancing' in line:
							bond_mode = '5 (tlb)'
						elif 'adaptive load balancing' in line:
							bond_mode = '6 (alb)'
						else:
							bond_mode = line[index+1:len(line)]
					if 'Currently Active Slave' in line:
						active_dev = line[index+1:len(line)].rstrip('\n').lstrip(' ')
					if 'Slave Interface:' in line:
						dev = str(line[index+1:len(line)].rstrip('\n').lstrip(' '))
						try:
							if dev == active_dev:
								dev = dev + "*"
						except:
							pass
						phys_devs.append(dev)
						
					if 'Permanent HW addr' in line:
						hw_addrs.append(str(line[index+1:len(line)].rstrip('\n')))
					if os.path.isfile(target + 'etc/sysconfig/network-scripts/ifcfg-' + name):
						with open(target + 'etc/sysconfig/network-scripts/ifcfg-' + name, 'r') as bondfile:
							for line in bondfile:
								if 'BONDING_OPTS' in line or 'bonding_opts' in line:
									index = line.find('=')
									bond_opts = line[index+1:len(line)].lstrip("'").rstrip('\n')
									bond_opts = bond_opts.rstrip("'")
				try:
					bond_opts
				except:
					bond_opts = ''
				if not phys_devs:
					phys_devs.append(' [None]')
				if not hw_addrs:
					hw_addrs.append('')
				bond_devs[name] = (bond_mode, bond_opts, phys_devs, hw_addrs)
			
	print colors.SECTION + colors.BOLD + 'Bonding' + colors.ENDC
	print colors.WHITE + colors.BOLD + '\t {:^10}    {:^20}   {:^30}   {:^34}'.format('Device', 'Mode', 'BONDING_OPTS', 'Slave Interfaces')
	print '\t ' + '=' * 10 + '\t' + '=' * 19 + '\t  ' + '=' * 21 + '\t\t   ' + '=' * 26 + colors.ENDC
	for item in sorted(bond_devs):
		value = bond_devs[item]
		print colors.GREEN + '\t {:<10}'.format(item) + colors.ENDC + '     {:^20}'.format(value[0]) + '\t  {:<26}'.format(value[1]) + '{:>14} {:<18}'.format(value[2][0], value[3][0])
		dev_count = 1
		for each in value[2]:
			try: 
				if value[2][dev_count]:
					print '  {:>87}{:>20}'.format(value[2][dev_count], value[3][dev_count])
					dev_count = dev_count + 1
			except:
				print colors.PURPLE + '\t' * 10 + '   ' + '- ' * 10 + colors.ENDC


def get_ethtool_info(target):
	# get list of all devices
	dev_list = []
	dev_info = {}
	with open(target +'proc/net/dev', 'r') as devfile:
		for line in devfile:
			if 'Inter' not in line:
				if ' face' not in line:
					index = line.find(':')
					dev = str(line[0:index]).strip()
					if 'lo' not in dev:
						dev_list.append(dev)
						
	# for each device found, get ethtool reported info
	for device in dev_list:
		link_state, link_speed, an_state = get_full_eth(target, device)
		driver, drv_ver, firmware_ver = get_ethi_info(target, device)
		rxring, rxjumbo = get_ring_info(target, device)
		dev_info[device] = [link_state, link_speed, an_state, rxring, rxjumbo, driver, drv_ver, firmware_ver]
	print colors.SECTION + 'Ethtool' + colors.ENDC
	print colors.WHITE + colors.BOLD + '\t {:^10}    {:^20}  {:^8}  {:^15}   {:^15}'.format('Device', 'Link', 'Auto-Neg', 'Ring', 'Driver Info')
	print '\t ' + '=' * 10 + '\t ' + '=' * 17 + '  ' + '=' * 10 + '\t ' + '=' * 10 + '\t ' + '=' * 15 + colors.ENDC
	for item in sorted(dev_info):
		if ';' not in item:
			value = dev_info[item]
			if 'bond' in item:
				linecolor = colors.GREEN
			elif 'eth' in item or 'em' in item:
				linecolor = colors.BLUE
			else:
				linecolor = colors.PURPLE
			print '\t' + linecolor + item + '\t\t ' + '{:<8}'.format(value[0]) + '{:<9}'.format(value[1]) + '   {:3}'.format(value[2]) + '\t  %4s%3s' %(value[3], value[4]) + '\t  ' + '{:<8}'.format(value[5]) + ' ver: {:5}  fw: {:8}'.format(value[6], value[7])

def get_ring_info(target, device):
	rx = ''
	rxjumbo = ''
	if os.path.isfile(target + 'sos_commands/networking/ethtool_-g_' + device):
		with open(target + 'sos_commands/networking/ethtool_-g_' + device, 'r') as efile:
			for line in efile:
				if 'RX:' in line:
					rx = line.split()[1]
				if 'RX Jumbo:' in line:
					rxjumbo = line.split()[2]
	return rx, rxjumbo
			
def get_full_eth(target, device):
	link_speed = ''
	an_state = 'off'
	link_state = ''
	if os.path.isfile(target +  'sos_commands/networking/ethtool_' + device):
		with open(target + 'sos_commands/networking/ethtool_' + device, 'r') as efile:
			for line in efile:
				if 'Link detected: no' in line:
					link_state = 'UNKNOWN'
				if 'Link detected: yes' in line:
					link_state = 'UP'
				if 'Speed:' in line:
					link_speed = line.split()[1]
				if 'Auto-negotiation:' in line:
					an_state = line.split()[1]
	return link_state, link_speed, an_state
	
					
def get_ethi_info(target, device):
	driver = ''
	drv_ver = ''
	firmware_ver = 'unknown'
	if os.path.isfile(target +  'sos_commands/networking/ethtool_-i_' + device):
		with open(target + 'sos_commands/networking/ethtool_-i_' + device, 'r') as efile:
			for line in efile:
				if 'driver:' in line:
					driver = line.split()[1]
					driver = driver.strip()
				if re.match('^version:', line):

					try: 
						drv_ver = line.split()[1]
					except:
						drv_ver = ''
				if 'firmware-version:' in line:
					try:
						firmware_ver = line.split()[1]
					except:
						firmware_ver = 'unknown'
	return driver, drv_ver, firmware_ver							
	
#def getoffset(offset, v1, v2):
#	return offset + (len(v2) - len(v1))


def get_rhev_info(target):
	# grab / print basic information first
	print ""
	print colors.SECTION + colors.BOLD + "RHEV Information"
	#print colors.SECTION + colors.BOLD + "----------------"
	print ""

	# Find RHEVM rpm
	rhevm_ver = find_rpm(target, "rhevm-3")
	print colors.PURPLE + "\t Version: " + colors.GREEN + rhevm_ver
	
	# Find simplified version for debug purposes
	if "-3.0" in rhevm_ver:
		simpleVer = "3.0"
	elif "-3.1" in rhevm_ver:
		simpleVer = "3.1"
	elif "-3.2" in rhevm_ver:
		simpleVer = "3.2"
	else:
		simpleVer = "Could not be found"
		
	#logging.warning('Found the simplified version of rpm: ' + simpleVer) 
	
	# Try to find database
	database = False
	fullPath = os.path.abspath(target)
	
	#logging.warning('Using the following as fullpath variable: ' + fullPath)
	lcRoot = os.path.dirname(fullPath)
	
	#logging.warning('Using the following as lcRoot variable: ' + lcRoot)
	if os.path.isdir(lcRoot + "/database"):
		database = True
		dbDir = lcRoot + "/database"
		
	# The following is only possible if we found the db above
	if database:
		print colors.PURPLE + "\t Database: " + colors.GREEN +"Located"
		
		# Compensate for 3.0 / 3.x database differences
		if simpleVer == "3.1" or simpleVer == "3.2":
			# Eval manager before moving on to db analysis
			rhev_eval_mngr(dbDir)
		elif simpleVer == "3.0":
			print colors.WARN + "\t Not ready to parse 3.0 databases yet, may not be trustworthy!!"
		else:
			print colors.WARN + simpleVer
		
		# Move on to the database
		rhev_eval_db(dbDir)
		
	else:
		print colors.WARN + "Database not found"
		
		# Eval manager even without the database being found
		print ""
		rhev_eval_mngr(target)
	
	
# Method for evaulating the manager regardless of whether or not we find the database	
# This method should expect to receive the original target path, that is, path to sosreport of manager
def rhev_eval_mngr(target):
	#logging.warning('rhev_eval_mngr has been called, beginning eval...')
	print ""
	
# Method for evaluating the database for env information
# This method should expect to be passed the directory containing the database
def rhev_eval_db(dbDir):
	#logging.warning('rhev_eval_db has been called, beginning eval...')
	
	if os.path.exists(dbDir + "/sos_pgdump.tar"):
		dbTar = dbDir + "/sos_pgdump.tar"
		#logging.warning('Found dbdump: ' + dbTar)
		masterDB = Database(dbTar)

		# create data center list
		dc_list = masterDB.get_data_centers()
				
		#Print data center list
		#headerStr = '%2s '+ colors.BLUE + '%3s %4s %5s %6s' % ("Data Center Name","|","UUID","|","Compatibility Version")
		print colors.HEADER_BOLD
		print "\t {0:<18} {1:1} {2:^36} {3:1} {4:^22}".format("Data Center Name","|","UUID","|","Compatibility Version")
		print "\t "+"-"*83 + colors.GREEN
	
		for d in dc_list:
			#dc_details = d.split(",")
			print "\t {0:<18} {1:1} {2:^36} {3:1} {4:^22}".format(d.get_name(),"|",d.get_uuid(),"|",d.get_compat())
			
		print colors.ENDC
				
		####### End of Data Center Parsing #######
		
		sd_list = masterDB.get_storage_domains()
				
	
		#Print data center list
		#headerStr = '%2s '+ colors.BLUE + '%3s %4s %5s %6s' % ("Data Center Name","|","UUID","|","Compatibility Version")
		print colors.HEADER_BOLD + "\t {0:<21} {1:1} {2:^36} {3:1} {4:^12} {5:1} {6:^6}".format("Storage Domain Name","|","UUID","|","Storage Type","|","Master")
		print "\t "+"-"*85+colors.GREEN
		for d in sd_list:
			print d.get_name()
			#sd_details = d.split(",")
			print "\t {0:<21} {1:1} {2:^36} {3:1} {4:^12} {5:1} {6:^6}".format(d.get_name()[0],"|",d.get_uuid(),"|",d.get_storage_type(),"|",d.get_master())
			
		print colors.ENDC
	
	
		##
		# Find all hosts and store in list
		##
		
		host_list = []
		theFile = open(host_dat,"r")
		lines = theFile.readlines()
		
		hostDirs = []
		# look for all files in the parent of the passed 'dbDir', and if it is a dir then attempts to parse
		rootDir = os.path.dirname(dbDir)
		#print "rootDir: " + rootDir
		for d in os.listdir(rootDir):
			#print(rootDir+"/"+d)
			if os.path.isdir(rootDir+"/"+d):
				hostDirs.append(d)
				#print("Appending dir: "+d)
		
		for n in lines:
			vals = n.split("\t")
			if len(vals) >= 2:
				#print vals[1] + " - " + vals[0]
				host_uuid = vals[0]
				# determine if the host is SPM for a DC
				if host_uuid == spm_host:
					host_spm = "*"
				else:
					host_spm = ""
				host_name = vals[1]
				host_ip = vals[2]
				host_release = "unknown"
				
				# determine host type, 0 = rhel, 2 = rhev-h
				host_type = vals[8]					
				if host_type == "0":
					host_type = "RHEL"
				elif host_type == "2":
					host_type = "RHEV-H"
								
				# try and find release version
				hostDirName = host_name.split(".")
				for h in hostDirs:
					names = h.split("-")
					if names[0] == hostDirName[0]:
						# this is a stupid hack, using '..' in the path name. stop being lazy and find a better alternative
						releaseFile = open(dbDir+"/../"+h+"/etc/redhat-release")
						releaseVer = releaseFile.readlines()
						host_release = releaseVer[0].split("(")[1]
						# strip the newline character at the end of the line
						host_release = host_release.replace("\n","")
						host_release = host_release.rstrip(")")
						
				
				#the below tries to parse host folder names based on the patter: <hostname>_<time_of_sosreport>/
				
				#logging.warning(dc_name +","+dc_uuid+","+dc_compat)
				newHost = host_name+","+host_uuid+","+host_spm+","+host_type+","+host_release
				#logging.warning("Newest DC is: " + newDC)
				host_list.append(newHost)
		
		#Print data center list
		#headerStr = '%2s '+ colors.BLUE + '%3s %4s %5s %6s' % ("Data Center Name","|","UUID","|","Compatibility Version")
		print colors.HEADER_BOLD + "\t {0:<20} {1:1} {2:^36} {3:1} {4:^6} {5:1} {6:^18} {7:1} {8:^5}".format("Host Name","|","UUID","|","Type","|","Release","|","SPM")
		print "\t "+"-"*98+colors.GREEN
		for d in host_list:
			host_details = d.split(",")
			print "\t {0:<20} {1:1} {2:^36} {3:1} {4:^6} {5:1} {6:^18} {7:1} {8:^5}".format(host_details[0],"|",host_details[1],"|",host_details[3],"|",host_details[4],"|",host_details[2])
			
		print colors.ENDC
		
		
	else:
		print colors.WARN + "Could not find a database file"
		
# Finds relevant files after dbdump has been extracted
def findDat(table,restFile):
	'''
	Subroutine to find the dat file name in restore.sql
	''' 
	openFile = open(restFile, "r")
	lines = openFile.readlines()
	
	# print "Looking for " + table
	
	for n in lines:
		if n.find(table) != -1:
			if n.find("dat") != -1:
				datInd = n.find("PATH")
				datFileName =  n[datInd+7:datInd+15]
				if datFileName.endswith("dat"):
					#print "Found dat line for " + table
					#logging.warning('Return dat file: ' +datFileName)
					return datFileName
	
	return -1
    
def get_main(os, mem, kdump, cpu, sysctl, ip, bonding, test, netdev, rhev, eth, target):
	if os:
		get_os_info(target)
	if mem:
		get_mem_info(target)
	if kdump:
		get_kernel_info(target)
	if cpu:
		get_cpu_info(target)
	if sysctl:
		get_sysctl_info(target)
	if ip:
		get_ip_info(target)
	if bonding:
		get_bonding_info(target)
	if test:
		test_ip_info(target)
	if netdev:
		get_netdev_info(target)
	if rhev:
		get_rhev_info(target)
	if eth:
		get_ethtool_info(target)		
			
			
target = args.target[0]
if not target.endswith('/'):
	target = target + '/'

get_main(args.os, args.memory, args.kdump, args.cpu, args.sysctl, args.ip\
, args.bonding, args.test, args.netdev, args.rhev, args.ethtool, target)

