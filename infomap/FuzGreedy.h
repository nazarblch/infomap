#ifndef FUZGREEDY_H
#define FUZGREEDY_H

#include "Greedy.h"

class FuzGreedy: public Greedy {

public:
    FuzGreedy(MTRand *RR, int nnode, double deg, Node **node);
    
    virtual void move(bool &moved);
    
    struct NodeModLinks {
      
       map<int, double> wToCluster;
       map<int, double> wToClusterWithPr;
       map<int, double> wToClusterDelta;
       map<int, double> wToClusterExternal;
       double deg_outside_mods;
	
    };
    
    double deltaCodeLengthAdd(int curNodeId, int toM, NodeModLinks& nm_links);
    double deltaCodeLengthDel(int curNodeId, int toM, NodeModLinks& nm_links);
    double deltaCodeLengthSwap(int curNodeId, int toM, NodeModLinks& nm_links, int& fromM);
    double multPlogP(double deg, int count);
    
    void check_invariants() {
      
      double lodL = codeLength;
      
      tune();
      
      if (fabs(lodL - codeLength) > 0.0001) {
	throw "check_invariants error";
      }
      
    }
    
    void refresh_splited_nodeDegree_log_nodeDegree () {
      nodeDegree_log_nodeDegree = 0.0;
      for(int i = 0; i < Nnode; i++){
	  for (map<int, double>::iterator id_pr = node[i]->modPr.begin(); id_pr != node[i]->modPr.end(); id_pr++) {
	    nodeDegree_log_nodeDegree += plogp(node[i]->degree * id_pr->second);
          }
      }
    }
    
    virtual void initiate(void){
  
      for(int i = 0 ;i < Nnode; i++){
	node[i]->refresh_degree();
      }

      refresh_nodeDegree_log_nodeDegree();
      calibrate(); 
    }
  
    virtual void initFromFile(const char* input_coms_path, map<int, int>& id2ind);
    
    void calcWtoNbMods(Node* curNode, NodeModLinks& nm_links) {
      vector< pair<int, double> >& curLinks = curNode->links;
      vector< pair<int, double> >::iterator ind_w;
      
      nm_links.deg_outside_mods = curNode->degree;
      
      for(ind_w = curLinks.begin(); ind_w < curLinks.end(); ind_w++){
	Node* nb_node = node[ind_w->first];
	set<int>& nb_Mods = nb_node->modIds;
	double nb_w = ind_w->second;
	int common_mods_count = set_intsecton(curNode->modIds, nb_Mods).size();
	
	for (set<int>::iterator nb_mod_id = nb_Mods.begin(); nb_mod_id != nb_Mods.end(); nb_mod_id++) {
	  nm_links.wToCluster[*nb_mod_id] += nb_w;
	  nm_links.wToClusterWithPr[*nb_mod_id] += nb_w * nb_node->modPr[*nb_mod_id];
	  
	  if ( common_mods_count == 0 ) {
	    nm_links.wToClusterDelta[*nb_mod_id] += nb_w;
	    nm_links.wToClusterExternal[*nb_mod_id] += nb_w / nb_node->modIds.size();
	  }
	  
	  if ( common_mods_count == 1  && curNode->modIds.find(*nb_mod_id) != curNode->modIds.end()) {
	    nm_links.wToClusterDelta[*nb_mod_id] += nb_w;
	  }
	}
	
	if (common_mods_count != 0) {
	  nm_links.deg_outside_mods -= nb_w;
	}
	
      }
      
    }


    
    virtual void sumModToModWeights(vector<int>& ModId2Ind, vector<map<int,double> >& wModToMod) {

      for (int i = 0; i < Nnode; i++) {
	  set<int>::iterator mod_id;
	  set<int>::iterator nb_mod_id;
	      
	  for (link = node[i]->links.begin(); link < node[i]->links.end(); link++) {
	    int nb = link->first;
	    for (nb_mod_id = node[nb]->modIds.begin(); nb_mod_id != node[nb]->modIds.end(); nb_mod_id++) {
	      for (mod_id = node[i]->modIds.begin(); mod_id != node[i]->modIds.end(); mod_id++) {
		int nb_M = ModId2Ind[*nb_mod_id];
		int i_M = ModId2Ind[*mod_id];
		int i_M_pr = node[i]->modPr[*mod_id];
		if (nb != i && i_M != nb_M) {
		  wModToMod[i_M][nb_M] += link->second * i_M_pr / node[nb]->modIds.size(); 
		}
	      }
	    }
	  }
      }
    
    }
    
