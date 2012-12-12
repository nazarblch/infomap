package infomap


import loader.GraphLoader
import spark.SparkContext
import spark.bagel.{Message, Bagel}





object PageRank {
  def main(args: Array[String]) {
    val sc: SparkContext = new SparkContext(args(0), "test")
    val messages = sc.parallelize(Array[(Int, PRMessage)]())
    val graph = GraphLoader.loadGraph(sc, args(1)).cache()
    val numVerts = graph.count()

    graph.foreach(id2node => id2node._2.rank /= numVerts)

    val utils = new PRutils(numVerts)


    Bagel.run(sc, graph, messages, 2)
    {
      utils.compute

    }.map(idToNode => (idToNode._2.id + "\t" + idToNode._2.rank)).saveAsTextFile(args(2))
  }

}