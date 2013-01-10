#ifndef GREEDYBASE_H
#define GREEDYBASE_H
#include "MersenneTwister.h"
#include <cstdio>
#include <vector>
#include "Node.h"

using namespace std;
// forward declaration
class Node;


class GreedyBase{
 public:
  GreedyBase() :shortestCodeLength(1000.0) {};
  virtual ~GreedyBase(){};
  virtual void initiate(void){};
  virtual void initiate(Node **cpy_node, int N){};
  virtual void tune(void){};
  virtual void calibrate(void){};
  virtual void prepare(bool sort){};
  virtual void level(bool sort){};
  virtual void move(bool &moved){};
  virtual void determMove(vector<int> &moveTo){};
  void print_partition_log();
  virtual void initFromFile(const char* input_coms_path,  map<int, int>& id2ind){};
  
  virtual void print_map_in_communityPerLine_format(string networkName,  string* & nodeNames){};
  
  int Nmod;
  int Nnode;
 
  double degree;
  double invDegree;
  double log2;
   
  double exit;
  double exitDegree;
  double exit_log_exit;
  double degree_log_degree;
  double nodeDegree_log_nodeDegree;
  
  double codeLength;
  double shortestCodeLength;
  
  Node **node;
  
  Node ** copy_nodes(Node ***node, int N) {
    
    Node **cpy_node = new Node*[N];
    
    for(int i=0; i < N; i++){
      cpy_node[i] = new Node();
      cpy_node[i] = (*node)[i]->getCopy();
    }
    
    return cpy_node;
  }
  
  void store_best_partition(vector<int>& cluster) {
    if(codeLength < shortestCodeLength){
      
      shortestCodeLength = codeLength;
      vector<int>::iterator mem_it; 
      
      for(int i=0;i<Nnode;i++){
        for(mem_it = node[i]->members.begin(); mem_it != node[i]->members.end(); mem_it++){
          cluster[(*mem_it)] = i;
        }
      }
      
    }
    
    for(int i=0; i< Nnode; i++){
      delete node[i];
    }
    delete [] node;
  }
  
  void update_moves(vector<int>& localToGlobal, vector<int>& subMoveTo, vector<int>& moveTo, int& subModIndex, int modIndex) {
    for(int j = 0; j < Nnode; j++) {
       
       vector<int>& subCluster = node[j]->members;
       vector<int>::iterator subCluster_mem_it;
            
       for(subCluster_mem_it = subCluster.begin(); subCluster_mem_it < subCluster.end(); subCluster_mem_it++){
          int subCluster_mem_global_ind = localToGlobal[*subCluster_mem_it];
          subMoveTo[subCluster_mem_global_ind] = subModIndex;
       }
            
       moveTo[subModIndex] = modIndex;
       subModIndex++;
    }
  }
  
  
  void delete_nodes() {
    for(int j = 0; j < Nnode; j++) {
        delete node[j];
    }
    delete [] node;
  }
  
  void set_first_level_in_modules(Node*** cpy_node, int N) {
      
      vector<int> moveTo(N);
      for(int modIndex = 0; modIndex < Nnode; modIndex++){
        vector<int>& modMembers = node[modIndex]->members;
        for(vector<int>::iterator mem = modMembers.begin(); mem < modMembers.end(); mem++){
          moveTo[*mem] = modIndex;
        }
      }
      
      delete_nodes();
      initiate(copy_nodes(cpy_node, N), N);
      determMove(moveTo);
  }
  
  void louvian(bool silent) {
      bool moved = true;
      int Nloops = 0;
      int count = 0;
      
      while(moved){
        moved = false;
        double inner_oldCodeLength = codeLength;
        move(moved);
        Nloops++;
        count++;
        if(fabs(inner_oldCodeLength - codeLength) < 1.0e-10) {
          moved = false;
        }
        
        if(count == 10){  
          tune();
          count = 0;
        }
      }
      
      level(true);
      
      if(!silent) {
        cout << Nloops << " " << flush;
      }
  }
 
 
 protected:

  MTRand *R;
 
};

#endif
