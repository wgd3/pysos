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
	
	# add logic for stacked codes later
	with open(target + 'proc/sys/kernel/tainted', 'r') as tfile:
		check = tfile.read().splitlines()
		if check[0] in t:
			return t[check[0]]
		else:
			return 'Undefined taint code : %s' %check[0]
