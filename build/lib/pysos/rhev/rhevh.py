from opsys import *
import os

def get_rhev_hyp_info(target):
		packages = {}
		rpm_check = {}
		vm_list = []
		running_vms = 0
		warn_count = 0
		rhevh_release = get_status(target, 'release')
		packages['kernel'] = get_status(target, 'kernel').split()[2]
		
		# Find package versions
		packages['vdsm'] = find_rpm(target, 'vdsm')
		packages['libvirt'] = find_rpm(target, 'libvirt')
		packages['spice'] = find_rpm(target, 'spice-server')
		packages['qemu_img'] = find_rpm(target, 'qemu-img-rhev')
		packages['qemu_kvm'] = find_rpm(target, 'qemu-kvm-rhev')
		packages['qemu_tools'] = find_rpm(target, 'qemu-kvm-rhev-tools')
		
		# Check RPM versions.
		
		for each in packages:
			rpm_check[each] = check_rpm_ver(packages[each])
		
		# Format package results				
		for item in packages:
			if 'not installed' in packages[item]:
				packages[item] = 'Not Installed'
			else:
				index = str(packages[item]).find('.')
				index2 = str(packages[item]).find('.x86')
				packages[item] = str(packages[item])[index-1:index2]

		# check pysos-web for known hypervisor ISO issues
		if 'Hypervisor' in rhevh_release:
			packages['hypervisor'] = rhevh_release[(rhevh_release.find('(')) +1:rhevh_release.find('.el6)')]
			rpm_check['hypervisor'] = check_rpm_ver('', name='rhev-hypervisor', ver=packages['hypervisor'])	
		
		for item in rpm_check:
			if rpm_check[item]:
				warn_count += 1
		
		# get number of VMs running on this hypervisor currently
		if os.path.isfile(target + 'ps'):
			with open(target + 'ps', 'r') as psfile:
				for line in psfile:
					if '/usr/libexec/qemu-kvm ' in line:
						running_vms += 1
						index = line.find('-name')
						index2 = line.find("-S -M")
						vm_name = str(line[index+6:index2]).strip()
						vm_mem =str(round((int(line.split()[5]) / 1048576), 0))
						vm_cpu = line.split()[2]
						vm_list.append([vm_name, vm_cpu, vm_mem])
		
		
		print colors.SECTION + 'Virtualization'
		print colors.HEADER_BOLD + '\t Release    : ' + colors.ENDC + rhevh_release
		print colors.HEADER_BOLD + '\t Kernel     : ' + colors.ENDC + packages['kernel']
		print ''
		print colors.HEADER_BOLD + '\t vdsm       : ' + colors.ENDC + packages['vdsm'] + '\t' + \
		colors.HEADER_BOLD + '\t\t libvirt    : ' + colors.ENDC + packages['libvirt']
		print colors.HEADER_BOLD + '\t SPICE      : ' + colors.ENDC + packages['spice'] + '\t\t' + \
		colors.HEADER_BOLD + '\t RHEV tools : ' + colors.ENDC + packages['qemu_tools']
		print colors.HEADER_BOLD + '\t qemu-img   : ' + colors.ENDC + packages['qemu_img']+ '\t' + \
		colors.HEADER_BOLD + '\t qemu-kvm   : ' + colors.ENDC + packages['qemu_kvm']
		print ''

		if warn_count > 0:
			print colors.RED + colors.BOLD + '\t WARNING : ' + colors.ENDC 
			for item in rpm_check:
				if rpm_check[item]:
					print '\t\t {:10} {:10}: {:<30} '.format(item, packages[item], str(rpm_check[item][0]).rstrip('\n'))
					print '\t\t\t KCS : ' + colors.WHITE + '{} '.format(rpm_check[item][1]) + colors.ENDC + '\tBZ : ' + colors.WHITE + \
					'{}'.format(rpm_check[item][2]) + colors.ENDC
		
		print ''			
		print colors.HEADER_BOLD + '\t Running VMs on this host : ' +colors.ENDC + str(running_vms) + '\t CPU/RSS usage in ()'
		vm_list.sort()
		rows = math.ceil(len(vm_list) / 5)
		for number in range(0, int(rows)):
			to_print = []
			for i in range(0, 5):
				try:
					to_print.append(vm_list[4-i])
					
					vm_list.remove(vm_list[4-i])
				except:
					to_print.append('')			
			print '\t ' + print_vms(to_print[4]) + print_vms(to_print[3]) + print_vms(to_print[2]) + print_vms(to_print[1]) + print_vms(to_print[0])

def print_vms(to_print):
	try:
		return colors.GREEN + ' {:12} '.format(to_print[0][:12]) + colors.ENDC + '({:4}% / {:4}GB)'.format(to_print[1], to_print[2])
	except:
		return ''
