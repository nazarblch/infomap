package infomap

import spark.RDD
import math.log

class InfoMeasures extends Serializable{

  def L(clusters: RDD[(Int, Cluster)]): Double = {
      val q = clusters.filter(_._2.active).map(_._2.q).reduce(_+_)
      val l0 = q * log(q)

      val l1 = -2 * clusters.filter(_._2.active).map(_._2.qLogq).reduce(_+_)

      val l2 = clusters.filter(_._2.active).map(_._2.qpLogqp).reduce(_+_)

      l0 + l1 + l2
  }

  def pLogp(q: Double): Double = {
      if (q < 0.0000001) {
        0.0
      } else {
        q * log(q) / log(2.0)
      }
  }

  def dH(q1: Double, q0: Double): Double = {
      pLogp(q1) - pLogp(q0)
  }

  def dH(qu: Double, q1: Double, q2: Double): Double = {
      pLogp(qu) - pLogp(q1) - pLogp(q2)
  }

}