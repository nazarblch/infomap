#include "infomap.h"

using namespace std;
using std::cout;
using std::cin;
using std::endl;

unsigned stou(char *s){
  return strtoul(s,(char **)NULL,10);
}

std::vector<string> split(const string& inputString, const char seperator) {
    std::vector<string> string_parts;
    string::size_type substring_begin = 0, substring_end = 0;
    while ((substring_end = inputString.find(seperator, substring_end)) != string::npos) {
      string substring(inputString.substr(substring_begin, substring_end - substring_begin));
      string_parts.push_back(substring);
      substring_begin = ++substring_end;
    }
    string_parts.push_back(inputString.substr(substring_begin, substring_end - substring_begin));
    return string_parts;
}

void print_nmi(string argv_0, string networkName);
void partition(MTRand *R,Node ***node, GreedyBase *greedy, bool silent);
void repeated_partition(MTRand *R, Node ***node, GreedyBase *greedy, bool silent,int Ntrials);



// Call: trade <seed> <Ntries>
int main(int argc,char *argv[]){
  
  if( argc !=4 ){
    cout << "Call: ./infomap <seed> <network.net> <# attempts>" << endl;
    exit(-1);
  }
   
  int Ntrials = atoi(argv[3]);  // Set number of partition attempts
  string infile = string(argv[2]);
  string networkName(infile.begin(),infile.begin() + infile.find(".net"));
  
  MTRand *R = new MTRand(stou(argv[1]));
 
  Graph G;
  G.read_edges_net(argv[2]);
    
  G.init_nodes();
  G.delele_links();
  G.print_read_log();
   
  int Nnode = G.get_N();
  string *nodeNames = G.get_nodeNames();
  int Nlinks = G.get_M();
  int NdoubleLinks = G.get_NdoubleLinks();
  map<int,map<int,double> >& Links = G.get_links(); 
  double totalDegree = G.get_totalDegree();
  vector<double> degree = G.get_degree();
  Node ** & node = G.get_nodes();
  
  
  /////////// Partition network ////////////////////

  cout << "Now partition the network:" << endl;
  
  // Initiation
  GreedyBase* greedy;
  greedy = new Greedy(R, G.get_N(), G.get_totalDegree(), G.get_nodes());
  greedy->initiate();
  
  double uncompressedCodeLength = -greedy->nodeDegree_log_nodeDegree;

  repeated_partition(R, &node, greedy, false, Ntrials);
  int Nmod = greedy->Nnode;
  greedy->print_partition_log();
  
  // Order modules by size
  MapTree mapTree(greedy, G, networkName); 
  
  multimap<double,treeNode,greater<double> >& treeMap = mapTree.treeMap;
  multimap<double,pair<int,int>,greater<double> >& sortedLinks = mapTree.sortedLinks;
  
  cout << "done>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>" << endl;
  
  mapTree.print_partition_in_format_moduleRankSizeName();
  mapTree.print_partition_in_format_Pajek_clu();
  mapTree.print_map_in_Pajek_net_format();
  mapTree.print_size_of_modules_in_Pajek_vec_format();
  mapTree.print_map_in_map_format();
  mapTree.print_map_in_communityPerLine_format();
  
  delete [] G.get_nodeNames();
  for(int i=0;i<greedy->Nnode;i++){
    delete node[i];
  }
  delete [] node;
  delete greedy;
  delete R;
  
  print_nmi(string(argv[0]), networkName);
}

void print_nmi(string argv_0, string networkName) {
  string mutual_path = "";
  vector<string> mutual_path_parts = split(string(argv_0), '/');
  for(int i = 0; i < mutual_path_parts.size() - 3; i++) {
    mutual_path += mutual_path_parts[i] + '/';
  }
  mutual_path += "mutual3/mutual";
  
  string ground_coms(networkName.begin(), networkName.begin() + networkName.find_last_of('/'));
  ground_coms += "/c.dat";
  string res_coms = networkName + ".coms";
  
  execl(mutual_path.c_str(), mutual_path.c_str(), ground_coms.c_str(), res_coms.c_str(), (char *) 0);
}

bool is_Partition_the_partition_phase(int iteration) {
  return (iteration > 0) && (iteration % 2 == 0);
}

void tmp_func() {
}

