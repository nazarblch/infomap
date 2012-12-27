#include "GraphLoader.h"

using namespace std;

void Graph::read_pajek_net(char* input_net_path) {
  
  ifstream net(input_net_path);
  istringstream ss;
  string line;
  string buf;
  
  net_path.assign(input_net_path);
    
  while(Nnode == 0){ 
    if(getline(net,line) == NULL){
      cout << "the network file is not in Pajek format...exiting" << endl;
      exit(-1);
    }
    else{
      ss.clear();
      ss.str(line);
      ss >> buf;
      if(buf == "*Vertices" || buf == "*vertices" || buf == "*VERTICES"){
        ss >> buf;
        Nnode = atoi(buf.c_str());
      }
      else{
        cout << "the network file is not in Pajek format...exiting" << endl;
        exit(-1);
      }
    }
  }
  
  nodeNames = new string[Nnode];
  
  // Read node names, assuming order 1, 2, 3, ...
  for(int i=0;i<Nnode;i++){
    getline(net,line);
    int nameStart = line.find_first_of("\"");
    int nameEnd = line.find_last_of("\"");
    if(nameStart < nameEnd){
      nodeNames[i] =  string(line.begin() + nameStart + 1,line.begin() + nameEnd);
    }
    else{
      ss.clear();
      ss.str(line);
      ss >> buf; 
      ss >> nodeNames[i];
    }
  }
  // Read the number of links in the network
  getline(net,line);
  ss.clear();
  ss.str(line);
  ss >> buf;
  if(buf != "*Edges" && buf != "*edges" && buf != "*Arcs" && buf != "*arcs"){
    cout << endl << "Number of nodes not matching, exiting" << endl;
    exit(-1);
  }
  
 
  // Read links in format "from to weight", for example "1 3 2" (all integers) and each undirected link only ones (weight is optional).
  while(getline(net,line) != NULL){
    ss.clear();
    ss.str(line);
    ss >> buf;
    int linkEnd1 = atoi(buf.c_str());
    ss >> buf;
    int linkEnd2 = atoi(buf.c_str());
    buf.clear();
    ss >> buf;
    double linkWeight;
    if(buf.empty()) // If no information 
      linkWeight = 1.0;
    else
      linkWeight = atof(buf.c_str());
    
    linkEnd1--; // Nodes start at 1, but C++ arrays at 0.
    linkEnd2--;
    
    if(linkEnd2 < linkEnd1){
      int tmp = linkEnd1;
      linkEnd1 = linkEnd2;
      linkEnd2 = tmp;
    }

    // Aggregate link weights if they are definied more than once
    map<int,map<int,double> >::iterator fromLink_it = Links.find(linkEnd1);
    if(fromLink_it == Links.end()){ // new link
      map<int,double> toLink;
      toLink.insert(make_pair(linkEnd2,linkWeight));
      Links.insert(make_pair(linkEnd1,toLink));
      Nlinks++;
    }
    else{
      map<int,double>::iterator toLink_it = fromLink_it->second.find(linkEnd2);
      if(toLink_it == fromLink_it->second.end()){ // new link
        fromLink_it->second.insert(make_pair(linkEnd2,linkWeight));
        Nlinks++;
      }
      else{
        toLink_it->second += linkWeight;
        NdoubleLinks++;
      }
    }
  }
  
  net.close();
}

struct Edge {
  int linkEnd1;
  int linkEnd2;
  double linkWeight;
  
  Edge(string id_id_w) {
    istringstream ss;
    string buf;
    
    ss.str(id_id_w);
    ss >> buf;
    linkEnd1 = atoi(buf.c_str());
    ss >> buf;
    linkEnd2 = atoi(buf.c_str());
    buf.clear();
    ss >> buf;
    if(buf.empty()) { 
      linkWeight = 1.0;
    } else {
      linkWeight = atof(buf.c_str());
    }
    
    if(linkEnd2 < linkEnd1){
      int tmp = linkEnd1;
      linkEnd1 = linkEnd2;
      linkEnd2 = tmp;
    }
  }
};

    
void Graph::read_edges_net(char* input_net_path) {
  
  ifstream net(input_net_path);
  string line;
  
  net_path.assign(input_net_path);
  
  map<int, int> id2ind;
  map<int, int>::iterator id2ind_it;
  
  // Read links in format "from to weight", for example "1 3 2" (all integers) and each undirected link only ones (weight is optional).
  while(getline(net,line) != NULL){
   
    Edge edge(line);   
    int linkEnd1;
    int linkEnd2;
    
    id2ind_it = id2ind.find(edge.linkEnd1);
    if (id2ind_it == id2ind.end()) {
      linkEnd1 = Nnode;
      id2ind.insert(make_pair(edge.linkEnd1, linkEnd1));
      Nnode++;
    } else {
      linkEnd1 = id2ind_it->second;
    }
    
    id2ind_it = id2ind.find(edge.linkEnd2);
    if (id2ind_it == id2ind.end()) {
      linkEnd2 = Nnode;
      id2ind.insert(make_pair(edge.linkEnd2, linkEnd2));
      Nnode++;
    } else {
      linkEnd2 = id2ind_it->second;
    }

    // Aggregate link weights if they are definied more than once
    map<int,map<int,double> >::iterator fromLink_it = Links.find(linkEnd1);
    if(fromLink_it == Links.end()){ // new link
      map<int,double> toLink;
      toLink.insert(make_pair(linkEnd2, edge.linkWeight));
      Links.insert(make_pair(linkEnd1,toLink));
      Nlinks++;
    } else {
      map<int,double>::iterator toLink_it = fromLink_it->second.find(linkEnd2);
      if(toLink_it == fromLink_it->second.end()){ // new link
        fromLink_it->second.insert(make_pair(linkEnd2, edge.linkWeight));
        Nlinks++;
      } else {
        toLink_it->second += edge.linkWeight;
        NdoubleLinks++;
      }
    }
  }
  
  nodeNames = new string[Nnode];
  
  for(id2ind_it = id2ind.begin(); id2ind_it != id2ind.end(); ++id2ind_it){
      nodeNames[id2ind_it->second] = to_string(id2ind_it->first);
  }
  
  net.close();
}


void Graph::init_nodes() {
  
  nodes = new Node*[Nnode];
  degree.resize(Nnode);
  totalDegree = 0.0;
  NselfLinks = 0;
  
  for(int i=0;i<Nnode;i++){
    nodes[i] = new Node(i);
    degree[i] = 0.0;
  }
  
  for(map<int,map<int,double> >::iterator fromLink_it = Links.begin(); fromLink_it != Links.end(); fromLink_it++){
    for(map<int,double>::iterator toLink_it = fromLink_it->second.begin(); toLink_it != fromLink_it->second.end(); toLink_it++){
      
      int from = fromLink_it->first;
      int to = toLink_it->first;
      double weight = toLink_it->second;
      if(weight > 0.0){
        if(from == to){
          NselfLinks++;
        }
        else{
          nodes[from]->links.push_back(make_pair(to,weight));
          nodes[to]->links.push_back(make_pair(from,weight));
          totalDegree += 2*weight;
          degree[from] += weight;
          degree[to] += weight;
        }
      }
    }
  }
}
