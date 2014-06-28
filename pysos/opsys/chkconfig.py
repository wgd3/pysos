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
