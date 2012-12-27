#ifndef NODE_H
#define NODE_H

#include <cmath>
#include <iostream>
#include <vector>
#include <set>
#include <list>
#include <map>
#include <stack>
#include <algorithm>
#include <iomanip>
#include <fstream>
#include <sstream>
#include <cstring>

class Node;
using namespace std;

class Node{
 public:
  ~Node();
  Node();
  Node(int modulenr);
  Node(int modulenr, int global_modulenr);

  vector<int> members; // If module, lists member nodes in module
  vector<pair<int,double> > links; // List of identities and link weight of connected nodes/modules  
  set<int> modIds;
  
  double exit; // total weight of links to other nodes / modules
  double degree; // total degree of node / module
  int index; // the node / module identity
  int global_index;
  
  
  void refresh_degree() {
    double Mdeg = 0.0;
    for(vector<pair<int,double> >::iterator link = links.begin(); link != links.end(); link++) {
      Mdeg += (*link).second;
    }
    exit = Mdeg;
    degree = Mdeg; 
  }
  
  string str() {
    stringstream res;
    
    res << index << ": deg(" << degree << ") [";
    
    for (int i = 0; i < links.size(); i++) {
      res << "(" << links[i].first << ", " << links[i].second << "), ";
    }
    
    res << "]";
    
    return res.str();
  }
  
  Node* getCopy() {
  
    Node* newNode = new Node();
    
    newNode->index = index;
    newNode->global_index = global_index;
    newNode->exit = exit;
    newNode->degree = degree;

    int Nmembers = members.size();
    newNode->members = vector<int>(Nmembers);
    for(int i=0;i<Nmembers;i++)
      newNode->members[i] = members[i];
    
    int Nlinks = links.size();
    newNode->links = vector<pair<int,double> >(Nlinks);
    for(int i=0;i<Nlinks;i++){
      newNode->links[i].first = links[i].first;
      newNode->links[i].second = links[i].second;
    }
    
    return newNode;  
  }
  
  
  Node** get_sub_nodes(int Nnode, Node**& cpy_node) {
     
    set<int> sub_mem;
    int sub_Nnode = members.size();
    Node **sub_node = new Node*[sub_Nnode]; 

    for(int j = 0; j < sub_Nnode; j++) {
       sub_mem.insert(members[j]);
    }
    
    set<int>::iterator it_mem = sub_mem.begin();  
    int *sub_renumber = new int[Nnode];
                
    for(int j = 0; j < sub_Nnode; j++){
            
       int orig_nr = members[j];
       int orig_Nlinks = cpy_node[orig_nr]->links.size();
            
       sub_renumber[orig_nr] = j;
       sub_node[j] = new Node(j, orig_nr);
       
       for(int k = 0; k < orig_Nlinks; k++){
              int orig_link = cpy_node[orig_nr]->links[k].first;
              int orig_link_newnr = sub_renumber[orig_link];
              double orig_weight = cpy_node[orig_nr]->links[k].second;
              
            if(orig_link < orig_nr && sub_mem.find(orig_link) != sub_mem.end()) {
                  sub_node[j]->links.push_back(make_pair(orig_link_newnr,orig_weight));
                  sub_node[orig_link_newnr]->links.push_back(make_pair(j,orig_weight));
                  sub_node[j]->degree += orig_weight;
                  sub_node[orig_link_newnr]->degree += orig_weight;
            }
       }
    }
    
    delete [] sub_renumber;
    
    return sub_node; 
    
  }

 
 protected:
   
};



#endif
