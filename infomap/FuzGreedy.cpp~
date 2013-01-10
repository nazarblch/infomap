#include "FuzGreedy.h"

FuzGreedy::FuzGreedy(MTRand *RR, int nnode, double deg, Node **node) :Greedy(RR, nnode, deg, node) {
}

void FuzGreedy::initFromFile(const char* input_coms_path, map<int, int>& id2ind) {
      
    ifstream coms_file(input_coms_path);
    istringstream ss;
    string line;
    string buf;
    
    int comId = 0;
    
    for (int i = 0; i < Nnode; i++) {
        node[i]->modIds.clear();
    }
    
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
    
    for (int i = 0; i < Nnode; i++) {
        node[i]->set_equal_ModsPr();
    }
    
    for(int i = 0 ;i < Nnode; i++){
       node[i]->refresh_degree();
    }

   
    tune();
    tune();
    tune();

   
    tune();
}



void FuzGreedy::move(bool &moved){
  
  //check_invariants();

  vector<int> randomOrder = randomPermutation(Nnode);
  
  for(int k = 0; k < Nnode; k++){
    
    int curNodeId = randomOrder[k]; 
    Node* curNode = node[curNodeId];
    
    NodeModLinks nm_links;
    calcWtoNbMods(curNode, nm_links);
       	 
    vector<pair<int, double> > wToClusterVec(nm_links.wToCluster.begin(), nm_links.wToCluster.end());
    
    // Option to move to empty module (if node not already alone)
    if(Nempty > 0 && nm_links.wToCluster.find(mod_empty[Nempty-1]) == nm_links.wToCluster.end()) {
        wToClusterVec.push_back(make_pair(mod_empty[Nempty-1], 0.0));
	nm_links.wToClusterWithPr[mod_empty[Nempty-1]] = 0.0;
    }
    
    wToClusterVec = randomPermutation(wToClusterVec);

    double best_delta = 0.0;
    int fromM = -1;
    int bestM = -1;
    
    
    
    // Find the move that minimizes the description length
    for (vector<pair<int, double> >::iterator ind_w = wToClusterVec.begin(); ind_w < wToClusterVec.end(); ind_w++) {
      
      int toM = ind_w->first;
      double wtoMwithPr = nm_links.wToClusterWithPr[toM];
      
      if(curNode->modIds.find(toM) != curNode->modIds.end()) continue;
	
      double deltaLAdd = deltaCodeLengthAdd(curNodeId, toM, nm_links);
      //check_invariants();
      double deltaLSwap = deltaCodeLengthSwap(curNodeId, toM, nm_links, fromM);
      
      
      if(min(deltaLAdd, deltaLSwap) < best_delta){
          bestM = toM;
          best_delta = min(deltaLAdd, deltaLSwap);  
	  
	  if (deltaLAdd < deltaLSwap) {
	    fromM = -1;
	  }
	  
	  moved = true;
      }
      
    }
    
    if (bestM != -1) {
      addNodeToModule(bestM, curNode, nm_links);
      
      if (fromM != -1) {
	  removeNodeFromModule(fromM, curNode, nm_links);
      }  		
    }
    
    //tune();
		
  }	
  tune();
}

double FuzGreedy::multPlogP(double deg, int count) {
  
  double res = 0.0;
  
  for (int i = 0; i < count; i++) {
    res += plogp(deg/count);
  }
  
  return res;
  
}

double FuzGreedy::deltaCodeLengthAdd(int curNodeId, int toM, NodeModLinks& nm_links) {
  
   Node* curNode = node[curNodeId];
   
   addNodeToModule(toM, curNode, nm_links);
  
   double newL = codeLength;
   
   removeNodeFromModule(toM, curNode, nm_links);
   
   return newL - codeLength;
}


double FuzGreedy::deltaCodeLengthDel(int curNodeId, int toM, NodeModLinks& nm_links) {
   
   Node* curNode = node[curNodeId];
   
   removeNodeFromModule(toM, curNode, nm_links);
   
   double newL = codeLength;
   
   addNodeToModule(toM, curNode, nm_links);
   
   return newL - codeLength;
}

double FuzGreedy::deltaCodeLengthSwap(int curNodeId, int toM, NodeModLinks& nm_links, int& fromM) {
   
   Node* curNode = node[curNodeId];
   set<int> parentModIds = node[curNodeId]->modIds;
   
   double LBeforeAdd = codeLength;
   
   addNodeToModule(toM, curNode, nm_links);
  
   double deltaLAfterAdd = codeLength - LBeforeAdd;
   
   double deltaLAfterSwapBest = 10;
   
   for (set<int>::iterator mod_id = parentModIds.begin(); mod_id != parentModIds.end(); mod_id++) {
      double deltaLAfterSwap = deltaCodeLengthDel(curNodeId, *mod_id, nm_links);
      
      if (deltaLAfterSwap < deltaLAfterSwapBest) {
	deltaLAfterSwapBest = deltaLAfterSwap;
	fromM = *mod_id;
      }
   }
   
   removeNodeFromModule(toM, curNode, nm_links);
   
   return deltaLAfterSwapBest + deltaLAfterAdd;
}


void FuzGreedy::level(bool sort) {
  
  gather_nonEmpty_modules(sort);
  
  Node** node_tmp = new Node*[Nmod];
  vector<int> ModId2Ind(Nnode);
  
  for (int i = 0; i < Nmod; i++) {
    node_tmp[i] = create_node_from_module(i);
    ModId2Ind[modWnode[i]] = i;
  }
  
  vector<map<int,double> > wModToMod(Nmod);

  for (int i = 0; i < Nnode; i++) {
    set<int>& parentModIds = node[i]->modIds;
    for (set<int>::iterator mod_id = parentModIds.begin(); mod_id != parentModIds.end(); mod_id++) {
      push_node_members_to_module(node[i], node_tmp[*mod_id]);
    }		
  }
  
  sumModToModWeights(ModId2Ind, wModToMod);

  for (int i = 0; i < Nmod; i++) {
    map<int,double>::iterator M_link;
    for(M_link = wModToMod[i].begin(); M_link != wModToMod[i].end(); M_link++) {
	node_tmp[i]->links.push_back(make_pair(M_link->first, M_link->second));
    } 
  }
  
  vector<int>().swap(mod_empty);
  Nempty = 0;
  
  delete_nodes();
  
  Nnode = Nmod;
  node = node_tmp;
  
  calibrate();
}