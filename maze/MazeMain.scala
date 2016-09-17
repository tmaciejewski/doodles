import java.net._
import java.io._

import maze._

object MazeMain {

    var m: Maze = _
    var playerX = 0
    var playerY = 0

    def main(args: Array[String]): Unit = {
        val server = new ServerSocket(9999)

        val maxWidth = args(0).toInt
        val maxHeight = args(1).toInt

        m = new MazeDFS(maxWidth, maxHeight)

        handleGames(server)
    }

    def handleGames(server: ServerSocket): Unit = {
        try {
            println("waiting for new client")
            val client = server.accept()
            println("new client has connected")

            playerX = 0
            playerY = 0
            m.generate

            sendMaze(client.getOutputStream())
            gameLoop(client.getInputStream(), client.getOutputStream())

            println("client disconnected")
        } catch {
            case _ : java.net.SocketException => println("connection error")
        }

        handleGames(server)
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
        stream.flush()
    }

    def gameLoop(in: InputStream, out: OutputStream): Unit = {
        sendPlayerPosition(out)
        val command = in.read()
        if (command > 0) {
            processCommand(command.toChar)
            gameLoop(in, out)
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
