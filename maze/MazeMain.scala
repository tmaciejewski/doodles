import maze.Maze

object MazeMain {
    def main(args: Array[String]): Unit = {
        val m = new Maze(30, 15)
        m.generate
        println(m.mkString)
    }
}
