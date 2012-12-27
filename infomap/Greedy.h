#ifndef GREEDY_H
#define GREEDY_H

#include "MersenneTwister.h"
#include "GreedyBase.h"
#include <cmath>
#include <iostream>
#include <vector>
#include <queue>
#include <deque>
#include <set>
#include <stack>
#include <map>
#include <algorithm>
using namespace std;


class Greedy : public GreedyBase{
 public:
  Greedy(MTRand *RR, int nnode, double deg, Node **node);
  virtual ~Greedy();
  virtual void initiate(void);
  virtual void initiate(Node **cpy_node, int N);
  virtual void calibrate(void);
  virtual void tune(void);
  virtual void prepare(bool sort);
  virtual void level(bool sort);
  virtual void move(bool &moved);
  virtual void determMove(vector<int> &moveTo);
  
  int Nempty;
  vector<int> mod_empty;

  vector<double> mod_exit;
  vector<double> mod_degree;
  vector<int> mod_members;
  
  
 protected:
  double plogp(double d);
  double delta_plogp(double q1, double q0);
  double deltaCodeLength(int curNodeId, int toM, double wtoM, int fromM, double wfromM);
  
  void refresh_nodeDegree_log_nodeDegree () {
      nodeDegree_log_nodeDegree = 0.0;
      for(int i=0;i<Nmod;i++){
          nodeDegree_log_nodeDegree += plogp(node[i]->degree);
      }
  }
   
  void set_mod_params_to_zero() {
      exit_log_exit = 0.0;
      degree_log_degree = 0.0;
      exitDegree = 0.0;
  
      vector<double>(Nmod, 0.0).swap(mod_exit);
      vector<double>(Nmod, 0.0).swap(mod_degree);
      vector<int>(Nmod, 0).swap(mod_members);
  }
  
  void refresh_code_params() {
    
    for (int i = 0; i < Nmod; i++) {
      exit_log_exit += plogp(mod_exit[i]);
      degree_log_degree += plogp(mod_exit[i] + mod_degree[i]);
      exitDegree += mod_exit[i]; 
    }
	
    exit = plogp(exitDegree);
    codeLength = exit - 2.0*exit_log_exit + degree_log_degree - nodeDegree_log_nodeDegree; 
  }
  
  double sumModuleNodeWeight(int modId, const Node* newNode) {
    
    vector< pair<int, double> >::const_iterator ind_w;
    double node_mod_link_w = 0.0;
    
    for(ind_w = newNode->links.begin(); ind_w < newNode->links.end(); ind_w++){
      int nb_M = node[ind_w->first]->index;
      if (nb_M == modId) {
	node_mod_link_w += ind_w->second;
      }
    }
    
    return node_mod_link_w;
    
  }
  
  void eraseModuleCode(int modId) {
    exitDegree -= mod_exit[modId];
    exit_log_exit -= plogp(mod_exit[modId]);
    degree_log_degree -= plogp(mod_exit[modId] + mod_degree[modId]); 
    
    exit = plogp(exitDegree); 
    codeLength = exit - 2.0*exit_log_exit + degree_log_degree - nodeDegree_log_nodeDegree; 
  }
  
  void pasteModuleCode(int modId) {
    exitDegree += mod_exit[modId];
    exit_log_exit += plogp(mod_exit[modId]);
    degree_log_degree += plogp(mod_exit[modId] + mod_degree[modId]); 
    
    exit = plogp(exitDegree);
    codeLength = exit - 2.0*exit_log_exit + degree_log_degree - nodeDegree_log_nodeDegree; 
  }
  
  void addNodeToModule(int modId, Node* newNode) {
    
    if (newNode->index == modId) {
      cout << "Warning: pushing node to module that already contains it" << endl;
      return;
    }
    
    double node_mod_link_w = sumModuleNodeWeight(modId, newNode);
    
    eraseModuleCode(modId);
    
    mod_exit[modId] += newNode->exit - 2*node_mod_link_w;
    mod_degree[modId] += newNode->degree;
    mod_members[modId] += newNode->members.size();
    newNode->index = modId;
    
    pasteModuleCode(modId);
  }
  
  void removeNodeFromModule(int modId, const Node* newNode) {
    
    if (newNode->index != modId) {
      cout << "Warning: pop node from module which it doesn't belong to" << endl;
      return;
    }
   
    double node_mod_link_w = sumModuleNodeWeight(modId, newNode);;
    
    eraseModuleCode(modId);
    
    mod_exit[modId] -= newNode->exit - 2*node_mod_link_w;
    mod_degree[modId] -= newNode->degree;
    mod_members[modId] -= newNode->members.size();
    
    pasteModuleCode(modId);
  }
  
  vector<pair<int,double> >::iterator link;
  vector<int> modWnode;
  
  vector<int> randomPermutation(int n) {
   
    vector<int> randomOrder(n);
    
    for(int i = 0; i < n; i++) {
      randomOrder[i] = i;
    }
    
    for(int i = 0; i < n - 1; i++){
      int randPos = i + R->randInt(n-i-1);
      swap(randomOrder[i], randomOrder[randPos]);
    }
    
    return randomOrder;
  }
  
  template <class T>
  vector<T>& randomPermutation(vector<T>& array) {
    
    int n = array.size();
    
    for(int i = 0; i < n - 1; i++){
      int randPos = i + R->randInt(n-i-1);
      swap(array[i], array[randPos]);
    }
    
    return array;
  }
  
};

#endif
