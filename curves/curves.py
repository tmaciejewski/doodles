#!/usr/bin/python

import gtk

import matplotlib
matplotlib.use('GTKCairo')

from matplotlib.backends.backend_gtkcairo import FigureCanvasGTKCairo
import matplotlib.pyplot as plt
import numpy as np
import time

def cspline_basis(knots, i, j, t):
    if j == 0:
        if knots[i] <= t < knots[i + 1]:
            return 1
        else:
            return 0
    else:
        base_a = cspline_basis(knots, i, j - 1, t)
        base_b = cspline_basis(knots, i + 1, j - 1, t)

        a = base_a * (t - knots[i]) / (knots[i + j] - knots[i])
        b = base_b * (knots[i + j + 1] - t) / (knots[i + j + 1] - knots[i + 1])

        return a + b

def cspline(control_points, p = 3):
    curve = []
    knots = np.linspace(0, 1, len(control_points) + p + 1)

    if len(control_points) < p:
        return control_points

    for t in np.linspace(knots[p], knots[-p], 100):
        sum_x = 0
        sum_y = 0
        for i in range(len(control_points)):
            basis = cspline_basis(knots, i, p, t)
            sum_x += control_points[i][0] * basis
            sum_y += control_points[i][1] * basis

        curve.append((sum_x, sum_y))

    return curve

def deCasteljau(control_points):
    curve = []
    for t in np.linspace(0, 1, 100):
        temp_points = list(control_points)
        while len(temp_points) > 1:
            for i, (Wx, Wy) in enumerate(temp_points[:-1]):
                Vx, Vy = temp_points[i + 1]
                temp_points[i] = (1 - t) * Wx + t * Vx, (1 - t) * Wy + t * Vy
            temp_points.pop()
        curve.append(temp_points[0])
    return curve

def add_point(event):
    i = {1 : 0, 3 : 1}[event.button]
    if event.xdata != None and event.ydata != None:
        control_points[i].append((event.xdata, event.ydata))

        len1, len2 = len(control_points[0]), len(control_points[1])
        transform_btn.set_sensitive(len1 == len2)

        update_title()

        redraw_curve(curve[i], control_points[i])
        redraw_points(points[i], control_points[i])


def redraw_curve(curve, control_points):
    if control_points == []:
        curve_xs, curve_ys = [], []
    else:
        curve_points = cspline(control_points)
        curve_xs, curve_ys = zip(*curve_points)
    curve.set_data(curve_xs, curve_ys)
    curve.figure.canvas.draw()

def redraw_points(points, control_points):
    if control_points == []:
        points_xs, points_ys = [], []
    else:
        points_xs, points_ys = zip(*control_points)
    points.set_data(points_xs, points_ys)
    points.figure.canvas.draw()

def transform(widget):
    for t in np.linspace(0, 1, 20):
        tmp_control_points = list((1 - t) * np.array(control_points[0]) + t * np.array(control_points[1]))
        redraw_curve(curve[2], tmp_control_points)
        redraw_points(points[2], tmp_control_points)
        #time.sleep(0.01)
    redraw_curve(curve[2], [])
    redraw_points

def clear(widget):
    global control_points
    control_points = [[], []]
    update_title()

    for i in range(3):
        redraw_curve(curve[i], [])
        redraw_points(points[i], [])

def update_title():
    len1, len2 = len(control_points[0]), len(control_points[1])
    ax.set_title("Blue: %d, Red: %d" % (len1, len2))
    ax.figure.canvas.draw()

control_points = [[], []]

fig = plt.figure(facecolor = 'w')
gtk_fig = FigureCanvasGTKCairo(fig)
gtk_fig.mpl_connect('button_press_event', add_point)

ax = fig.add_subplot(111)
update_title()

curve = ax.plot([], [], 'b', [], [], 'r', [], [], 'g')
points = ax.plot([], [], 'ob', [], [], 'or', [], [], 'og')

window = gtk.Window()
window.set_title('Bezier curves transformation')
window.set_default_size(500, 500)
window.connect('destroy', gtk.main_quit)

transform_btn = gtk.Button('Transform')
transform_btn.connect('clicked', transform)

clear_btn = gtk.Button('Clear')
clear_btn.connect('clicked', clear)

mainbox = gtk.VBox(False, 0)
toolbox = gtk.HBox(False, 5)

window.add(mainbox)

mainbox.pack_start(toolbox, False, False, 10)
mainbox.pack_start(gtk_fig, True, True, 0)

toolbox.pack_start(clear_btn, True, True, 10)
toolbox.pack_start(transform_btn, True, True, 10)

window.show_all()

gtk.main()
