#ifndef FUZGREEDY_H
#define FUZGREEDY_H

#include "Greedy.h"

class FuzGreedy: public Greedy {

public:
    FuzGreedy(MTRand *RR, int nnode, double deg, Node **node);
  
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
    
    virtual tune(void){
  
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
    
    ~FuzGreedy(){};
};

#endif // FUZGREEDY_H
