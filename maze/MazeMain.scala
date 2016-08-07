import maze.Maze

object MazeMain {
    def printMaze(m: Maze) = {

        val totalNodes = m.width * m.height
        val rowStarts = List.range(0, totalNodes, m.width)

        def printLinkRight = print("..")

        def printBlockedRight = print("#.")

        def printLinkDown = print(".#")

        def printBlockedDown = print("##")

        def printBorder(width: Int) = println("#" * width * 2 + "#")

        def printRow(nodes: List[Int]) = {
            print("#.")
            nodes.tail foreach (node =>
                if (m.isMazeLink(node, node - 1))
                    printLinkRight
                else
                    printBlockedRight
            )
            println("#")
        }

        def printInterRow(nodes: List[Int]) = {
            print("#")
            nodes foreach (node =>
                if (m.isMazeLink(node, node - m.width))
                    printLinkDown
                else
                    printBlockedDown
            )
            println
        }

        printBorder(m.width)
        printRow(List.range(rowStarts.head, rowStarts.head + m.width))
        rowStarts.tail foreach {start =>
            val row = List.range(start, start + m.width)
            printInterRow(row)
            printRow(row)
        }
        printBorder(m.width)
    }

    def main(args: Array[String]): Unit = {
        val width = 30
        val height = 15
        val m = new Maze(width, height)
        m.generate
        printMaze(m)
    }
}
