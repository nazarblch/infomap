package infomap



class PRutils(val numVerts: Long) extends Serializable{

  def compute(member: Node, incomeMessages: Option[Array[PRMessage]], superstep: Int) =   {

    val msgSum = incomeMessages.flatten.map(_.rank).sum
    val newRank =
      if (msgSum != 0)
        PR.tau / numVerts + (1 - PR.tau) * msgSum
      else
        member.rank

    val halt = superstep >= 30
    val msgsOut =
      if (!halt)
        member.edges.map(edge =>
          new PRMessage(edge._1, newRank / member.edges.size)).toArray
      else
        Array[PRMessage]()


    (new Node(member.id, member.edges, !halt, newRank), msgsOut)

  }
}