#include "Greedy.h"

Greedy::~Greedy(){
  vector<int>().swap(modWnode);
}

Greedy::Greedy(MTRand *RR, int nnode, double deg, Node **ah){
  R = RR;
  Nnode = nnode;  
  node = ah;
  degree = deg;
  invDegree = 1.0/degree;
  log2 = log(2.0);
  Nmod = Nnode;	
}

void Greedy::move(bool &moved){

  vector<int> randomOrder = randomPermutation(Nnode);
  
  for(int k = 0; k < Nnode; k++){
    
    int curNodeId = randomOrder[k]; 
    Node* curNode = node[curNodeId];
    
    map<int, double> wToCluster;

    vector< pair<int, double> >& curLinks = curNode->links;
    vector< pair<int, double> >::iterator ind_w;
         
    for(ind_w = curLinks.begin(); ind_w < curLinks.end(); ind_w++){
      int nb_M = node[ind_w->first]->index;
      double nb_w = ind_w->second;
      wToCluster[nb_M] += nb_w;
    }    
    
    // Calculate exit weight to own module
    int fromM = curNode->index; 
    double wfromM = 0.0;
    if(wToCluster.find(fromM) != wToCluster.end()) {
      wfromM = wToCluster[fromM];
    }
     	 
    vector<pair<int, double> > wToClusterVec(wToCluster.begin(), wToCluster.end());
    
    // Option to move to empty module (if node not already alone)
    if(mod_members[fromM] > node[curNodeId]->members.size() && Nempty > 0 && wToCluster.find(mod_empty[Nempty-1]) == wToCluster.end()) {
        wToClusterVec.push_back(make_pair(mod_empty[Nempty-1], 0.0));
    }
    
    wToClusterVec = randomPermutation(wToClusterVec);

    int bestM = fromM;
    double best_weight = 0.0;
    double best_delta = 0.0;
    
    // Find the move that minimizes the description length
    for (ind_w = wToClusterVec.begin(); ind_w < wToClusterVec.end(); ind_w++) {
      
      int toM = ind_w->first;
      double wtoM = ind_w->second;
      
      if(toM == fromM) continue;
				
      double deltaL = deltaCodeLength(curNodeId, toM, wtoM, fromM, wfromM);
				
      if(deltaL < best_delta){
          bestM = toM;
          best_weight = wtoM;
          best_delta = deltaL;  
      }			
      
    }
    
    if (bestM != fromM) {
      
      removeNodeFromModule(fromM, curNode);	
      addNodeToModule(bestM, curNode);
      	 
      moved = true;		
    }
		
  }	
}

void Greedy::initiate(void){
  
  for(int i = 0 ;i < Nnode; i++){
    node[i]->refresh_degree();
  }

  refresh_nodeDegree_log_nodeDegree();
  calibrate(); 
}

void Greedy::initiate(Node** cpy_node, int N) {
    Nnode = N;
    Nmod = N;
    node = cpy_node;
    initiate();
}

void Greedy::initFromFile(const char* input_coms_path, map<int, int>& id2ind) {
      
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
    
}

void Greedy::tune(void){
  
  set_mod_params_to_zero();
	
  for(int i=0;i<Nnode;i++){
    int i_M = node[i]->index;
    double i_d = node[i]->degree;
    int Nlinks = node[i]->links.size(); 
    mod_members[i_M]++;
    mod_degree[i_M] += i_d;
    for(int j=0;j<Nlinks;j++){
      int nb = node[i]->links[j].first;
      double nb_w = node[i]->links[j].second;
      int nb_M = node[nb]->index;
      if(i_M != nb_M)
	mod_exit[i_M] += nb_w;
    }
  }
  
  refresh_code_params();
}

void Greedy::calibrate(void){
  
  vector<int>(Nmod).swap(mod_empty);
  Nempty = 0;
  
  set_mod_params_to_zero();
  
  for (int i = 0; i < Nmod; i++) {
    mod_exit[i] = node[i]->exit;
    mod_degree[i] = node[i]->degree;
    mod_members[i] = node[i]->members.size();
    node[i]->index = i;
  }
  
  refresh_code_params();
}

void Greedy::gather_nonEmpty_modules(bool sort){

  Nmod = 0;
  vector<int>().swap(modWnode);
    
  for (int i = 0; i < Nnode; i++) {
      if(mod_members[i] > 0) {
          Nmod++;
	  modWnode.push_back(i);
      }
  }
  
  if(sort){
    Mod_cmp mod_cmp(mod_degree);
    std::sort(modWnode.begin(), modWnode.end(), mod_cmp);
  }	
}

void Greedy::level(bool sort){
  
  gather_nonEmpty_modules(sort);
  
  Node** node_tmp = new Node*[Nmod];
  vector<int> ModId2Ind(Nnode);
  
  for (int i = 0; i < Nmod; i++) {
    node_tmp[i] = create_node_from_module(i);
    ModId2Ind[modWnode[i]] = i;
  }
  
  vector<map<int,double> > wModToMod(Nmod);

  for (int i = 0; i < Nnode; i++) {
 
    int i_M = ModId2Ind[node[i]->index];
    
    push_node_members_to_module(node[i], node_tmp[i_M]);
		
    for (link = node[i]->links.begin(); link < node[i]->links.end(); link++) {
      int nb = link->first;
      int nb_M = ModId2Ind[node[nb]->index];
      if (nb != i && i_M != nb_M) {
	wModToMod[i_M][nb_M] += link->second; 
      }
    }
  }

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

void Greedy::determMove(vector<int> &moveTo){
	
  for (int i = 0; i < Nnode; i++) {
    if (i != moveTo[i]) {		
      removeNodeFromModule(i, node[i]);	
      addNodeToModule(moveTo[i], node[i]);
    }
  }
	
};


void Greedy::push_node_members_to_module(Node* oldNode, Node* module) {
    copy(oldNode->members.begin(), oldNode->members.end(), back_inserter(module->members));
}

double Greedy::plogp(double d){

  if(d < 1.0e-10) {
    return 0.0;
  } else {
    return invDegree*d*log(invDegree*d)/log2;
  }
}

double Greedy::delta_plogp(double q1, double q0) {
   return plogp(q1) - plogp(q0);
}

double Greedy::deltaCodeLength(int curNodeId, int toM, double wtoM, int fromM, double wfromM) {
   
   double node_exit = node[curNodeId]->exit;
   double node_deg = node[curNodeId]->degree; 
  
   double delta_exit = plogp(exitDegree - 2*wtoM + 2*wfromM) - exit;
	
   double new_exit_fromM = mod_exit[fromM] - node_exit + 2*wfromM;
   double new_exit_toM = mod_exit[toM] + node_exit - 2*wtoM;
   double new_deg_fromM = mod_degree[fromM] - node_deg;
   double new_deg_toM = mod_degree[toM] + node_deg;
				
   double delta_exit_log_exit = delta_plogp(new_exit_fromM, mod_exit[fromM]) + 
                                delta_plogp(new_exit_toM, mod_exit[toM]);
   double delta_degree_log_degree = delta_plogp(new_exit_fromM + new_deg_fromM, mod_exit[fromM] + mod_degree[fromM]) +
	                            delta_plogp(new_exit_toM + new_deg_toM, mod_exit[toM] + mod_degree[toM]);
				
   double deltaL = delta_exit - 2.0*delta_exit_log_exit + delta_degree_log_degree;
   
   return deltaL;
}