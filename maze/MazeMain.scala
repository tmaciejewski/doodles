import maze._

object MazeMain {

    def main(args: Array[String]): Unit = {
        val width = args(0).toInt
        val height = args(1).toInt
        val m = new MazeDFS(width, height)
        m.generate
        List.range(0, m.height) foreach {y =>
            List.range(0, m.width) foreach {x =>
                if (m.isWall(x, y))
                    print('#')
                else
                    print('.')
            }
            println
        }
    }
}
