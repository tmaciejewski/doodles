import maze.Maze

object MazeMain {
    def printMaze(m: Maze) = {
        def printLinkRight = print("..")

        def printBlockedRight = print("#.")

        def printLinkDown = print(".#")

        def printBlockedDown = print("##")

        def printBorder(width: Int) = println("#" * width * 2 + "#")

        def printRow(row: List[(Int, Int)]) = {
            print("#.")
            row.tail foreach {case (x, y) =>
                if (m.adjRooms(x, y) contains (x - 1, y))
                    printLinkRight
                else
                    printBlockedRight
            }
            println("#")
        }

        def printInterRow(row: List[(Int, Int)]) = {
            print("#")
            row foreach {case (x, y) =>
                if (m.adjRooms(x, y) contains (x, y - 1))
                    printLinkDown
                else
                    printBlockedDown
            }
            println
        }

        val rows = for (y <- List.range(0, m.height))
                     yield for (x <- List.range(0, m.width))
                       yield (x, y)

        printBorder(m.width)
        printRow(rows.head)
        rows.tail foreach {row =>
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
