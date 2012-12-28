#include "FuzGreedy.h"

FuzGreedy::FuzGreedy(MTRand *RR, int nnode, double deg, Node **node) :Greedy(RR, nnode, deg, node) {
}

void FuzGreedy::initFromFile(const char* input_coms_path, map<int, int>& id2ind) {
      
    ifstream coms_file(input_coms_path);
    istringstream ss;
    string line;
    string buf;
    
    int comId = 0;
    
    while(getline(coms_file, line) != NULL){
      ss.clear();
      ss.str(line);
      
      while(ss >> buf != NULL) {
	int nodeId = atoi(buf.c_str());
	buf.clear();
	node[id2ind[nodeId]]->modIds.insert(comId);
      }
      comId++;
    }
    
    Nmod = comId;
}
