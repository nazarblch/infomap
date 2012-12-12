package infomap


import spark.bagel.Vertex
import math.log


class Cluster(val id: Int) extends Vertex with Serializable {
  var edges: Map[Int, Double] = _
  var n: Int = _
  var p: Double = _
  var q: Double = _
  var active: Boolean = _

  var maxdL: Double = 0
  var maxdLId: Int = -1
  var maxdLC: Cluster = _
  var deleted: Boolean = false
  var internalIds: Set[Int] = Set(id)

  def this(id: Int, edges: Map[Int, Double], n: Int, p: Double, q: Double, active: Boolean = true) {
    this(id)
    this.edges = edges
    this.n = n
    this.p = p
    this.q = q
    this.active = active
  }

  def this(node: Node) {
    this(node.cluster)
    this.edges = node.edges.map(e => (e._1, node.rank*e._2))
    this.n = 1
    this.p = node.rank
    this.q = PR.tau * this.p + (1 - PR.tau) * node.rank * node.edges.map(e => e._2).sum
    this.active = true
  }

  override def toString = id + " n=" + n + " p=" + p + " q=" + q + " " + edges.toString()

  def qLogq = q * log(q)
  def qpLogqp = (q + p) * log (q + p)

  def dqJoin(other: Cluster): Double = {
    val p_other_this = other.edges.getOrElse(this.id, 0.toDouble)
    val p_this_other = this.edges.getOrElse(other.id, 0.toDouble)
    val pu = (this.p + other.p)
    val jump_nodes_fraction = ((PR.n - this.n - other.n).toDouble / (PR.n - 1))

    PR.tau * jump_nodes_fraction * pu  + (1 - PR.tau) * (this.q + other.q - p_other_this - p_this_other)

  }

  def dLJoin(other: Cluster, qOut: Double): Double = {
    val qu = dqJoin(other)
    val pu = this.p + other.p
    val qOut1 = qOut - this.q - other.q + qu

    val info = new InfoMeasures

    info.dH(qOut1, qOut) - 2 * info.dH(qu, this.q, other.q) + info.dH(qu+pu, this.q+this.p, other.q+other.p)
  }

  def joinEdges(otherEdges: Map[Int, Double]): Map[Int, Double] = {
    edges ++ ( for ( (k,v) <- otherEdges) yield ( k -> ( v + edges.getOrElse(k, 0.toDouble) ) ) )
  }

  def mergeEdges(motion: ClMotion){
    val sum = edges.getOrElse(motion.fromId, 0.toDouble) + edges.getOrElse(motion.toId, 0.toDouble)
    if (sum > 0) this.edges = edges ++ Map( motion.toId -> sum )
    this.edges = edges.-(motion.fromId)
  }

  def join(other: Cluster): Double = {

      val qu = dqJoin(other)
      val dqOut = - this.q - other.q + qu

      this.q = qu
      this.edges = joinEdges(other.edges).filter(e => e._1 != other.id && e._1 != id)

      this.p += other.p
      this.n += other.n

      this.internalIds = this.internalIds ++ other.internalIds

      dqOut
  }
}



object CreateCluster {
  def main(args: Array[String]) {

    val n1 = {
      new Node(1, Map(2 -> 6, 3 -> 4, 6 -> 10), true, 2)
    }

    val n2 = {
      new Node(2, Map(4 -> 3, 3 -> 3, 6 -> 4), true, 4)
    }

    println(n1)
    println(n2)

    val c1 = new Cluster(n1)
    val c2 = new Cluster(n2)

    println(c1)
    println(c2)

    c1.join(c2)
    println(c1)
  }

}
