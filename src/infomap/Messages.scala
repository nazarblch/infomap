package infomap

import spark.bagel.Message


class ClMotion(val fromId: Int, val toId: Int, val dL: Double, val fromC: Cluster) extends Serializable{
  def Idsum = fromId + toId
  override def toString = "fromId=" + fromId + " toId=" + toId + " dL=" + dL
}


class PRMessage(val targetId: Int, val rank: Double) extends Message[Int] with Serializable

class ClClMessage(val targetId: Int, val c: Cluster) extends Message[Int] with Serializable

class NodeNodeMessage(val targetId: Int,
                      val node: Node,
                      val pWout: Double = 0.0,
                      val cluster: Cluster = null,
                      val fromId: Int = 0) extends Message[Int] with Serializable