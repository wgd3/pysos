from rhn import *
from config import *

def get_yum_info(target, local):
	server = get_rhn(target, local)
	channels = get_rhn(target, local, channels=True)

	print colors.SECTION + 'Channel Info' + colors.ENDC
	print ''
	print colors.HEADER_BOLD + '\t Server   : ' + colors.ENDC + server
	print colors.HEADER_BOLD + '\t Channels : ' + colors.ENDC
	for channel in channels:
		print '\t\t    {:40} {:<20}'.format(channel,channels[channel].strip())
		