    virtual void addNodeToModule(int toM, Node* newNode, NodeModLinks& nm_links) {
    
      if ( newNode->containsMod(toM) ) {
	cout << "Warning: pushing node to module that already contains it" << endl;
	return;
      }
      
      if(mod_members[toM] == 0) {
	  Nempty--;
      }
      
      double old_deg_outside_mods = nm_links.deg_outside_mods;
      double new_deg_outside_mods = old_deg_outside_mods - nm_links.wToClusterDelta[toM];
      nm_links.deg_outside_mods = new_deg_outside_mods; 
    
      set<int>& parentModIds = newNode->modIds;
      double node_exit = newNode->exit;
      double node_deg = newNode->degree;
      
      double oldPr = 1.0 / parentModIds.size();
      double newPr = 1.0 / (parentModIds.size() + 1);
      
      for (set<int>::iterator mod_id = parentModIds.begin(); mod_id != parentModIds.end(); mod_id++) {
	eraseModuleCode(*mod_id);
	
	double wFromMod = node_exit - nm_links.wToCluster[*mod_id];
	mod_exit[*mod_id] = mod_exit[*mod_id] + wFromMod * (newPr - oldPr);
	mod_degree[*mod_id] += new_deg_outside_mods * newPr - old_deg_outside_mods * oldPr + nm_links.wToCluster[*mod_id] * (newPr - oldPr);
	nodeDegree_log_nodeDegree += delta_plogp(new_deg_outside_mods * newPr + nm_links.wToClusterWithPr[toM], 
						 old_deg_outside_mods * oldPr + nm_links.wToClusterWithPr[toM]);
	
	pasteModuleCode(*mod_id);
      }
      
      eraseModuleCode(toM);
      
      mod_exit[toM] = mod_exit[toM] + (node_exit - nm_links.wToCluster[toM]) * newPr - nm_links.wToClusterWithPr[toM];
      mod_degree[toM] += new_deg_outside_mods * newPr + nm_links.wToClusterWithPr[toM] + newPr * nm_links.wToCluster[toM];
      mod_degree[toM] -= nm_links.wToClusterExternal[toM];
      nodeDegree_log_nodeDegree += delta_plogp(new_deg_outside_mods * newPr + nm_links.wToClusterWithPr[toM], 0.0);
       
      pasteModuleCode(toM);
      
      newNode->add_parent_module(toM);
      //mod_members[toM] += newNode->members.size();
      
    }
  
