#!/usr/bin/python

import gtk
import random
import math
import time
import threading
import sys

def general_rk_step(x, dx, h, f_x, table):
    k_x = []
    k_dx = []
    for row in table[:-2]:
        a = row[0]
        sum_x = sum_dx = 0
        i = 0
        for b in row[1:]:
            sum_x += b * k_x[i]
            sum_dx += b * k_dx[i]
            i += 1
        k_dx.append(f_x(x + h * sum_x, dx + h * sum_dx))
        k_x.append(dx + h * sum_dx)

    i = 0
    fi_x = fi_dx = 0
    error_x = error_dx = 0
    for c in table[-1]:
        fi_dx += c * k_dx[i]
        fi_x += c * k_x[i]

        i += 1

    return x + h * fi_x, dx + h * fi_dx

def fehlberg_step(x, dx, h, f_x):
    table = [[0],
    [1.0/4, 1.0/4],
    [3.0/8, 3.0/32, 9.0/32],
    [12.0/13, 1932.0/2197, -7200.0/2197, 7296.0/2197],
    [1, 439.0/216, -8, 3680.0/513, -845.0/4104],
    [1.0/2, -8.0/27, 2, -3544.0/2565, 1859.0/4104, -11.0/40],
    [25.0/216, 0, 1408.0/2565, 2197.0/4104, -1.0/5, 0],
    [16.0/135, 0, 6656.0/12825, 28561.0/56430, -9.0/50, 2.0/55]]
    return general_rk_step(x, dx, h, f_x, table)

def dormand_prince_step(x, dx, h, f_x):
    table =  [[0],
    [1.0/5, 1.0/5],
    [3.0/10, 3.0/40, 9.0/40],
    [4.0/5, 44.0/45, -56.0/15, 32.0/9],
    [8.0/9, 19372.0/6561, -25360.0/2187, 64448.0/6561, -212.0/729],
    [1, 9017.0/3168, -355.0/33, 46732.0/5247, 49.0/176, -5103.0/18656],
    [1, 35.0/384, 0, 500.0/1113, 125.0/192, -2187.0/6784, 11.0/84],
    [5179.0/57600, 0, 7571.0/16695, 393.0/640, -92097.0/339200, 187.0/2100, 1.0/40],
    [35.0/384, 0, 500.0/1113, 125.0/192, -2187.0/6784, 11.0/84, 0]]
    return general_rk_step(x, dx, h, f_x, table)

def fehlberg2_step(x, dx, h, f_x):
    table = [ [0],
    [2.0/27, 2.0/27],
    [1.0/9, 1.0/36, 1.0/12],
    [1.0/6, 1.0/24, 0, 1.0/8],
    [5.0/12, 5.0/12, 0, -25.0/16, 25.0/16],
    [0.5, 1.0/20, 0, 0, 1.0/4, 1.0/5],
    [5.0/6, -25.0/108, 0, 0, 125.0/108, -65.0/27, 125.0/54],
    [1.0/6, 31.0/300, 0, 0, 0, 61.0/225, -2.0/9, 13.0/900],
    [2.0/3, 2, 0, 0, -53.0/6, 704.0/45, -107.0/9, 67.0/90, 3.0],
    [1.0/3, -91.0/108, 0, 0, 23.0/108, -976.0/135, 311.0/54, -19.0/60, 17.0/6, -1.0/12],
    [1.0, 2383.0/4100, 0, 0, -341.0/164, 4496.0/1025, -301.0/82, 2133.0/4100, 45.0/82, 45.0/164, 18.0/41],
    [0, 3.0/205, 0, 0, 0, 0, -6.0/41, -3.0/205, -3.0/41, -3.0/41, 6.0/41, 0],
    [1, -1777.0/4100, 0, 0, -341.0/164, 4496.0/1025, -289.0/82, 2193.0/4100, 51.0/82, 33.0/164, 12.0/41, 0, 1],
    [41.0/840, 0, 0, 0, 0, 34.0/105, 9.0/35, 9.0/35, 9.0/280, 9.0/280, 41.0/840, 0, 0],
    [0, 0, 0, 0, 0, 34.0/105, 9.0/35, 9.0/35, 9.0/280, 9.0/280, 0, 41.0/840, 41.0/840] ]
    return general_rk_step(x, dx, h, f_x, table)

