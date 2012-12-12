package infomap

import loader.GraphLoader
import loader.RanksLoader
import spark.{Partitioner, SparkContext}
import spark.bagel.{Combiner, Aggregator, Bagel}
import spark.SparkContext.rddToOrderedRDDFunctions
import math.{max, min}
import spark.RangePartitioner


object UniteClusters {

  def compute(C: Cluster, inMsg: Option[Array[ClClMessage]], agd_dL: Option[(Double, ClMotion)], superstep: Int) = {

    val behaviors = 3

    var msgsOut = Array[ClClMessage]()

    if (superstep % behaviors == 0 && !C.deleted){

      //println(C.id+ " active="+ C.active + " inmsg: " + inMsg.getOrElse(Array[ClClMessage]()).length +" step="+superstep)

      msgsOut = C.edges.map(e => new ClClMessage(e._1, C) ).toArray

    }else if(superstep % behaviors == 1 && !C.deleted){

      var dL:Double = 1

      C.maxdL = 0.0

      for(msg <- inMsg.flatten){
        dL = C.dLJoin(msg.c, agd_dL.get._1)
        if (dL < C.maxdL || (dL == C.maxdL && C.maxdLId > msg.c.id)){
          C.maxdL = dL
          C.maxdLId = msg.c.id
          C.maxdLC = msg.c
        }
      }

      C.active = (C.maxdL < 0)

    }else if(superstep % behaviors == 2 && !C.deleted){

      val motion = agd_dL.get._2

      if (agd_dL.size != 0 && C.id == motion.fromId){
        //println(motion)
        C.active = false
        C.deleted = true
        C.maxdL = 0.0

      }else if (agd_dL.size != 0 && C.id == motion.toId){

        C.join(motion.fromC)
        msgsOut = C.edges.map(e => new ClClMessage(e._1, C) ).toArray
        C.active = true
        C.maxdL = 0.0

      }else if (C.edges.contains(motion.fromId) || C.edges.contains(motion.toId)){

        C.mergeEdges(motion)
        msgsOut = Array[ClClMessage](new ClClMessage(motion.toId, C))
        C.active = true
      }else{
        //C.active = false
      }

    }

    (C, msgsOut)

  }


  def compute_fast(C: Cluster, inMsg: Option[Array[ClClMessage]], agd_dL: Option[(Double, ClMotion)], superstep: Int) = {

    val behaviors = 5

    var msgsOut = Array[ClClMessage]()

    if (superstep % behaviors == 0 && !C.deleted){

      msgsOut = C.edges.map(e => new ClClMessage(e._1, C) ).toArray

    }else if(superstep % behaviors == 1 && !C.deleted){

      var dL:Double = 1

      C.maxdL = 0.0
      C.maxdLId = -1

      for(msg <- inMsg.flatten){
        dL = C.dLJoin(msg.c, agd_dL.get._1)
        if (dL < C.maxdL || (dL == C.maxdL && C.maxdLId > msg.c.id)){
          C.maxdL = dL
          C.maxdLId = msg.c.id
          C.maxdLC = msg.c
        }
      }

      C.active = (C.maxdL < 0)

      if (C.active)
        msgsOut = C.edges.map(e => new ClClMessage(e._1, C) ).toArray

    }else if(superstep % behaviors == 2 && !C.deleted && C.active && inMsg.flatten.size > 0){

      val MaxMsgC = inMsg.flatten.map(_.c).reduceLeft( (c1, c2) => {
        if(c1.maxdL <  c2.maxdL || (c1.maxdL == c2.maxdL && c1.maxdLId == C.id))
          c1
        else
          c2
      })

      if (C.maxdLId == MaxMsgC.id && C.id == MaxMsgC.maxdLId && C.maxdL < 0){
        msgsOut = C.edges.map(e => new ClClMessage(e._1, C) ).toArray
      }else{
        C.maxdLId = -1
        C.maxdLC = null
      }

    }else if(superstep % behaviors == 3 && !C.deleted ){

      val msgs = inMsg.flatten

      if (msgs.size == 1 && msgs.last.c.id == C.maxdLId && msgs.last.c.maxdLId == C.id && C.id < C.maxdLId){
        C.join(C.maxdLC)
        msgsOut = C.edges.map(e => new ClClMessage(e._1, C) ).toArray
        C.active = true
      } else if (msgs.size == 1 && msgs.last.c.id == C.maxdLId && msgs.last.c.maxdLId == C.id && C.id > C.maxdLId){
        C.deleted = true
        msgsOut = C.edges.map(e => new ClClMessage(e._1, C) ).toArray
        C.active = false
      }

    } else if(superstep % behaviors == 4 && !C.deleted ){

        for(msg <- inMsg.flatten if msg.c.maxdLId != C.id  && msg.c.id != C.id){
          val toId = min(msg.c.id, msg.c.maxdLId)
          val fromId = max(msg.c.id, msg.c.maxdLId)
          val motion = new ClMotion(fromId, toId, msg.c.maxdL, msg.c)
          C.mergeEdges(motion)
        }
        C.active = true


    }

    (C, msgsOut)

  }