    virtual void removeNodeFromModule(int toM, Node* newNode, NodeModLinks& nm_links) {
    
      if ( !newNode->containsMod(toM) ) {
	cout << "Warning: pop node from module which it doesn't belong to" << endl;
	return;
      }
      
//       if(mod_members[toM] == newNode->members.size()) {
// 	  mod_empty[Nempty] = toM;
// 	  Nempty++;
//       }
    
      double old_deg_outside_mods = nm_links.deg_outside_mods;
      double new_deg_outside_mods = old_deg_outside_mods + nm_links.wToClusterDelta[toM];
      nm_links.deg_outside_mods = new_deg_outside_mods;
      
      set<int>& parentModIds = newNode->modIds;
      double node_exit = newNode->exit;
      double node_deg = newNode->degree;
      
      double oldPr = 1.0 / parentModIds.size();
      double newPr = 1.0 / (parentModIds.size() - 1);
     
      for (set<int>::iterator mod_id = parentModIds.begin(); mod_id != parentModIds.end(); mod_id++) {
	
	if (*mod_id == toM) continue;
	
	eraseModuleCode(*mod_id);
	
	double wFromMod = node_exit - nm_links.wToCluster[*mod_id];
	mod_exit[*mod_id] = mod_exit[*mod_id] + wFromMod * (newPr - oldPr);
	mod_degree[*mod_id] += new_deg_outside_mods * newPr - old_deg_outside_mods * oldPr + nm_links.wToCluster[*mod_id] * (newPr - oldPr);
	nodeDegree_log_nodeDegree += delta_plogp(new_deg_outside_mods * newPr +  nm_links.wToClusterWithPr[toM], 
						 old_deg_outside_mods * oldPr + nm_links.wToClusterWithPr[toM]);
	
	pasteModuleCode(*mod_id);
      }
      
      eraseModuleCode(toM);
      
      mod_exit[toM] = mod_exit[toM] - (node_exit - nm_links.wToCluster[toM]) * oldPr + nm_links.wToClusterWithPr[toM];
      mod_degree[toM] = mod_degree[toM] - old_deg_outside_mods * oldPr - nm_links.wToClusterWithPr[toM] - oldPr * nm_links.wToCluster[toM];
      mod_degree[toM] += nm_links.wToClusterExternal[toM];
      nodeDegree_log_nodeDegree += delta_plogp(0.0, old_deg_outside_mods * oldPr + nm_links.wToClusterWithPr[toM]);
       
      pasteModuleCode(toM);
      
      newNode->del_parent_module(toM);
      //mod_members[toM] -= newNode->members.size();
      

    }
    
    vector<int> set_intsecton(set<int>& first, set<int>& second){
       vector<int> v;                           
       set_intersection (first.begin(), first.end(), second.begin(), second.end(), back_inserter(v));
       return v;
    }
    
    virtual void tune(void) {
  
      set_mod_params_to_zero();
      
      nodeDegree_log_nodeDegree = 0.0;
	    
      for (int i = 0; i < Nnode; i++) {
	set<int>& i_Mods = node[i]->modIds;
	int i_ModsCount = i_Mods.size();
	map<int, double> new_i_ModsPr;
	map<int, double> delta_mod_exit;
	map<int, double> delta_mod_deg;
	
	for (link = node[i]->links.begin(); link < node[i]->links.end(); link++) {
	
	  int nb = link->first;
	  double nb_w = link->second;
	  set<int>& nb_Mods = node[nb]->modIds;
	  vector<int> common_Mods = set_intsecton(i_Mods, nb_Mods);
	  
	  for (set<int>::iterator mod_id = i_Mods.begin(); mod_id != i_Mods.end(); mod_id++) {
	  
	      if (common_Mods.size() == 0) {
		mod_degree[*mod_id] += nb_w / i_ModsCount;
		delta_mod_deg[*mod_id] += nb_w / i_ModsCount;
		
	      } else if ( node[nb]->containsMod(*mod_id) ) {
		mod_degree[*mod_id] += nb_w * node[nb]->modPr[*mod_id];
		delta_mod_deg[*mod_id] += nb_w * node[nb]->modPr[*mod_id];
	      }
	      
	      if ( !node[nb]->containsMod(*mod_id) ) {
		delta_mod_exit[*mod_id] += nb_w;
	      }
	  
	  }
	}
	
	map<int, double>::iterator id_pr;
	for (id_pr = node[i]->modPr.begin(); id_pr != node[i]->modPr.end(); id_pr++) {
	  mod_exit[id_pr->first] += delta_mod_exit[id_pr->first] * id_pr->second;
	  nodeDegree_log_nodeDegree += plogp(delta_mod_deg[id_pr->first]);
	}
	
      }
      
      refresh_code_params();
      
      cout << "code length in imported partition " << codeLength << " with mods count " << Nmod << endl;
    }
    
    ~FuzGreedy(){};
};

#endif // FUZGREEDY_H
