package infomap

import spark.bagel.Vertex


class Node(val id: Int) extends Vertex with Serializable {
  var edges: Map[Int, Double] = _
  var active: Boolean = _
  var cluster: Int = _
  var rank: Double = _
  var C: Cluster = _

  var Wc: Double = _
  var FromCMovePr: Double = _

  def this(id: Int, edges: Map[Int, Double], active: Boolean = true, rank: Double) {
    this(id)
    this.edges = edges
    this.active = active
    this.cluster = id
    this.rank = rank
    if (edges != null)
      normalize_edges()
  }

  def normalize_edges() {
    val Wdeg  = this.edges.map(_._2).reduce(_+_)
    this.edges = this.edges.map(e => (e._1, e._2 / Wdeg))
  }

  def createNodeWithC(): Node = {
    val cl = new Cluster(this)
    cl.internalIds = Set(this.id)
    val newNode = new Node(-this.id, null, true, this.rank)
    newNode.C = cl
    newNode.cluster = cl.id

    newNode
  }

  def dLFromMove(curC: Cluster, curClNodeMovePr: Double, WNodeC: Double, agd_Q: Double): Double = {
    val newCp = curC.p + rank
    val newCq = PR.tau * PR.outNodesFraction(curC.n + 1) * newCp +
                (1 - PR.tau) * (curC.q + rank * (1 - WNodeC) - curClNodeMovePr)

    val newCpParent = C.p - rank
    val newCqParent = PR.tau * PR.outNodesFraction(C.n - 1) * newCpParent +
    (1 - PR.tau) * (C.q - rank * (1 - Wc) + FromCMovePr)

    val newQ = agd_Q - curC.q - C.q + newCqParent + newCq

    val info = new InfoMeasures

    info.dH(newQ, agd_Q) - 2 * ( info.dH(newCq, curC.q) + info.dH(newCqParent, C.q) ) +
    info.dH(newCq + newCp, curC.q + curC.p) + info.dH(newCqParent + newCpParent, C.q + C.p)
  }

  override def toString = id + " cluster=" + cluster + " rank=" + rank + " edges=" + edges.toString()
}


object CreateNode {
  def main(args: Array[String]) {

    var n = new Node(1, Map(2->6, 3->4), true, 2.3)
    println(n.rank)
    println(n)

  }

}
