#include <iostream>
#include <sstream>
#include <string>
#include <fstream>
#include <map>
#include <cstdlib>
#include "Node.h" 

using namespace std;

template <class T>
inline std::string to_string (const T& t){
  std::stringstream ss;
  ss << t;
  return ss.str();
}


class treeNode{
 public:
  multimap<double,pair<int,string>,greater<double> > members;
  multimap<double,treeNode, greater<double> > nextLevel;
};

class Graph {
  
  Node **nodes;
  string* nodeNames;
  
  map<int,map<int,double> > Links;
  int Nnode;
  int Nlinks;
  int NdoubleLinks;
  int NselfLinks;
  
  double totalDegree;
  vector<double> degree;
  
  string net_path;

public:
  
  map<int, int> id2ind;
  
  Graph(): Nnode(0), Nlinks(0), NdoubleLinks(0), NselfLinks(0), totalDegree(0.0) {}
  
  void read_pajek_net(char* input_net_path);
  void read_edges_net(char* input_net_path);
  
  void init_nodes();
  
  void delele_links() {
     for(map<int,map<int,double> >::iterator it = Links.begin(); it != Links.end(); it++) {
       map<int,double>().swap(it->second);
     }
     map<int,map<int,double> >().swap(Links);
  }
  
  Node ** & get_nodes() {
    return nodes;
  }
  
  string* & get_nodeNames() {
    return nodeNames;
  }
  
  map<int,map<int,double> >& get_links() {
    return Links;
  }
  
  int get_N() {
    return Nnode;
  }
  
  int get_M() {
    return Nlinks;
  }
  
  int get_NdoubleLinks() {
    return NdoubleLinks;
  }
  
  int get_NselfLinks() {
    return NselfLinks;
  }
  
  double get_totalDegree() {
    return totalDegree;
  }
  
  vector<double>& get_degree() {
    return degree;
  }
  
  void print() {
    for (int i = 0; i < Nnode; i++) {
      cout << nodes[i]->str() << endl;
    }
  }
  
  void print_read_log() {
    
    cout << "Reading network " << net_path << "..." << flush;
    
    cout << "done! (found " << Nnode << " nodes and " << Nlinks << " links";
    
    if(NdoubleLinks > 0) {
      cout << ", aggregated " << NdoubleLinks << " link(s) defined more than once";
    }

    if(NselfLinks > 0) {
      cout << ", ignoring " <<  NselfLinks << " self link(s)." << endl;
    } else {
      cout << ")" << endl;
    }  
  }
  
  treeNode make_treeNode(Node* cluster) {
    
    treeNode tmp_tN;
     
    for(int j = 0; j < cluster->members.size(); j++) {
      int memberId = cluster->members[j];
      string memberName = nodeNames[memberId];
      double rank = degree[memberId]/totalDegree;
      
      tmp_tN.members.insert(make_pair(rank, make_pair(memberId, memberName)));
    }
    
    return tmp_tN;
  }
  
};