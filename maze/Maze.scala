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

        def visitNode(node: Int): Unit = {
            visited(node) = true
            val nextNodes = Random.shuffle(neighbors(node))
            nextNodes foreach { nextNode =>
                if (!visited(nextNode)) {
                    addGraphLink(node, nextNode)
                    visitNode(nextNode)
                }
            }
        }

        visitNode(0)
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
    private var graphLinks = new Array[Boolean](graphSize * graphSize)

    private def addGraphLink(node1: Int, node2: Int): Unit = {
        graphLinks(node1 + node2 * graphSize) = true
        graphLinks(node2 + node1 * graphSize) = true
    }

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

        def isGraphLink(node1: Int, node2: Int) = graphLinks(node1 + node2 * graphSize)

        for (adj_node <- neighbors(node) if isGraphLink(node, adj_node))
            yield (adj_node % graphWidth, adj_node / graphWidth)
    }
}

}
