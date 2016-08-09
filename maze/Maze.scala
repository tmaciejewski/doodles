import scala.util.Random

package maze {

class Maze(val width: Int, val height: Int) {
    def generate: Unit= {
        var visited = new Array[Boolean](totalNodes)

        def visitNode(node: Int): Unit = {
            visited(node) = true
            val nextNodes = Random.shuffle(neighbors(node))
            nextNodes foreach { nextNode =>
                if (!visited(nextNode)) {
                    addMazeLink(node, nextNode)
                    addMazeLink(nextNode, node)
                    visitNode(nextNode)
                }
            }
        }

        visitNode(0)
    }

    def adjRooms(x: Int, y: Int): List[(Int, Int)] = {
        val node = x + y * width
        for (adj_node <- neighbors(node) if isMazeLink(node, adj_node))
            yield (adj_node % width, adj_node / width)
    }

    private val totalNodes = width * height
    private var mazeLinks = new Array[Boolean](totalNodes * totalNodes)

    private def addMazeLink(node1: Int, node2: Int): Unit =
        mazeLinks(node1 + node2 * totalNodes) = true

    private def isMazeLink(node1: Int, node2: Int): Boolean =
        mazeLinks(node1 + node2 * totalNodes)

    private def neighbors(node: Int): List[Int] = {
        val x = node % width
        val y = node / width

        var adj: List[(Int, Int)] = List()

        if (x > 0) adj = (x - 1, y) :: adj
        if (x < width - 1) adj = (x + 1, y) :: adj
        if (y > 0) adj = (x, y - 1) :: adj
        if (y < height - 1) adj = (x, y + 1) :: adj

        adj map {case (x, y) => x + y * width}
    }
}

}
