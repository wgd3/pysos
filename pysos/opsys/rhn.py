def get_rhn(target, local):
	if os.path.isfile(target + 'etc/sysconfig/rhn/up2date'):
		with open(target + 'etc/sysconfig/rhn/up2date', 'r') as rhnfile:
			for line in rhnfile:
				if re.match('^serverURL=.*', line):
					return line.rstrip('\n')
	else:
		return colors.WARN + 'Up2date file not found' + colors.ENDC
