#include "Node.h"

Node::~Node(){

  members.clear();
  links.clear();
  modIds.clear();
  modPr.clear();

}

Node::Node(){
}


Node::Node(int nodenr){
  
  index = nodenr;
  exit = 0.0;
  degree = 0.0;
  members.push_back(nodenr);
  modIds.insert(index);
  modPr[index] = 1;
}

Node::Node(int modulenr, int global_modulenr) {
   index = modulenr;
   exit = 0.0;
   degree = 0.0;
   members.push_back(modulenr);
   global_index = global_modulenr;
   modIds.insert(index);
   modPr[index] = 1;
}
