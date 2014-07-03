from rhn import *
from kernel import *
from selcheck import *
from loadavg import *
from config import *
from getstats import *
import os, time, textwrap

def get_os_info(target, local): 
	
	rhnserver = get_rhn(target, local)
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
				num_cpus += 1
			if re.match("processes", line):
				num_procs = line.split(" ")[1].rstrip('\n')
			if re.match("procs_running", line):
				run_procs = line.split(" ")[1].rstrip('\n')
		if not boottime:
			boottime = colors.RED + 'Could not find boot time' + colors.ENDC
	

	loadavg = get_loadavg(target, num_cpus, local)	
	sys = get_status(target, 'date', local)			
	# from sys time and boot time calc uptime rather than butcher the uptime string more
	if boottime and btime and ('not found' not in sys):         
											# Python strptime only works for timezone the 
		index = sys.find(sys.split()[-2])	# local computer is set to, so we need to strip the TZ
		systime = str(sys[0:index] + sys[index+3:len(sys)])
		systimesec = time.mktime(datetime.datetime.strptime(systime, "%a %b  %d %H:%M:%S %Y").timetuple())		
		uptime = str(datetime.timedelta(seconds=(int(systimesec) - int(btime))))
	else:
		uptime = colors.RED + colors.BOLD + 'Cannot determine uptime' + colors.ENDC

	# Print it all pretty like.
	print colors.SECTION + colors.BOLD + "OS " + colors.ENDC
	print colors.HEADER_BOLD + '\t Hostname  : ' + colors.ENDC + get_status(target, 'hostname', local)
	print colors.HEADER_BOLD +  '\t Release   : ' + colors.ENDC + get_status(target, 'release', local)
	print colors.HEADER_BOLD + '\t RHN Info  : ' + colors.ENDC + rhnserver
	print colors.HEADER_BOLD + '\t Runlevel  : ' + colors.ENDC + get_status(target, 'runlevel', local)
	print colors.HEADER_BOLD +  '\t SELinux   : ' + colors.ENDC + selstate
	
	print colors.HEADER_BOLD + '\t Kernel    : ' + colors.ENDC
	print '\t   ' + colors.BLUE + colors.BOLD + 'Booted kernel  : ' + colors.ENDC + str(get_status(target, 'kernel', local)).split(" ")[2]
	print '\t   ' + colors.BLUE + colors.BOLD + 'GRUB default   : '
	print '\t   ' + colors.BLUE + colors.BOLD + 'Booted cmdline : ' + colors.ENDC
	print '%15s' % ' ' + textwrap.fill(get_status(target, 'cmdline', local), 90, subsequent_indent='%15s' % ' ')
	print '\t   ' + colors.BLUE + colors.BOLD + 'Taint-check    : ' + colors.ENDC + str(tainted)
	
	print colors.GREEN + '%9s' % ' ' + colors.BOLD + '~ ' * 20 + colors.ENDC
	
	print colors.HEADER_BOLD  + '\t Boot time : ' + colors.ENDC + boottime
	print colors.HEADER_BOLD  + '\t Sys time  : ' + colors.ENDC + sys
	print colors.HEADER_BOLD + '\t Uptime    : ' + colors.ENDC + uptime
	print colors.HEADER_BOLD + '\t Load Avg  : ' + colors.WHITE +'[%s CPUs] ' %(num_cpus) + colors.ENDC \
	 + loadavg
	print colors.HEADER_BOLD + '\t /proc/stat: ' + colors.ENDC
	print '\t   ' + colors.BLUE + colors.BOLD + 'procs_running : ' + colors.ENDC + run_procs + colors.BLUE + colors.BOLD + '   processes (since boot) : ' + colors.ENDC + num_procs
