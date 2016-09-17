import scala.util.Random

package maze {

abstract class Maze {
    val width: Int
    val height: Int

    def generate: Unit

    def isWall(x: Int, y: Int): Boolean
}

class MazeDFS(maxWidth: Int, maxHeight: Int) extends Maze {
    private val graphWidth = (maxWidth + 1) / 2
    private val graphHeight = (maxHeight + 1) / 2

    val width = 2 * graphWidth - 1
    val height = 2 * graphHeight - 1

    def generate: Unit = {
        var visited = new Array[Boolean](graphSize)

        graphLinks = new Array[List[Int]](graphSize)

        def visitNode(nodes: List[(Int, Int)]): Unit = nodes match {
            case Nil => ()
            case (prevNode, node) :: restNodes =>
                if (!visited(node)) {
                    visited(node) = true
                    addGraphLink(prevNode, node)
                    val nextNodes = Random.shuffle(neighbors(node)) map (n => (node, n))
                    visitNode(nextNodes ::: restNodes)
                } else {
                    visitNode(restNodes)
                }
        }

        visitNode(List((0, 0)))
    }

    def isWall(x: Int, y: Int): Boolean = {
        def isNode = (x % 2 == 0) && (y % 2 == 0)
        def isLink = (x % 2 == 0) || (y % 2 == 0)

        def isInterRow = y % 2 > 0

        if (isNode)
            false
        else if (isLink) {
            val nodeX = x / 2
            val nodeY = y / 2
            if (isInterRow)
               !(adjRooms(nodeX, nodeY) contains (nodeX, nodeY + 1))
            else
               !(adjRooms(nodeX, nodeY) contains (nodeX + 1, nodeY))
        } else
            true
    }

    private val graphSize = graphWidth * graphHeight
    private var graphLinks = new Array[List[Int]](graphSize)

    private def addGraphLink(node1: Int, node2: Int): Unit = {
        if (graphLinks(node1) != null)
            graphLinks(node1) = node2 :: graphLinks(node1)
        else
            graphLinks(node1) = List(node2)

        if (graphLinks(node2) != null)
            graphLinks(node2) = node1 :: graphLinks(node2)
        else
            graphLinks(node2) = List(node1)
    }

    private def isGraphLink(node1: Int, node2: Int) = graphLinks(node1) contains node2

    private def neighbors(node: Int): List[Int] = {
        val x = node % graphWidth
        val y = node / graphWidth

        var adj: List[(Int, Int)] = List()

        if (x > 0) adj = (x - 1, y) :: adj
        if (x < graphWidth - 1) adj = (x + 1, y) :: adj
        if (y > 0) adj = (x, y - 1) :: adj
        if (y < graphHeight - 1) adj = (x, y + 1) :: adj

        adj map {case (x, y) => x + y * graphWidth}
    }

    private def adjRooms(x: Int, y: Int): List[(Int, Int)] = {
        val node = x + y * graphWidth

        for (adj_node <- neighbors(node) if isGraphLink(node, adj_node))
            yield (adj_node % graphWidth, adj_node / graphWidth)
    }
}

}
