import maze._

object MazeMain {

    var m: Maze = null
    var playerX = 0
    var playerY = 0

    def main(args: Array[String]): Unit = {
        val width = args(0).toInt
        val height = args(1).toInt
        m = new MazeDFS(width, height)
        m.generate
        mainLoop
    }

    def mainLoop: Unit = {
        printMaze
        val c = Console.in.read.toChar
        c match {
            case 'q' => ()
            case 'w' => {
                if (playerY > 0 && !m.isWall(playerX, playerY - 1))
                    playerY -= 1
                mainLoop
            }
            case 's' => {
                if (playerY < m.height - 1 && !m.isWall(playerX, playerY + 1))
                    playerY += 1
                mainLoop
            }
            case 'a' => {
                if (playerX > 0 && !m.isWall(playerX - 1, playerY))
                    playerX -= 1
                mainLoop
            }
            case 'd' => {
                if (playerX < m.width - 1 && !m.isWall(playerX + 1, playerY))
                    playerX += 1
                mainLoop
            }
            case _ => mainLoop
        }
    }

    def printMaze: Unit = {
        print("\u001b[2J")
        List.range(0, m.height) foreach {y =>
            List.range(0, m.width) foreach {x =>
                if (x == playerX && y == playerY)
                    print('@')
                else if (m.isWall(x, y))
                    print('#')
                else
                    print('.')
            }
            println
        }
    }
}
