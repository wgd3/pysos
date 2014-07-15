import json, urllib2

def check_rpm_ver(rpm, stand_alone=False, all_test=False, name=False, ver=False):

	if not name:
		index = rpm.find('.')
		rpmname = rpm[0:index-1]
	else:
		rpmname = name
	
	if not ver:
		version = rpm[len(rpmname):len(rpm)]
	
	else:
		version = ver
		
	base_url = "http://pysosweb-wdaniel.itos.redhat.com/"
	check_url = base_url + 'check/' + rpmname.strip('-') + '/' + version
	
	try:
		rpm_check = urllib2.urlopen(check_url)
	except:
		if stand_alone:
			return 'Cannot query pysosweb'
		else:		
			return False
	data = json.load(rpm_check)
	status = data['status']
	if stand_alone:
				
		if status == 'success':
			bz = data['bz']
			kcs = data['kcs']
			warning = data['warning']
			return [warning, kcs, bz]
		elif 'fail' in status:
			return 'No entries found'
		else:
			return 'Invalid RPM'
	elif all_test:
		if status == 'success':
			bz = data['bz']
			kcs = data['kcs']
			warning = data['warning']
			return [warning, kcs, bz]
		else:
			return False	
	else:
		if status == 'success':
			bz = data['bz']
			kcs = data['kcs']
			warning = data['warning']
			return [warning, kcs, bz]
		else:
			return False