void partition(MTRand *R, Node ***node, GreedyBase *greedy, bool silent){
  
  int Nnode = greedy->Nnode;
  Node **cpy_node = greedy->copy_nodes(node, Nnode);
  int iteration = 0;
  double outer_oldCodeLength;
  
  do{
    outer_oldCodeLength = greedy->codeLength;
    
    if(is_Partition_the_partition_phase(iteration) && (greedy->Nnode > 1)){  
        
      if(!silent)
        cout << "Iteration " << iteration+1 << ", moving " << flush;
      
      Node **rpt_node = greedy->copy_nodes(&cpy_node, Nnode);
      
      vector<int> subMoveTo(Nnode);
      vector<int> moveTo(Nnode);
      int subModIndex = 0;
      
      for(int i = 0; i < greedy->Nnode; i++){
        
        int sub_Nnode = (*node)[i]->members.size();
        
        if(sub_Nnode > 1) {
          
          Node **sub_node = new Node*[sub_Nnode]; 
	   
	  int *sub_rev_renumber = new int[sub_Nnode];
          double totalDegree = 0.0;
          
	  (*node)[i]->get_sub_nodes(Nnode,  cpy_node, totalDegree, sub_rev_renumber, sub_node );
	  Node **sub_node_cp = greedy->copy_nodes(&sub_node, sub_Nnode);
	  
          
          GreedyBase* sub_greedy;
          sub_greedy = new Greedy(R,sub_Nnode,totalDegree,sub_node);
          sub_greedy->initiate();
          partition(R,&sub_node,sub_greedy,true);
          
	  for(int j=0;j<sub_greedy->Nnode;j++){
            vector<int>& subCluster = sub_node[j]->members;
            for(vector<int>::iterator subCluster_mem_it = subCluster.begin(); subCluster_mem_it < subCluster.end(); subCluster_mem_it++){
	      cout << sub_node_cp[*subCluster_mem_it]->global_index << " ";
	      cout << sub_rev_renumber[*subCluster_mem_it] << endl;
              subMoveTo[sub_rev_renumber[*subCluster_mem_it]] = subModIndex;
            }
            moveTo[subModIndex] = i;
            subModIndex++;
            delete sub_node[j];
          }
          
          delete [] sub_node;
          delete sub_greedy;
          //delete [] sub_renumber;
          delete [] sub_rev_renumber;
          
        }
        else{
          
          subMoveTo[(*node)[i]->members[0]] = subModIndex;
          moveTo[subModIndex] = i;
          
          subModIndex++;
          
        }
      }
      
      for(int i=0;i<greedy->Nnode;i++)
        delete (*node)[i];
      delete [] (*node);
      
      greedy->initiate(rpt_node, Nnode);
      greedy->determMove(subMoveTo);
      greedy->level(node,false); 
      greedy->determMove(moveTo);
      (*node) = rpt_node;
      
      outer_oldCodeLength = greedy->codeLength;
      
      if(!silent)
        cout << greedy->Nnode << " modules, looping " << flush;
      
    }
    else if(iteration > 0){
      
      if(!silent)
        cout << "Iteration " << iteration+1 << ", moving " << Nnode << " nodes, looping " << flush;
      
      
      Node **rpt_node = new Node*[Nnode];
      for(int i=0;i<Nnode;i++){
        rpt_node[i] = new Node();
        cpyNode(rpt_node[i],cpy_node[i]);
      }
      
      vector<int> moveTo(Nnode);
      for(int i=0;i<greedy->Nnode;i++){
        int Nmembers = (*node)[i]->members.size();
        for(int j=0;j<Nmembers;j++){
          moveTo[(*node)[i]->members[j]] = i;
        }
      }
      
      for(int i=0;i<greedy->Nnode;i++)
        delete (*node)[i];
      delete [] (*node);
      
      greedy->initiate(rpt_node, Nnode);
      greedy->determMove(moveTo);
      
      (*node) = rpt_node;
    }
    else{
      
      if(!silent)
        cout << "Iteration " << iteration+1 << ", moving " << Nnode << " nodes, looping " << flush;
      
    }
    
    double oldCodeLength;
    do{
      oldCodeLength = greedy->codeLength;
      bool moved = true;
      int Nloops = 0;
      int count = 0;
      while(moved){
        moved = false;
        double inner_oldCodeLength = greedy->codeLength;
        greedy->move(moved);
        Nloops++;
        count++;
        if(fabs(inner_oldCodeLength-greedy->codeLength) < 1.0e-10)
          moved = false;
        
        if(count == 10){  
          greedy->tune();
          count = 0;
        }
      }
      
      greedy->level(node,true);
      
      if(!silent)
        cout << Nloops << " " << flush;
      
    } while(oldCodeLength - greedy->codeLength >  1.0e-10);
    
    iteration++;
    if(!silent)
      cout << "times between mergings to code length " <<  greedy->codeLength << " in " << greedy->Nmod << " modules." << endl;
    
  } while(outer_oldCodeLength - greedy->codeLength > 1.0e-10);
  
  for(int i=0;i<Nnode;i++)
    delete cpy_node[i];
  delete [] cpy_node;
  
}

void repeated_partition(MTRand *R, Node ***node, GreedyBase *greedy, bool silent, int Ntrials){
  
  int Nnode = greedy->Nnode;
  vector<int> cluster(Nnode);
  
  for(int trial = 0; trial < Ntrials; trial++){
    
    if(!silent)
      cout << "Attempt " << trial+1 << "/" << Ntrials << endl;
    
    Node **cpy_node = greedy->copy_nodes(node, Nnode);
    
    greedy->initiate(cpy_node, Nnode);
    
    partition(R, &cpy_node, greedy, silent);
    greedy->store_best_partition(cluster);
  }
  
  // Commit best partition
  greedy->initiate((*node), Nnode);
  greedy->determMove(cluster);
  greedy->level(node,true);
  
}




