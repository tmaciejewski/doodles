import java.net._
import java.io._

import maze._

object MazeMain {

    var m: Maze = null
    var playerX = 0
    var playerY = 0

    def main(args: Array[String]): Unit = {
        val server = new ServerSocket(9999)
        val client = server.accept()

        val width = args(0).toInt
        val height = args(1).toInt
        m = new MazeDFS(width, height)
        m.generate

        mainLoop(client.getInputStream(), client.getOutputStream())
    }

    def mainLoop(in: InputStream, out: OutputStream): Unit = {
        printMaze(out)
        val command = in.read()
        if (command > 0) {
            processCommand(command.toChar)
            mainLoop(in, out)
        }
    }

    def printMaze(out: OutputStream): Unit = {
        val buffered = new BufferedOutputStream(out)
        List.range(0, m.height) foreach {y =>
            List.range(0, m.width) foreach {x =>
                if (x == playerX && y == playerY)
                    out.write('@')
                else if (m.isWall(x, y))
                    out.write('#')
                else
                    out.write('.')
            }
            out.write('\n')
        }
        out.flush()
    }

    def processCommand(command: Char) = command match {
        case 'w' => {
            if (playerY > 0 && !m.isWall(playerX, playerY - 1))
                playerY -= 1
        }
        case 's' => {
            if (playerY < m.height - 1 && !m.isWall(playerX, playerY + 1))
                playerY += 1
        }
        case 'a' => {
            if (playerX > 0 && !m.isWall(playerX - 1, playerY))
                playerX -= 1
        }
        case 'd' => {
            if (playerX < m.width - 1 && !m.isWall(playerX + 1, playerY))
                playerX += 1
        }
        case _ => ()
    }
}
