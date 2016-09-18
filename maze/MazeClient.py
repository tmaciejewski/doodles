#! /usr/bin/env python
import socket
import struct
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
        self.width = struct.unpack('!I', self.socket.recv(4))[0]
        self.height = struct.unpack('!I', self.socket.recv(4))[0]

        self.maze = []

        for _ in range(self.height):
            row = [ord(x) for x in self.socket.recv(self.width)]
            self.maze.append(row)

        self.exitX = struct.unpack('!I', self.socket.recv(4))[0]
        self.exitY = struct.unpack('!I', self.socket.recv(4))[0]

    def receive_position(self):
        self.playerX = struct.unpack('!I', self.socket.recv(4))[0]
        self.playerY = struct.unpack('!I', self.socket.recv(4))[0]

    def on_key_press(self, widget, event):
        if event.string == 'q':
            gtk.main_quit()

        if event.string != '':
            self.socket.send(event.string[0])
            self.receive_position()
            widget.queue_draw()

        if self.playerX == self.exitX and self.playerY == self.exitY:
            md = gtk.MessageDialog(widget,
                                   gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO,
                                   gtk.BUTTONS_CLOSE, "You won!")
            md.run()
            gtk.main_quit()

class Screen(gtk.DrawingArea):

    # Draw in response to an expose-event
    __gsignals__ = { "expose-event": "override" }

    def __init__(self, game):
        super(Screen, self).__init__()
        self.game = game

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
        scaleWidth = width / self.game.width
        scaleHeight = height / self.game.height
        borderWidth = (scaleHeight + scaleWidth) / 4

        # exit
        cr.set_source_rgb(0.8, 0.9, 0.1)
        cr.arc(game.exitX * scaleWidth + scaleWidth / 2,
               game.exitY * scaleHeight + scaleHeight / 2,
               (scaleWidth + scaleHeight) / 6, 0, 3.14 * 2)
        cr.fill()

        # player
        cr.set_source_rgb(0.6, 0.3, 0.8)
        cr.arc(game.playerX * scaleWidth + scaleWidth / 2,
               game.playerY * scaleHeight + scaleHeight / 2,
               (scaleWidth + scaleHeight) / 6, 0, 3.14 * 2)
        cr.fill()

        # border
        cr.set_line_width(borderWidth)
        cr.set_source_rgb(0.3, 0.3, 0.3)
        cr.rectangle(0 - borderWidth, 0 - borderWidth, scaleWidth * self.game.width + 1.5 * borderWidth,
                     scaleHeight * self.game.height + 1.5 * borderWidth)
        cr.stroke()

        # maze
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
