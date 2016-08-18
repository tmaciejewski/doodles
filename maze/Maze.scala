import scala.util.Random

package maze {

abstract class Maze {
    val width: Int
    val height: Int   

    def generate: Unit

    def mkString: String = {
        val blockedChar = '#'
        val freeChar = '.'

        def makeLink(x1: Int, y1: Int)(x2: Int, y2: Int) = {
            if (adjRooms(x1, y1) contains (x2, y2))
                freeChar
            else
                blockedChar
        }

        def makeRow(row: List[(Int, Int)]): String = {
            val l = row.tail map {case (x, y) => makeLink(x, y)(x - 1, y)}
            l.mkString(".", ".", ".")
        }

        def makeInterRow(row: List[(Int, Int)]): String = {
            val l = row map {case (x, y) => makeLink(x, y)(x, y - 1)}
            l.mkString("#")
        }

        val rows = for (y <- List.range(0, height))
                     yield for (x <- List.range(0, width))
                       yield (x, y)
        
        val x: List[String] = rows.tail flatMap {row =>
            List(makeInterRow(row), makeRow(row))
        }
        (makeRow(rows.head) :: x).mkString("\n")
    }

    protected val totalNodes = width * height
    protected var mazeLinks = new Array[Boolean](totalNodes * totalNodes)

    protected def addMazeLink(node1: Int, node2: Int): Unit = {
        mazeLinks(node1 + node2 * totalNodes) = true
        mazeLinks(node2 + node1 * totalNodes) = true
    }

    protected def isMazeLink(node1: Int, node2: Int): Boolean =
        mazeLinks(node1 + node2 * totalNodes)

    protected def neighbors(node: Int): List[Int] = {
        val x = node % width
        val y = node / width

        var adj: List[(Int, Int)] = List()

        if (x > 0) adj = (x - 1, y) :: adj
        if (x < width - 1) adj = (x + 1, y) :: adj
        if (y > 0) adj = (x, y - 1) :: adj
        if (y < height - 1) adj = (x, y + 1) :: adj

        adj map {case (x, y) => x + y * width}
    }

    protected def adjRooms(x: Int, y: Int): List[(Int, Int)] = {
        val node = x + y * width
        for (adj_node <- neighbors(node) if isMazeLink(node, adj_node))
            yield (adj_node % width, adj_node / width)
    }
}

class MazeDFS(val width: Int, val height: Int) extends Maze {
    def generate: Unit = {
        var visited = new Array[Boolean](totalNodes)

        def visitNode(node: Int): Unit = {
            visited(node) = true
            val nextNodes = Random.shuffle(neighbors(node))
            nextNodes foreach { nextNode =>
                if (!visited(nextNode)) {
                    addMazeLink(node, nextNode)
                    visitNode(nextNode)
                }
            }
        }

        visitNode(0)
    }
}

}
