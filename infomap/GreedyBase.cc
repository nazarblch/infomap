#include "GreedyBase.h"


void GreedyBase::print_partition_log()
{
  cout << "Done! Code length " << codeLength << " in " << Nmod << " modules." << endl;
  cout << "Compressed by " << 100.0*(1.0 - codeLength/(-nodeDegree_log_nodeDegree)) << " percent." << endl;
}
