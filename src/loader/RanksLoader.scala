package loader

import spark.SparkContext
import spark.SparkContext.rddToPairRDDFunctions
import spark.SparkContext.rddToOrderedRDDFunctions



import infomap.Node
import spark.rdd.ShuffledSortedRDD

object RanksLoader {
    def loadRanks(sc: SparkContext, path: String) = {

      val idToRank = sc.textFile(path).map(string => {
            val splited = string.split("[ \t\n\r\f]")
            (splited(0).toInt, splited(1).toDouble)
        })

      idToRank.sortByKey()
    }
}
