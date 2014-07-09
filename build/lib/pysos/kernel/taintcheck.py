from collections import OrderedDict

def taint_check(target):
	
	# check for kernel taint, well known values go in this dictionary
	t=OrderedDict()
	t['536870912']="Technology Preview code is loaded"
	t['268435456']="Hardware is unsupported"
	t['4096']="Out-of-tree module has been loaded"
	t['2048']="Working around severe firmware bug"
	t['1024']="Modules from drivers/staging are loaded"
	t['512']="Taint on warning"
	t['256']="ACPI table overridden"
	t['128']="Kernel has oopsed before"
	t['64']="Userspace-defined naughtiness"
	t['32']="System has hit bad_page"
	t['16']="System experienced a machine check exception"
	t['8']="User forced a module unload"
	t['4']="SMP with CPUs not designed for SMP"
	t['2']="Module has been forcibly loaded"
	t['1']="Proprietary module has been loaded"
	t['0']="Not tainted. Hooray!"
	

	with open(target + 'proc/sys/kernel/tainted', 'r') as tfile:
		check = tfile.read().splitlines()
		check = check[0]
		if check in t:
			return t[check]
		else:
			check = int(check)
			taint_string = ' '
			for key in t:
				if int(check) - int(key) > int('-1'):
					taint_string = taint_string + t[key] + '\n\t\t\t     '
					check = int(check) - int(key)
					if check == 0:
						return taint_string
				else:
					pass
			# we should only hit this if we have an undefined taint code remainder from the above
			return taint_string + '\n\t\t\t     Undefined taint code: %s' %str(check)


