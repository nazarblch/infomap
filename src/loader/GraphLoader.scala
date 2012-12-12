package loader

import spark.SparkContext
import java.util.Random
import spark.SparkContext.rddToPairRDDFunctions
import infomap.Node

object GraphLoader {
    def loadGraph(sc: SparkContext, path: String) = {
        sc.textFile(path).map(string => {
            val splited = string.split("[ \t\n\r\f]")
            (splited(0), splited(1))
        }).map(strings => (strings._1.toInt, strings._2.toInt)).flatMap(pair => List(pair, (pair._2, pair._1)))
            .groupByKey().map(pair => {
                 val edges = Map(pair._2.map(id=>(id, 1.0)):_*)
                (pair._1, new Node(pair._1, edges, true, 1))
            })
    }
}
