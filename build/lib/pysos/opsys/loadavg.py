from config import *

def get_loadavg(target, cpus, local):
	
	if local:
		mem_file = tempfile.NamedTemporaryFile(delete=False)
		command = subprocess.Popen('uptime', stdout=subprocess.PIPE)
		output = command.stdout.read()
		for line in output:
			mem_file.write(line)
		mem_file.close()
		load_file = mem_file.name
	else:
		load_file = target + 'uptime'
		
	# get raw loadavg report from sosreport
	with open(load_file, 'r') as lfile:
		load = lfile.readline()
		index = load.find('e:')
		loadavg = load[index+2:len(load)].rstrip('\n')
		
	# now, calculate percent load from the string
	loads = loadavg.split(',')
	for item in loads:
		index = loads.index(item)
		loadperc = (float(item) / cpus) * 100
		if loadperc < 75:
			loads[index] = (loads[index] + colors.DBLUE + '(%.2f%%)' + colors.ENDC) %loadperc
		elif loadperc > 74 and loadperc < 100:
			loads[index] = (loads[index] + colors.WARN + '(%.2f%%)' + colors.ENDC) %loadperc
		else:
			loads[index] = (loads[index] + colors.RED + colors.BOLD + '(%.2f%%)' + colors.ENDC) %loadperc
	return str(loads[0] + loads[1] + loads[2])
	
	try:
		os.remove(mem_file.name)
	except:
		pass
