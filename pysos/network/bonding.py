import os
from config import *

def get_bonding_info(target):
	bond_devs = {}
	for root, dirs, files in os.walk(target + 'proc/net/bonding'):
		for name in files:
			phys_devs = []
			hw_addrs = []
			with open(target + 'proc/net/bonding/' + name, 'r') as bfile:
				for line in bfile:
					index= line.find(':')
					if 'Bonding Mode:' in line:
						if '(round-robin)' in line:
							bond_mode = '0 (balance-rr)'
						elif '(active-backup)' in line:
							bond_mode = '1 (active backup)'
						elif '(xor)' in line:
							bond_mode = '2 (balance-xor)'
						elif '(broadcast)' in line:
							bond_mode = '3 (broadcast)'
						elif 'IEEE 802.3ad Dynamic link aggregation' in line:
							bond_mode = '4 (802.3ad - LACP)'
						elif 'transmit load balancing' in line:
							bond_mode = '5 (tlb)'
						elif 'adaptive load balancing' in line:
							bond_mode = '6 (alb)'
						else:
							bond_mode = line[index+1:len(line)]
					if 'Currently Active Slave' in line:
						active_dev = line[index+1:len(line)].rstrip('\n').lstrip(' ')
					if 'Slave Interface:' in line:
						dev = str(line[index+1:len(line)].rstrip('\n').lstrip(' '))
						try:
							if dev == active_dev:
								dev = dev + "*"
						except:
							pass
						phys_devs.append(dev)
						
					if 'Permanent HW addr' in line:
						hw_addrs.append(str(line[index+1:len(line)].rstrip('\n')))
					if os.path.isfile(target + 'etc/sysconfig/network-scripts/ifcfg-' + name):
						with open(target + 'etc/sysconfig/network-scripts/ifcfg-' + name, 'r') as bondfile:
							for line in bondfile:
								if 'BONDING_OPTS' in line or 'bonding_opts' in line:
									index = line.find('=')
									bond_opts = line[index+1:len(line)].lstrip("'").rstrip('\n')
									bond_opts = bond_opts.rstrip("'")
				try:
					bond_opts
				except:
					bond_opts = ''
				if not phys_devs:
					phys_devs.append(' [None]')
				if not hw_addrs:
					hw_addrs.append('')
				bond_devs[name] = (bond_mode, bond_opts, phys_devs, hw_addrs)
			
	print colors.SECTION + colors.BOLD + 'Bonding' + colors.ENDC
	print colors.WHITE + colors.BOLD + '\t {:^10}    {:^20}   {:^30}   {:^34}'.format('Device', 'Mode', 'BONDING OPTS', 'Slave Interfaces')
	print '\t ' + '=' * 10 + '\t' + '=' * 19 + '\t  ' + '=' * 21 + '\t\t   ' + '=' * 26 + colors.ENDC
	for item in sorted(bond_devs):
		value = bond_devs[item]
		print colors.GREEN + '\t {:<10}'.format(item) + colors.ENDC + '     {:^20}'.format(value[0]) + '\t  {:<26}'.format(value[1]) + '{:>14} {:<18}'.format(value[2][0], value[3][0])
		dev_count = 1
		for each in value[2]:
			try: 
				if value[2][dev_count]:
					print '  {:>87}{:>20}'.format(value[2][dev_count], value[3][dev_count])
					dev_count += 1
			except:
				print colors.PURPLE + '\t' * 10 + '   ' + '- ' * 10 + colors.ENDC
