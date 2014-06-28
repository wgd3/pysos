
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
	
