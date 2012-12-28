#ifndef FUZGREEDY_H
#define FUZGREEDY_H

#include "Greedy.h"

template<class T>
bool contains(set<T>& arr, T value) {
  return (arr.find(value) != arr.end());
}

class FuzGreedy: public Greedy {

public:
    FuzGreedy(MTRand *RR, int nnode, double deg, Node **node);
    
    void refresh_splited_nodeDegree_log_nodeDegree () {
      nodeDegree_log_nodeDegree = 0.0;
      for(int i = 0; i < Nnode; i++){
	  for (map<int, double>::iterator id_pr = node[i]->modPr.begin(); id_pr != node[i]->modPr.end(); id_pr++) {
	    nodeDegree_log_nodeDegree += plogp(node[i]->degree * id_pr->second);
          }
      }
    }
  
    virtual void initFromFile(const char* input_coms_path, map<int, int>& id2ind);
    
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
    
    vector<int> set_intsecton(set<int>& first, set<int>& second){
       vector<int> v;                           
       set_intersection (first.begin(), first.end(), second.begin(), second.end(), back_inserter(v));
       return v;
    }
    
    virtual void tune(void) {
  
      set_mod_params_to_zero();
	    
      for (int i = 0; i < Nnode; i++) {
	set<int>& i_Mods = node[i]->modIds;
	int i_ModsCount = i_Mods.size();
	map<int, double> new_i_ModsPr;
	map<int, double> delta_mod_exit;
	
	for (link = node[i]->links.begin(); link < node[i]->links.end(); link++) {
	
	  int nb = link->first;
	  double nb_w = link->second;
	  set<int>& nb_Mods = node[nb]->modIds;
	  vector<int> common_Mods = set_intsecton(i_Mods, nb_Mods);
	  
	  for (set<int>::iterator mod_id = i_Mods.begin(); mod_id != i_Mods.end(); mod_id++) {
	  
	      if (common_Mods.size() == 0) {
		
		new_i_ModsPr[*mod_id] += nb_w / i_ModsCount;
		//mod_degree[*mod_id] += nb_w / i_ModsCount;
		
	      } else if ( contains(nb_Mods, *mod_id) ) {
		
		new_i_ModsPr[*mod_id] += nb_w * node[nb]->modPr[*mod_id];
		//mod_degree[*mod_id] += nb_w * node[nb]->modPr[*mod_id];
	      }
	      
	      if ( !contains(nb_Mods, *mod_id) ) {
		delta_mod_exit[*mod_id] += nb_w;
	      }
	  
	  }
	}
	
	node[i]->set_ModsPr(new_i_ModsPr);
	
	map<int, double>::iterator id_pr;
	for (id_pr = node[i]->modPr.begin(); id_pr != node[i]->modPr.end(); id_pr++) {
	  mod_exit[id_pr->first] += delta_mod_exit[id_pr->first] * id_pr->second;
	  mod_degree[id_pr->first] += node[i]->degree * id_pr->second; 
	}
	
      }
      
      refresh_code_params();
      
      cout << "code length in imported partition " << codeLength << " with mods count " << Nmod << endl;
    }
    
    ~FuzGreedy(){};
};

#endif // FUZGREEDY_H
