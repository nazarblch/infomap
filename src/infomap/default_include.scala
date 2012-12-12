package infomap

object PR{
   val tau: Double = 0.15
   var n: Long = 300
   def outNodesFraction (nc: Int): Double = {
     (n - nc).toDouble / (n - 1).toDouble
   }
}
