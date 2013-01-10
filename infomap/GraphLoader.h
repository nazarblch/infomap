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
  vector<map<int, int> > link2ind;
  vector<pair<int, int> > linkId2Pair;
  
  vector<map<int, int> > links_for_mod_sim;
  
  Graph(): Nnode(0), Nlinks(0), NdoubleLinks(0), NselfLinks(0), totalDegree(0.0) {}
  
  void read_pajek_net(char* input_net_path);
  void read_edges_net(char* input_net_path);
  
  Graph build_line_graph();
  
  void init_nodes();
  
  int insert_link_as_node(int nodeId, int nbId1) {
    if (nodeId < nbId1) {
      cout << Nnode << endl;
      link2ind[nodeId][nbId1] = Nnode;
      link2ind[nbId1][nodeId] = Nnode;
      linkId2Pair[Nnode] = make_pair(nodeId, nbId1);
      Nnode++;
    }
    
    return link2ind[nodeId][nbId1];
  }
  
  int united_links_count(int Id1, int Id2) {

    int res = 0;
    
    Node* node1 = nodes[Id1];
    Node* node2 = nodes[Id2];
    map<int, bool> node2LinkIds;
    
    for (int j = 0; j < node2->links.size(); j++) {
      node2LinkIds[node2->links[j].first] = true;
    }
    
    for (int j = 0; j < node1->links.size(); j++) {
      node2LinkIds[node1->links[j].first] = true;
    }
    
    return node2LinkIds.size();
    
  }
  
  double get_common_links_count(int Id1, int Id2) {
    return links_for_mod_sim[Id1][Id2];
  }
  
  double links_mod_sim(int nodeId, int nbId1, int nbId2) {
    double nb1nb2Intersect = get_common_links_count(nbId1, nbId2);
    double nb1nb2U = nodes[nbId1]->links.size() + nodes[nbId2]->links.size() - nb1nb2Intersect;
    
    double nodenb1Intersect = get_common_links_count(nodeId, nbId1);
    double nodenb1U = nodes[nodeId]->links.size() + nodes[nbId1]->links.size() - nodenb1Intersect;
    
    double nodenb2Intersect = get_common_links_count(nodeId, nbId2);
    double nodenb2U = nodes[nodeId]->links.size() + nodes[nbId2]->links.size() - nodenb2Intersect;
    
    return (nb1nb2Intersect + nodenb1Intersect + nodenb2Intersect) / (nb1nb2U + nodenb1U + nodenb2U);
  }
  
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