  class MaxLAggregator extends Aggregator[Cluster, Pair[Double, ClMotion]] with Serializable {

    def createAggregator(C: Cluster): Pair[Double, ClMotion] = {
      if (!C.deleted)
        (C.q, new ClMotion(C.id, C.maxdLId, C.maxdL, C))
      else
        (0.0, new ClMotion(-1, -1, 1.0, C))
    }

    def mergeAggregators(ag1: Pair[Double, ClMotion], ag2: Pair[Double, ClMotion]): Pair[Double, ClMotion] = {
      val motion1 = ag1._2
      val motion2 = ag2._2
      val q1 = ag1._1
      val q2 = ag2._1

      if (motion1.dL < motion2.dL || (motion1.dL == motion2.dL && motion1.Idsum < motion2.Idsum) )
        (q1+q2, motion1)
      else
        (q1+q2, motion2)
    }

  }



  class NoneCombiner extends Combiner[ClClMessage, Array[ClClMessage] ] with Serializable {
    def createCombiner(msg: ClClMessage): Array[ClClMessage] =
      Array(msg)
    def mergeMsg(combiner: Array[ClClMessage], msg: ClClMessage): Array[ClClMessage] =
      combiner :+ msg

    def mergeCombiners(a: Array[ClClMessage], b: Array[ClClMessage]): Array[ClClMessage] =
      a ++ b

  }

  def main(args: Array[String]) {

    val sc: SparkContext = new SparkContext(args(0), "test")

    val messages = sc.parallelize(Array[(Int, PRMessage)]())

    val graph = GraphLoader.loadGraph(sc, args(2)).sortByKey().cache()
    val numVerts = graph.count()
    PR.n = numVerts
    graph.foreach(id2node => id2node._2.rank /= numVerts)

    val utils = new PRutils(numVerts)
    val rankedG = Bagel.run(sc, graph, messages, 2){utils.compute}

    val clusters = rankedG.map(node => (node._1, new Cluster(node._2)))

    clusters.foreach(cl => println(cl))

    val infoMeasures = new InfoMeasures
    var L = infoMeasures.L(clusters)

    println(L)


    val messages1 = sc.parallelize(Array[(Int, ClClMessage)]())
    Bagel.run(
      sc,
      clusters,
      messages1,
      combiner = new NoneCombiner(),
      aggregator = Some(new MaxLAggregator()),
      partitioner = new RangePartitioner(args(1).toInt, clusters),
      numSplits = args(1).toInt){
        compute
    }.map(_._2).filter(_.deleted == false).map(c => c.internalIds.mkString(" ")).saveAsTextFile(args(3))



  }

}