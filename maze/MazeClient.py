#! /usr/bin/env python
import socket
import pygtk
pygtk.require('2.0')
import gtk, gobject, cairo

class Game:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(('127.0.0.1', 9999))

        self.receive_maze()
        self.receive_position()

    def receive_maze(self):
        self.width = ord(self.socket.recv(1)[0])
        self.height = ord(self.socket.recv(1)[0])

        print 'maze', self.width, 'x', self.height

        self.maze = []

        for _ in range(self.height):
            row = [ord(x) for x in self.socket.recv(self.width)]
            self.maze.append(row)

        print 'received maze'

    def receive_position(self):
        self.playerX = ord(self.socket.recv(1)[0])
        self.playerY = ord(self.socket.recv(1)[0])

        print 'player position:', self.playerX, self.playerY

    def on_key_press(self, widget, event):
        if event.string == 'q':
            gtk.main_quit()

        if event.string != '':
            print 'sending', event.string
            self.socket.send(event.string[0])
            self.receive_position()
            widget.queue_draw()

class Screen(gtk.DrawingArea):

    # Draw in response to an expose-event
    __gsignals__ = { "expose-event": "override" }

    def __init__(self, game):
        super(Screen, self).__init__()
        self.game = game
        self.maze = [0,1,1,0,1,0,0,1]

    # Handle the expose-event by drawing
    def do_expose_event(self, event):

        # Create the cairo context
        cr = self.window.cairo_create()

        # Restrict Cairo to the exposed area; avoid extra work
        cr.rectangle(event.area.x, event.area.y,
                event.area.width, event.area.height)
        cr.clip()

        self.draw(cr, *self.window.get_size())

    def draw(self, cr, width, height):
        print 'drawing'
        scaleWidth = width / self.game.width
        scaleHeight = height / self.game.height

        cr.set_source_rgb(0.6, 0.3, 0.8)
        cr.arc(game.playerX * scaleWidth + scaleWidth / 2,
               game.playerY * scaleHeight + scaleWidth / 2,
               (scaleWidth + scaleHeight) / 6, 0, 3.14 * 2)
        cr.fill()
        cr.set_source_rgb(0.3, 0.3, 0.3)
        for y in range(len(self.game.maze)):
            for x in range(len(self.game.maze[y])):
                if self.game.maze[y][x]:
                    cr.rectangle(x * scaleWidth, y * scaleHeight, scaleWidth, scaleHeight)
                    cr.fill()

game = Game()
window = gtk.Window()
window.connect("delete-event", gtk.main_quit)
window.connect("key-press-event", game.on_key_press)
widget = Screen(game)
widget.show()
window.add(widget)
window.present()

gtk.main()