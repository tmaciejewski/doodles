#!/usr/bin/python

import gtk
import random
import math
import time
import threading
import sys

def general_rk_step(x, y, h, f_x, f_y, table):
    k_x = []
    k_y = []
    for row in table[:-1]:
        a = row[0]
        sum_x = sum_y = 0
        i = 0
        for b in row[1:]:
            sum_x += b * k_x[i]
            sum_y += b * k_y[i]
            i += 1
        k_x.append(f_x(x + h * sum_x, y + h * sum_y))
        k_y.append(f_y(x + h * sum_x, y + h * sum_y))

    i = 0
    fi_x = fi_y = 0
    for c in table[-1]:
        fi_x += c * k_x[i]
        fi_y += c * k_y[i]
        i += 1

    return x + h * fi_x, y + h * fi_y

def rk_step(x, y, h, f_x, f_y):
    table = [ [0], [0.5, 0.5], [0.5, 0, 0.5], [1, 0, 0, 1], \
        [1.0 / 6, 1.0 / 3, 1.0 / 3, 1.0 / 6] ]
    return general_rk_step(x, y, h, f_x, f_y, table)

def merson_step(x, y, h, f_x, f_y):
    table = [ [0], [1.0 / 3, 1.0 / 3], [1.0 / 3, 1.0 / 6, 1.0 / 6], \
        [0.5, 0.125, 0, 3.0 / 8], [1, 0.5, 0, -3.0 / 2, 2], \
        [1.0 / 6, 0, 0, 2.0 / 3, 1.0 /6] ]
    return general_rk_step(x, y, h, f_x, f_y, table)

def scraton_step(x, y, h, f_x, f_y):
    table = [ [0], [2.0 / 9, 2.0 / 9], [1.0/3, 1.0 / 12, 0.25], \
        [0.75, 69.0 / 128, -243.0/128, 270.0/128], \
        [0.9, -9 * 0.0345, 9 * 0.2025, -9 * 0.1224, 9 * 0.0544], \
        [17.0 / 162, 0, 81.0 / 170, 32.0 / 135, 250.0 / 1377] ]
    return general_rk_step(x, y, h, f_x, f_y, table)

def butcher_step(x, y, h, f_x, f_y):
    table =  [ [0], [.25, .25], [.25, .125, .125], [.5, 0, 0, .5], \
        [.75, 3.0 / 16, -3.0 / 8, 3.0 / 8, 9.0 / 16], \
        [1, -3.0 / 7, 8.0 / 7,  6.0 / 7, -12.0 / 7, 8.0 / 7], \
        [7.0 / 90, 0, 32.0 / 90, 12.0 / 90, 32.0 / 90, 7.0 / 90] ]
    return general_rk_step(x, y, h, f_x, f_y, table)

def explicit_euler_step(x, y, h, f_x, f_y):
    return x + h * f_x(x, y), y + h * f_y(x, y)

class Method(threading.Thread):
    def __init__(self, window, step_fun, order, run_lock):
        threading.Thread.__init__(self)

        self.run_lock = run_lock
        self.max_steps = 1000
        self.step_fun = step_fun
        self.order = order
        self.step = eval(window.step_entry.get_text(), {'math' : math})
        self.x = eval(window.x0_entry.get_text())
        self.y = eval(window.y0_entry.get_text())
        self.yprim_text = window.yprim_entry.get_text()
        self.xprim_text = window.xprim_entry.get_text()
        self.xprim = lambda x, y: eval(self.xprim_text,
            {'math' : math, 'x' : x, 'y' : y})
        self.yprim = lambda x, y: eval(self.yprim_text,
            {'math' : math, 'x' : x, 'y' : y})
        self.window = window

    def run(self):
        for i in range(0, self.max_steps):
            if self.run_lock.acquire(False) == False:
                break
            else:
                self.run_lock.release()

            x, y = self.x, self.y

            self.x, self.y = self.step_fun(x, y, self.step,
                self.xprim, self.yprim)

            x_half, y_half = self.step_fun(x, y, self.step / 2,
                self.xprim, self.yprim)
            x_2, y_2 = self.step_fun(x_half, y_half, self.step / 2,
                self.xprim, self.yprim)

            #error = math.sqrt((self.x - x_2)**2 + (self.y - y_2)**2) \
            #    / (2**self.order - 1)
            error = (x_2 - self.x) / (2**self.order - 1)
            self.window.error_label.set_label(str(error))

            self.window.points.append((self.x, self.y))
            self.window.d.queue_draw()

            r = math.sqrt(self.x**2 + self.y**2)
            if self.window.range < 1.5 * r:
                self.window.range = 1.5 * r

            time.sleep(0.07)
        self.window.started = False