def vdp_step(x, dx):
    mi = 40
    res = mi * (1 - x**2) * dx - x
    return res

class MethodMove(threading.Thread):
    def __init__(self, window, method, run_lock):
        threading.Thread.__init__(self)
        self.run_lock = run_lock
        self.max_steps = 100000
        self.method = method
        self.step = 1.0/100
        self.x = 2
        self.dx = 0
        self.window = window

    def run(self):
        for i in range(0, self.max_steps):
            if self.run_lock.acquire(False) == False:
                break
            else:
                self.run_lock.release()

            self.x, self.dx = self.method(self.x, self.dx, self.step, vdp_step)

            self.window.points.append((i * self.step, self.x))
            self.window.d.queue_draw()
            time.sleep(self.step / 10)

        self.window.started = False

class MainWindow(gtk.Window):
    range = 30
    points = []
    screen_points = []

    started = False

    def __init__(self):
        gtk.Window.__init__(self)
        self.set_title("Van Der Pol")
        self.connect('destroy', self.close)

        self.main_box = gtk.VBox(False, 5)
        self.info_box = gtk.HBox(False, 5)

        self.d = gtk.DrawingArea()
        self.d.set_size_request(500, 500)
        self.d.add_events(gtk.gdk.BUTTON_PRESS_MASK
            | gtk.gdk.BUTTON_RELEASE_MASK | gtk.gdk.POINTER_MOTION_MASK)
        self.d.connect('expose-event', self.draw, None)

        self.stop_button = gtk.Button('Stop')
        self.stop_button.connect('clicked', self.stop_method)

        self.dp_button = gtk.Button('Dormand-Prince 4(5)')
        self.dp_button.connect('clicked', self.start_method, dormand_prince_step)

        self.rkf_button = gtk.Button('Runge-Kutta-Fehlberg 4(5)')
        self.rkf_button.connect('clicked', self.start_method, fehlberg_step)

        self.f_button = gtk.Button('Fehlberg 7(8)')
        self.f_button.connect('clicked', self.start_method, fehlberg2_step)

        self.info_box.pack_start(self.stop_button, False, False, 10)
        self.info_box.pack_start(self.dp_button, False, False, 10)
        self.info_box.pack_start(self.rkf_button, False, False, 10)
        self.info_box.pack_start(self.f_button, False, False, 10)

        self.main_box.pack_start(self.info_box, False, False, 10)
        self.main_box.pack_start(self.d, True, True, 10)

        self.add(self.main_box)

    def close(self, widget):
        try:
            self.run_lock.acquire()
        except:
            pass
        finally:
            gtk.main_quit()

    def stop_method(self, widget):
        if self.started:
            self.started = False
            self.run_lock.acquire()
            self.method.join()
            self.run_lock.release()

    def start_method(self, widget, method):
        if not self.started:
            self.screen_points = []
            self.run_lock = threading.Lock()
            self.method = MethodMove(self, method, self.run_lock)
            self.method.start()
            self.started = True

    def draw(self, widget, event, data):
        black = widget.get_colormap().alloc_color("#000000")
        red = widget.get_colormap().alloc_color("#FF0000")

        gc = widget.window.new_gc(foreground = red)
        last_gc = widget.window.new_gc(foreground = red, line_width = 4)

        for x, y in self.points:
            point = self.to_screen(x / 10.0 - self.range, y * self.range / 5.0)
            if self.screen_points == [] or point != self.screen_points[-1]:
                self.screen_points.append(point)

        self.points = []

        if len(self.screen_points) > 2:
            widget.window.draw_lines(gc, self.screen_points[:-1])
            widget.window.draw_lines(last_gc, self.screen_points[-2:])

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

    gtk.main()
