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
