#!/usr/bin/python

import gtk
import math
import time

def mandelbrot(c):
    z = 0 + 0j
    for i in range(40):
        z = z * z + c
        if abs(z) > 2:
            return i * 65535 / 40

    return 65535

def julia(z, c):
    for i in range(40):
        z = z * z + c
        if abs(z) > 2:
            return i * 65535 / 40

    return 65535

class MainWindow(gtk.Window):
    range = 1.5
    mandelbrot = []
    julia = []

    def __init__(self):
        gtk.Window.__init__(self)
        self.set_title("Fraktale")
        self.connect('destroy', gtk.main_quit)

        self.main_box = gtk.VBox(False, 5)
        self.draw_box = gtk.HBox(False, 5)

        self.d = gtk.DrawingArea()
        self.d.set_size_request(400, 400)
        self.d.add_events(gtk.gdk.BUTTON_PRESS_MASK
            | gtk.gdk.BUTTON_RELEASE_MASK | gtk.gdk.POINTER_MOTION_MASK)
        self.d.connect('expose-event', self.draw_mandelbrot, None)
        self.d.connect('button-press-event', self.generate_julia)

        self.d2 = gtk.DrawingArea()
        self.d2.connect('expose-event', self.draw_julia, None)
        self.d2.set_size_request(400, 400)

        self.draw_box.pack_start(self.d, True, True, 10)
        self.draw_box.pack_start(self.d2, True, True, 10)

        self.main_box.pack_start(self.draw_box, False, False, 10)

        self.add(self.main_box)

    def generate_julia(self, widget, data):
        self.julia = []
        w, h = self.d2.window.get_size()
        c_x, c_y = self.from_screen(data.x, data.y)
        c = complex(c_x - 0.5, c_y)
        for x in range(w):
            for y in range(h):
                x_, y_ = self.from_screen(x, y)
                self.julia.append((x, y, julia(complex(x_, y_), c)))

        self.d2.queue_draw()

    def generate_mandelbrot(self):
        self.mandelbrot = []
        w, h = self.d.window.get_size()
        for x in range(w):
            for y in range(h):
                x_, y_ = self.from_screen(x, y)
                self.mandelbrot.append((x, y, mandelbrot(complex(x_ - 0.5, y_))))

        self.d.queue_draw()

    def draw_mandelbrot(self, widget, event, data):
        for x, y, c in self.mandelbrot:
            color = widget.get_colormap().alloc_color(c, c, c)
            gc = widget.window.new_gc(foreground = color)
            widget.window.draw_point(gc, x, y)

    def draw_julia(self, widget, event, data):
        for x, y, c in self.julia:
            color = widget.get_colormap().alloc_color(c, c, c)
            gc = widget.window.new_gc(foreground = color)
            widget.window.draw_point(gc, x, y)

    def to_screen(self, x, y):
        w, h = self.d.window.get_size()
        m = min(w, h)
        x0 = w / 2.0
        y0 = h / 2.0
        scale_x = m / (2 * self.range)
        scale_y = m / (2 * self.range)

        return int(x0 + scale_x * x), int(y0 - scale_y * y)

    def from_screen(self, x, y):
        w, h = self.d.window.get_size()
        m = min(w, h)
        x0 = w / 2.0
        y0 = h / 2.0
        scale_x = m / (2 * self.range)
        scale_y = m / (2 * self.range)

        return (x - x0) / scale_x, (y0 - y) / scale_y

if __name__ == "__main__":
    gtk.gdk.threads_init()
    w = MainWindow()
    w.show_all()
    w.generate_mandelbrot()

    gtk.main()
