import os,re
from config import *

def graphit(perc):
	
	# general graphing function, needs to be fed a percentage. 
	tick = u"\u25C6"
	empty = u"\u25C7"	
	filled = round(40 * (perc / 100))
	nofill = 40 - filled
	percf = '%.2f' %perc + ' %'
	graph = tick * int(filled) + empty * int(nofill) + '  %7s' %percf
	return graph
		
def get_mem_info(target):
	
	# get all of our mem stats from check_mem
	if os.path.isfile(target + 'proc/meminfo'):
		with open(target + 'proc/meminfo', 'r') as meminfo:
			for line in meminfo:
				if 'MemTotal' in line:
					total_mem = round((int(line.split()[1]) / 1024), 2)
				if 'MemFree' in line:
					free_mem = round((int(line.split()[1]) / 1024), 2)
				if 'Buffers' in line:
					buffered_mem = round((int(line.split()[1]) / 1024), 2)
				if re.match ('^Cached:', line):
					cached_mem = round((int(line.split()[1]) / 1024), 2)
					cached_perc = (cached_mem / total_mem) * 100
				if 'HugePages_Total:' in line:
					hugepages = round(int(line.split()[1]) / 1024, 2)
					hugepage_perc = (hugepages / total_mem) * 100
				if 'Dirty:' in line:
					dirty_mem = round((int(line.split()[1]) / 1024), 2)
					dirty_perc = (dirty_mem / total_mem) * 100
				if 'Slab:' in line:
					slab = round((int(line.split()[1]) / 1024), 2)
					slab_perc = (slab / total_mem) * 100
				if 'SwapTotal:' in line:
					swap_total = round((int(line.split()[1]) / 1024), 2)
				if 'SwapFree:' in line:
					swap_free = round(int(line.split()[1]) / 1024, 2)
		if total_mem and free_mem:
			used_mem = round((total_mem - free_mem), 2)	
			perc_used = round(((used_mem / total_mem) * 100), 2)
		if swap_total and swap_free:
			swap_used = swap_total - swap_free
			swap_perc = (swap_used / swap_total) * 100
		else:
			swap_used = 0
			swap_perc = 0	
		try:
			hugepages
		except:
			hugepages = 0
			hugepage_perc = 0
		
	# generate graphs for memory related stuff	
	usedgraph = graphit(perc_used)
	hugepagegraph = graphit(hugepage_perc)
	slabgraph = graphit(slab_perc)
	dirtygraph = graphit(dirty_perc)
	slabgraph = graphit(slab_perc)
	swapgraph = graphit(swap_perc)
	buffergraph = graphit(((buffered_mem / total_mem) * 100))
	cachedgraph = graphit(cached_perc)
	
	print colors.SECTION + colors.BOLD + "Memory " + colors.ENDC
	print colors.HEADER + colors.BOLD + '\t Memory Statistics graphed : ' + colors.ENDC
	print colors.BLUE + '\t\t Used      : %8.2f GB ' %(used_mem / 1024) + usedgraph + colors.ENDC 
	print colors.PURPLE + '\t\t Buffered  : %8.2f GB ' %(buffered_mem / 1024) + buffergraph + colors.ENDC
	print colors.CYAN + '\t\t Cached    : %8.2f GB ' %(cached_mem / 1024) + cachedgraph + colors.ENDC
	print colors.WHITE + '\t\t Swap      : %8.2f MB ' % swap_used + swapgraph + colors.ENDC
	print colors.GREEN + '\t\t Hugepages : %8s MB ' %hugepages + hugepagegraph + colors.ENDC
	print colors.RED + '\t\t Dirty     : %8s MB ' %dirty_mem + dirtygraph + colors.ENDC
	print '\t\t SLAB      : %8s MB ' %slab + slabgraph 

	print colors.HEADER + colors.BOLD + '\t RAM  :' + colors.ENDC
	print '\t\t %6.2f GB total RAM on system' %(int(total_mem) / 1024)
	print colors.BLUE  + '\t\t %6.2f GB (%.2f %%) used' %((used_mem / 1024), perc_used) + colors.ENDC
	print colors.PURPLE + '\t\t %6.2f GB (%.2f %%) buffered' %((buffered_mem / 1024), ((buffered_mem / total_mem) * 100)) + colors.ENDC
	print colors.CYAN + '\t\t %6.2f GB (%.2f %%) cached' %((cached_mem / 1024), cached_perc) + colors.ENDC
	print colors.RED + '\t\t %6.2f MB (%.2f %%) dirty' %(dirty_mem, dirty_perc) + colors.ENDC
	
	print colors.HEADER + colors.BOLD + '\t Misc :'+ colors.ENDC
	print '\t\t %6s MB (%.2f %%) of total RAM used for SLAB' %(slab, slab_perc)
	print colors.GREEN + '\t\t %6s MB (%.2f %%) of total RAM used for Hugepages' %(hugepages, hugepage_perc) + colors.ENDC
	
	
	print colors.HEADER + colors.BOLD + '\t Swap :' + colors.ENDC
	print colors.WHITE + '\t\t %6.2f GB defined  swap space ' %(swap_total / 1024) + colors.ENDC
	print colors.WHITE + '\t\t %6.2f MB (%.2f %%) swap space used ' %(swap_used, swap_perc) + colors.ENDC

