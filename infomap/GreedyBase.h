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
  virtual void level(Node ***, bool sort){};
  virtual void move(bool &moved){};
  virtual void determMove(vector<int> &moveTo){};
  void print_partition_log();
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
  
 
 
 protected:

  MTRand *R;
 
};

#endif
