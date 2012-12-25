import sys;

coms = {}
out = open(sys.argv[2], "w")

for line in file(sys.argv[1]):
    node = int(line.split()[0]) 
    cid = int(line.split()[1])
    
    if not coms.has_key(cid):
	coms[cid] = []
    
    coms[cid].append(node);

for c in coms.values():
    out.write(" ".join(map(str, c)) + "\n");