class MainWindow():
    range = 3
    points = []

    started = False

    methods = {0 : (explicit_euler_step, 1), 1 : (rk_step, 4), \
            2 : (merson_step, 4), 3 : (scraton_step, 4), \
            4 : (butcher_step, 5)}

    def __init__(self):
        builder = gtk.Builder()
        builder.add_from_file('numerical_methods.glade')

        self.window = builder.get_object('window1')
        self.window.connect('destroy', self.close)

        self.start_button = builder.get_object('start_button')
        self.start_button.connect('clicked', self.start_method)

        self.circle_button = builder.get_object('circle_button')
        self.circle_button.connect('clicked', self.set_circle)

        self.prey_button = builder.get_object('prey_button')
        self.prey_button.connect('clicked', self.set_prey)

        self.yprim_entry = builder.get_object('yprim_entry')
        self.yprim_entry.set_text('x')

        self.xprim_entry = builder.get_object('xprim_entry')
        self.xprim_entry.set_text('-y')

        self.y0_entry = builder.get_object('y0_entry')
        self.y0_entry.set_text('0')

        self.x0_entry = builder.get_object('x0_entry')
        self.x0_entry.set_text('1')

        self.step_entry = builder.get_object('step_entry')
        self.step_entry.set_text('math.pi / 32')

        self.method_box = builder.get_object('method_box')

        self.error_label = builder.get_object('error_label')

        self.d = builder.get_object('drawingarea1')
        self.d.connect('expose-event', self.draw, None)

    def close(self, widget):
        try:
            self.run_lock.acquire()
        except:
            pass
        finally:
            gtk.main_quit()

    def set_circle(self, widget):
        self.xprim_entry.set_text('-y')
        self.yprim_entry.set_text('x')
        self.x0_entry.set_text('1')
        self.y0_entry.set_text('0')

    def set_prey(self, widget):
        self.xprim_entry.set_text('x * (5 - 0.3 * y)')
        self.yprim_entry.set_text('-y * (5 - 0.3 * x)')
        self.x0_entry.set_text('10')
        self.y0_entry.set_text('2')

    def start_method(self, widget):
        if not self.started:
            self.points = []
            self.range = 3
            self.run_lock = threading.Lock()
            method, order = self.methods[self.method_box.get_active()]
            self.method = Method(self, method, order, self.run_lock)
            self.method.start()
            self.started = True
            self.start_button.set_label('Stop')
        else:
            self.started = False
            self.run_lock.acquire()
            self.method.join()
            self.run_lock.release()
            self.start_button.set_label('Draw')


    def draw(self, widget, event, data):
        black = widget.get_colormap().alloc_color("#000000")
        red = widget.get_colormap().alloc_color("#FF0000")

        axis_gc = widget.window.new_gc(line_width = 1, foreground = black)
        points_gc = widget.window.new_gc(foreground = red)

        self.draw_axes(widget.window, axis_gc)

        if self.points != []:
            screen_points = [self.to_screen(x, y) for x, y in self.points]
            widget.window.draw_lines(points_gc, screen_points)

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

    def draw_axes(self, drawable, gc):
        self.draw_arrow(drawable, gc, 0, 0, 0, self.range)
        self.draw_arrow(drawable, gc, 0, 0, math.pi / 2, self.range)

    def draw_arrow(self, drawable, gc, x, y, angle, length):
        arrow_size = 0.1
        dy = length * math.sin(angle)
        dx = length * math.cos(angle)

        arrow_dy1 = -arrow_size * math.sin(angle + 0.5)
        arrow_dx1 = -arrow_size * math.cos(angle + 0.5)

        arrow_dy2 = -arrow_size * math.sin(angle - 0.5)
        arrow_dx2 = -arrow_size * math.cos(angle - 0.5)

        line_x1, line_y1 = self.to_screen(x + dx * 0.99, y + dy * 0.99)
        line_x2, line_y2 = self.to_screen(x - dx, y - dy)

        drawable.draw_line(gc, line_x1, line_y1, line_x2, line_y2)

        drawable.draw_polygon(gc, True,
            [self.to_screen(x + dx, y + dy),
             self.to_screen(x + dx + arrow_dx1, y + dy + arrow_dy1),
             self.to_screen(x + dx + arrow_dx2, y + dy + arrow_dy2)])


if __name__ == "__main__":
    gtk.gdk.threads_init()
    w = MainWindow()
    w.window.show()

    gtk.main()
