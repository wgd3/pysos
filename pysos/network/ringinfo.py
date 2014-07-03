import os

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
