import os

def find_rpm(target, rpm, local=False):
	
	# from here we will pull specific targets for installed RPMS
	rpm_state = False
	if local:
		import tempfile, subprocess
		temp_file = tempfile.NamedTemporaryFile(delete=False)
		command = subprocess.Popen(['rpm', '-qa', rpm], stdout=subprocess.PIPE)
		output = command.stdout.read()
		for line in output:
			temp_file.write(line)
		temp_file.close()
		rpm_file = temp_file.name
		
	else:
		rpm_file = target + 'installed-rpms'
			
	if os.path.isfile(rpm_file):
		with open(rpm_file, 'r') as rpmfile:
			for line in rpmfile:
				if line.startswith(rpm):
					index = line.find('.')
					this_rpm = line[0:index-2]
					if this_rpm == rpm:
						rpm_state = line.split()[0]
			
		if not rpm_state:
			return 'not installed'
		else:
			return rpm_state
	else:
		return 'installed-rpms not found'
	
	try:
		os.remove(temp_file.name)
	except:
		pass	
