import sys;

coms = {}
out = open(sys.argv[2], "w")

for line in file(sys.argv[1]): 
    nid = int(line.split('\t')[0])
   
    for cid in line.split('\t')[1].split():
 	if not coms.has_key(cid):
		coms[cid] = []
   
	coms[cid].append(nid);

for c in coms.values():
    out.write(" ".join(map(str, c)) + "\n");
