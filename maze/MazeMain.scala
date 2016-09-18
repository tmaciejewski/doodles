import java.net._
import java.io._

import maze._

object MazeMain {

    var m: Maze = _
    var playerX = 0
    var playerY = 0
    var exitX = 0
    var exitY = 0

    def main(args: Array[String]): Unit = {
        val server = new ServerSocket(9999)

        val maxWidth = args(0).toInt
        val maxHeight = args(1).toInt

        m = new MazeDFS(maxWidth, maxHeight)

        handleGames(server)
    }

    def handleGames(server: ServerSocket): Unit = {
        try {
            println("waiting for new player")
            val client = server.accept()
            println("new player has connected")

            initGame()
            sendMaze(client.getOutputStream())
            gameLoop(client.getInputStream(), client.getOutputStream())
            client.close()
        } catch {
            case _ : java.net.SocketException => println("connection error")
        }

        handleGames(server)
    }

    def initGame() = {
        m.generate
        playerX = 0
        playerY = 0

        exitX = m.width -1
        val exits = List.range(0, m.height).filter(y => !m.isWall(exitX, y)).reverse
        exitY = exits.head
    }

    def sendMaze(out: OutputStream) = {
        val stream = new DataOutputStream(new BufferedOutputStream(out))
        stream.writeInt(m.width)
        stream.writeInt(m.height)
        List.range(0, m.height) foreach {y =>
            List.range(0, m.width) foreach {x =>
                if (m.isWall(x, y))
                    stream.write(1)
                else
                    stream.write(0)
            }
        }
        stream.writeInt(exitX)
        stream.writeInt(exitY)
        stream.flush()
    }

    def gameLoop(in: InputStream, out: OutputStream): Unit = {
        sendPlayerPosition(out)

        if (playerX == exitX && playerY == exitY) {
            println("player won")
        } else {
            val command = in.read()
            if (command > 0) {
                processCommand(command.toChar)
                gameLoop(in, out)
            } else {
                println("player disconnected")
            }
        }
    }

    def sendPlayerPosition(out: OutputStream) = {
        println("Sending player pos: " + playerX + " " + playerY)
        val stream = new DataOutputStream(new BufferedOutputStream(out))
        stream.writeInt(playerX)
        stream.writeInt(playerY)
        stream.flush()
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
