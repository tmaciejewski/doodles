import maze._

object MazeMain {

    def main(args: Array[String]): Unit = {
        val width = args(0).toInt
        val height = args(1).toInt
        val m = new MazeDFS(width, height)
        m.generate
        println(m.mkString)
    }
}
