import scala.util.Random

package maze {

class Maze(width: Int, height: Int) {

    val totalNodes = width * height
    var mazeLinks = new Array[Boolean](totalNodes * totalNodes)

    def addMazeLink(node1: Int, node2: Int) = mazeLinks(node1 + node2 * totalNodes) = true
    
    def isMazeLink(node1: Int, node2: Int) = mazeLinks(node1 + node2 * totalNodes) 

    def neighbors(node: Int) = {
        val x = node % width
        val y = node / width

        var adj: List[(Int, Int)] = List()

        if (x > 0) adj = (x - 1, y) :: adj
        if (x < width - 1) adj = (x + 1, y) :: adj
        if (y > 0) adj = (x, y - 1) :: adj
        if (y < height - 1) adj = (x, y + 1) :: adj

        adj map (node => node._1 + node._2 * width)
    }

    def generate = {
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

    override def toString = {
        var result = "#" * width * 2 + "\n"
        var downLinks = ""

        for (node <- List.range(0, totalNodes)) {
            val x = node % width
            val y = node / width

            if (x > 0) {
                if (isMazeLink(node, node - 1))
                    result += ".."
                else
                    result += "#."

            } else {
                if (y > 0) {
                    result += "#\n" + downLinks + "\n"
                    downLinks = ""
                }
                result += "."
            }

            if (y < height - 1) {
                if (isMazeLink(node, node + width))
                    downLinks += ".#"
                else
                    downLinks += "##"
            }
        }

        result + "#\n" + "#" * width * 2 + "\n"
    }
}

}
