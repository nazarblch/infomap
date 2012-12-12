package infomap


import loader.GraphLoader
import loader.RanksLoader
import spark.{Partitioner, SparkContext}
import spark.bagel.{Combiner, Aggregator, Bagel}
import spark.SparkContext.rddToOrderedRDDFunctions
import math.{max, min}
import spark.RangePartitioner
import collection.mutable.ArrayBuffer
import util.Random


object GreedyOpt {

  def reduce_spread_cluster_info(node: Node, msgsIn: Array[NodeNodeMessage], superstep: Int) = {

    val C = node.C

    for(id <- msgsIn.map(_.node.C.id)){
      if(id != C.id)
        throw new Exception("cluster isn't a parent")
    }

    if (superstep > 0 ){

      C.n = msgsIn.size
      C.p = msgsIn.map(_.node.rank).sum
      C.q = PR.tau * PR.outNodesFraction(C.n) * C.p + (1-PR.tau) * msgsIn.map(_.pWout).sum
      C.internalIds = msgsIn.map(_.node.id).toSet
    }

    if (C.n == 0) {
      C.deleted = true
      node.active = false
    }

    // send info about cluster to internal nodes
    C.internalIds.map(id => new NodeNodeMessage(id, node) ).toArray
  }

  def compute(node: Node, inMsg: Option[Array[NodeNodeMessage]], agd_Q: Option[Double], superstep: Int) = {

    val behaviors = 4

    var msgsOut = Array[NodeNodeMessage]()
    val msgsIn = inMsg.flatten.toArray

    if (superstep % behaviors == 0 && node.id < 0 && !node.C.deleted){

      // send info about cluster to internal nodes
      msgsOut = reduce_spread_cluster_info(node, msgsIn, superstep)

      if (superstep > 100) {
        node.active = false
        msgsOut = Array[NodeNodeMessage]()
      }

    }else if(superstep % behaviors == 1 && node.id > 0){

      val msg = msgsIn.last

      if (msgsIn.size > 1) throw new Exception("more then one parent cluster")
      if (msgsIn.size == 0) throw new Exception("parent cluster lost")
      if (node.C.id != msg.node.C.id) throw new Exception("message from non-parent cluster")

      node.C = msg.node.C

      // send invitation to neighbor nodes
      msgsOut = node.edges.map(e => new NodeNodeMessage(e._1, null, node.rank * e._2, node.C, node.id) ).toArray

    }else if(superstep % behaviors == 2 && node.id > 0){

      val msgsPerC = msgsIn.groupBy(_.cluster.id)
      //val msgsFromParentC = msgsIn.filter(_.cluster.id == node.C.id)
      val CoId = node.C.id
      val ClNodeMovePr: Map[Int, Double] = msgsPerC.map(cm => {( cm._1, cm._2.map(_.pWout).sum )} )
      val NodeClW: Map[Int, Double] = msgsPerC.map(cm => {( cm._1, cm._2.map(m => node.edges.get(m.fromId).get).sum )} )

      node.Wc = NodeClW.getOrElse(CoId, 0)
      node.FromCMovePr = ClNodeMovePr.getOrElse(CoId, 0)

      var maxdL = 0.0
      var maxdLC = node.C
      var sumdL = 0.0
      val toM = ArrayBuffer[(Cluster, Double)]()

      for (cm <- msgsPerC if cm._1 != node.C.id) {
           val curC = cm._2.last.cluster
           val curClNodeMovePr = ClNodeMovePr.get(curC.id).get
           val WNodeC = NodeClW.get(curC.id).get
           val dL = node.dLFromMove(curC, curClNodeMovePr, WNodeC, agd_Q.get)

           if (dL < maxdL) {
             maxdL = dL
             maxdLC = curC
           }

           if (dL < 0) {
             sumdL += -dL
             toM += ((curC, -dL))
           }
      }

      val r = Random
      sumdL = r.nextDouble() * sumdL

      if ( maxdL < 0 && r.nextFloat() > 0.1) {
        //node.C = maxdLC
        for (C2dL  <- toM) {
          sumdL -= C2dL._2
          if (sumdL <= 0) {
            node.C = C2dL._1
          }
        }
      }

      // send information about replacement to neighbors
      msgsOut = node.edges.map(e => new NodeNodeMessage(e._1, null, node.rank * e._2, node.C, node.id) ).toArray

    } else if(superstep % behaviors == 3 && node.id > 0) {

      val msgsFromParentC = msgsIn.filter(_.cluster.id == node.C.id)
      val CoId = node.C.id

      node.Wc = 0.0
      node.Wc = msgsFromParentC.map(m => node.edges.get(m.fromId).get).sum

      // send info to parent cluster
      msgsOut = Array[NodeNodeMessage](new NodeNodeMessage(-node.C.id, node, node.rank * (1-node.Wc), null, node.id) )

    }

    (node, msgsOut)

  }

  class QAggregator extends Aggregator[Node, Double] with Serializable {

    def createAggregator(node: Node): Double = {
      if (node.id < 0 && !node.C.deleted)
        node.C.q
      else
        0.0
    }

    def mergeAggregators(ag1: Double, ag2: Double): Double = {
      ag1 + ag2
    }
  }

  class NoneCombiner extends Combiner[NodeNodeMessage, Array[NodeNodeMessage] ] with Serializable {
    def createCombiner(msg: NodeNodeMessage): Array[NodeNodeMessage] =
      Array(msg)
    def mergeMsg(combiner: Array[NodeNodeMessage], msg: NodeNodeMessage): Array[NodeNodeMessage] =
      combiner :+ msg

    def mergeCombiners(a: Array[NodeNodeMessage], b: Array[NodeNodeMessage]): Array[NodeNodeMessage] =
      a ++ b

  }

  def main(args: Array[String]) {

    val sc: SparkContext = new SparkContext(args(0), "test")

    var messages = sc.parallelize(Array[(Int, PRMessage)]())

    val graph = GraphLoader.loadGraph(sc, args(2)).sortByKey().cache()
    val numVerts = graph.count()
    PR.n = numVerts
    graph.foreach(id2node => id2node._2.rank /= numVerts)

    val utils = new PRutils(numVerts)
    val rankedG = Bagel.run(sc, graph, messages, 2){utils.compute}

    rankedG.foreach(id2node => {id2node._2.C = new Cluster(id2node._2)})

    val nodesWithC = rankedG.map(id2node => (-id2node._1, id2node._2.createNodeWithC()))

    val tmp  = rankedG.collect()

    val bi_graph = rankedG ++ nodesWithC

    println("n="+PR.n)

    val messages1 = sc.parallelize(Array[(Int, NodeNodeMessage)]())
    Bagel.run(
      sc,
      bi_graph,
      messages = messages1,
      combiner = new NoneCombiner(),
      aggregator = Some(new QAggregator()),
      partitioner = new RangePartitioner(args(1).toInt, bi_graph),
      numSplits = args(1).toInt){
      compute
    }.filter(_._2.id < 0).map(_._2.C).filter(_.deleted == false).map(c => c.internalIds.mkString(" ")).saveAsTextFile(args(3))

  }

}








