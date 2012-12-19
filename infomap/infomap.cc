#include "infomap.h"

using namespace std;
using std::cout;
using std::cin;
using std::endl;

unsigned stou(char *s){
  return strtoul(s,(char **)NULL,10);
}

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
  G.read_pajek_net(argv[2]);
    
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
  
}

void partition(MTRand *R,Node ***node, GreedyBase *greedy, bool silent){
  
  int Nnode = greedy->Nnode;
  Node **cpy_node = new Node*[Nnode];
  for(int i=0;i<Nnode;i++){
    cpy_node[i] = new Node();
    cpyNode(cpy_node[i],(*node)[i]);
  }
  
  int iteration = 0;
  double outer_oldCodeLength;
  do{
    outer_oldCodeLength = greedy->codeLength;
    
    if((iteration > 0) && (iteration % 2 == 0) && (greedy->Nnode > 1)){  // Partition the partition
      
      
      if(!silent)
        cout << "Iteration " << iteration+1 << ", moving " << flush;
      
      Node **rpt_node = new Node*[Nnode];
      for(int i=0;i<Nnode;i++){
        rpt_node[i] = new Node();
        cpyNode(rpt_node[i],cpy_node[i]);
      }
      vector<int> subMoveTo(Nnode);
      vector<int> moveTo(Nnode);
      int subModIndex = 0;
      
      for(int i=0;i<greedy->Nnode;i++){
        
        int sub_Nnode = (*node)[i]->members.size();
        
        if(sub_Nnode > 1){
          
          Node **sub_node = new Node*[sub_Nnode]; 
          set<int> sub_mem;
          for(int j=0;j<sub_Nnode;j++)
            sub_mem.insert((*node)[i]->members[j]);
          set<int>::iterator it_mem = sub_mem.begin();
          int *sub_renumber = new int[Nnode];
          int *sub_rev_renumber = new int[sub_Nnode];
          double totalDegree = 0.0;
          for(int j=0;j<sub_Nnode;j++){
            
            //    fprintf(stderr,"%d %d\n",j,(*it_mem));
            int orig_nr = (*it_mem);
            int orig_Nlinks = cpy_node[orig_nr]->links.size(); // ERROR HERE
            sub_renumber[orig_nr] = j;
            sub_rev_renumber[j] = orig_nr;
            sub_node[j] = new Node(j);
            for(int k=0;k<orig_Nlinks;k++){
              int orig_link = cpy_node[orig_nr]->links[k].first;
              int orig_link_newnr = sub_renumber[orig_link];
              double orig_weight = cpy_node[orig_nr]->links[k].second;
              if(orig_link < orig_nr){
                if(sub_mem.find(orig_link) != sub_mem.end()){
                  sub_node[j]->links.push_back(make_pair(orig_link_newnr,orig_weight));
                  sub_node[orig_link_newnr]->links.push_back(make_pair(j,orig_weight));
                  totalDegree += 2.0*orig_weight;
                }
              }
            }
            it_mem++;
          }
          
          GreedyBase* sub_greedy;
          sub_greedy = new Greedy(R,sub_Nnode,totalDegree,sub_node);
          sub_greedy->initiate();
          partition(R,&sub_node,sub_greedy,true);
          for(int j=0;j<sub_greedy->Nnode;j++){
            int Nmembers = sub_node[j]->members.size();
            for(int k=0;k<Nmembers;k++){
              subMoveTo[sub_rev_renumber[sub_node[j]->members[k]]] = subModIndex;
            }
            moveTo[subModIndex] = i;
            subModIndex++;
            delete sub_node[j];
          }
          
          delete [] sub_node;
          delete sub_greedy;
          delete [] sub_renumber;
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
      
      greedy->Nnode = Nnode;
      greedy->Nmod = Nnode;
      greedy->node = rpt_node;
      greedy->initiate();
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
      
      greedy->Nnode = Nnode;
      greedy->Nmod = Nnode;
      greedy->node = rpt_node;
      greedy->initiate();
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
        // 	if(!silent){
        // 	  cerr << Nloops;
        // 	  int loopsize = to_string(Nloops).length();
        // 	  for(int i=0;i<loopsize;i++)
        // 	    cerr << "\b";
        // 	}
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

void repeated_partition(MTRand *R, Node ***node, GreedyBase *greedy, bool silent,int Ntrials){
  
  double shortestCodeLength = 1000.0;
  int Nnode = greedy->Nnode;
  vector<int> cluster(Nnode);
  
  for(int trial = 0; trial<Ntrials;trial++){
    
    if(!silent)
      cout << "Attempt " << trial+1 << "/" << Ntrials << endl;
    
    Node **cpy_node = new Node*[Nnode];
    for(int i=0;i<Nnode;i++){
      cpy_node[i] = new Node();
      cpyNode(cpy_node[i],(*node)[i]);
    }
    
    greedy->Nnode = Nnode;
    greedy->Nmod = Nnode;
    greedy->node = cpy_node;
    greedy->initiate();
    
    partition(R,&cpy_node,greedy,silent);
    
    if(greedy->codeLength < shortestCodeLength){
      
      shortestCodeLength = greedy->codeLength;
      
      // Store best partition
      for(int i=0;i<greedy->Nnode;i++){
        for(vector<int>::iterator mem = cpy_node[i]->members.begin(); mem != cpy_node[i]->members.end(); mem++){
          cluster[(*mem)] = i;
        }
      }
    }
    
    for(int i=0;i<greedy->Nnode;i++){
      delete cpy_node[i];
    }
    delete [] cpy_node;
    
  }
  
  // Commit best partition
  greedy->Nnode = Nnode;
  greedy->Nmod = Nnode;
  greedy->node = (*node);
  greedy->initiate();
  greedy->determMove(cluster);
  greedy->level(node,true);
  
}




