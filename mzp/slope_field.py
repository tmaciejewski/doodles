#!/usr/bin/python

import gtk
import random
import math

class MainWindow(gtk.Window):
    step = 0.5
    range = 5
    formula = "x / y"
    linking = False
    linking_points = []

    def __init__(self):
        gtk.Window.__init__(self)
        self.set_title("Direction field")
        self.connect('destroy', gtk.main_quit)

        self.main_box = gtk.VBox(False)
        self.upper_box = gtk.HBox(False)
        self.info_box = gtk.HBox(False, 5)

        self.formula_entry = gtk.Entry()
        self.formula_entry.set_text(self.formula)
        self.formula_entry.connect('key-press-event',
            self.formula_entry_key_press)

        self.entry_label = gtk.Label("y' =")

        self.step_label = gtk.Label("Step: ")
        self.step_label.set_justify(gtk.JUSTIFY_RIGHT)
        step_adj = gtk.Adjustment(self.step, 0, 10, 0.1, 0.5)
        self.step_spin = gtk.SpinButton(step_adj, digits = 2)
        self.step_spin.connect('value-changed', self.change_step)

        self.range_label = gtk.Label("Range: ")
        self.range_label.set_justify(gtk.JUSTIFY_RIGHT)
        range_adj = gtk.Adjustment(self.range, 0.5, 50, 0.5, 5)
        self.range_spin = gtk.SpinButton(range_adj, digits = 2)
        self.range_spin.connect('value-changed', self.change_range)

        self.d = gtk.DrawingArea()
        self.d.set_size_request(500, 500)
        self.d.add_events(gtk.gdk.BUTTON_PRESS_MASK
            | gtk.gdk.BUTTON_RELEASE_MASK | gtk.gdk.POINTER_MOTION_MASK)
        self.d.connect('expose-event', self.draw, None)
        self.d.connect('button-press-event', self.switch_linking, True)
        self.d.connect('button-release-event', self.switch_linking, False)
        self.d.connect('motion-notify-event', self.update_linking)

        self.upper_box.pack_start(self.entry_label, False, False, 5)
        self.upper_box.pack_start(self.formula_entry, True, True)
        self.upper_box.pack_start(gtk.Label('click and move to draw a line'),
            False, False, 5)

        self.info_box.pack_start(self.step_label, False, False, 10)
        self.info_box.pack_start(self.step_spin)
        self.info_box.pack_start(self.range_label, False, False, 10)
        self.info_box.pack_start(self.range_spin)

        self.main_box.pack_start(self.upper_box, False, False, 10)
        self.main_box.pack_start(self.info_box, False, False, 10)
        self.main_box.pack_start(self.d, True, True, 10)

        self.add(self.main_box)

    def formula_entry_key_press(self, widget, event):
        if gtk.gdk.keyval_name(event.keyval) == 'Return':
            self.formula = self.formula_entry.get_text()
            self.d.queue_draw()

    def draw(self, widget, event, data):
        black = widget.get_colormap().alloc_color("#000000")
        red = widget.get_colormap().alloc_color("#FF0000")

        axis_gc = widget.window.new_gc(line_width = 2, foreground = black)
        arrows_gc = widget.window.new_gc(foreground = red)
        fun_gc = widget.window.new_gc(line_width = 2, foreground = red)

        self.draw_axes(widget.window, axis_gc)

        x = -self.range
        while x < self.range:
            y = -self.range
            while y < self.range:
                self.draw_vector(widget.window, arrows_gc, x, y)
                y += self.step
            x += self.step

        # link points
        if self.linking and self.linking_points != []:
            widget.window.draw_lines(fun_gc, self.linking_points)

    def generate_linking_points(self, drawable, x, y):
        self.linking_points = [self.to_screen(drawable, x, y)]
        h = self.step
        while abs(x) < self.range and abs(y) < self.range and len(self.linking_points) < 1000:
            try:
                angle = math.atan(self.eval_formula(x, y))
            except ZeroDivisionError:
                return
            except ValueError:
                return

            length = self.step / 2

            x += length * math.cos(angle)
            y += length * math.sin(angle)

            self.linking_points.append(self.to_screen(drawable, x, y))

    def switch_linking(self, widget, event, switch):
        if switch == True:
            self.linking = True
            x, y = self.from_screen(widget.window, event.x, event.y)
            self.generate_linking_points(widget.window, x, y)
        else:
            self.linking = False

        self.d.queue_draw()

    def update_linking(self, widget, event):
        if self.linking == True:
            x, y = self.from_screen(widget.window, event.x, event.y)
            self.generate_linking_points(widget.window, x, y)
            self.d.queue_draw()

    def change_range(self, widget):
        self.range = widget.get_value()
        self.d.queue_draw()

    def change_step(self, widget):
        self.step = widget.get_value()
        self.d.queue_draw()

    def to_screen(self, drawable, x, y):
        w, h = drawable.get_size()
        x0 = w / 2.0
        y0 = h / 2.0
        scale_x = w / (2 * self.range)
        scale_y = h / (2 * self.range)

        return int(x0 + scale_x * x), int(y0 - scale_y * y)

    def from_screen(self, drawable, x, y):
        w, h = drawable.get_size()
        x0 = w / 2.0
        y0 = h / 2.0
        scale_x = w / (2 * self.range)
        scale_y = h / (2 * self.range)

        return (x - x0) / scale_x, (y0 - y) / scale_y

    def eval_formula(self, x, y):
        return eval(self.formula, {"x" : x, "y" : y, "math" : math})

    def draw_axes(self, drawable, gc):
        w, h = drawable.get_size()
        self.draw_arrow(drawable, gc, 0, 0, 0, self.range, 0)
        self.draw_arrow(drawable, gc, 0, 0, math.pi / 2, self.range, 0)

    def draw_vector(self, drawable, gc, x, y):
        try:
            slope = self.eval_formula(x, y)
        except ZeroDivisionError:
            return
        except ValueError:
            return

        angle = math.atan(slope)
        epsilon = self.step / 2.5

        self.draw_arrow(drawable, gc, x, y, angle, epsilon)

    def draw_arrow(self, drawable, gc, x, y, angle, length, arrow_size = 0.6):
        dy = length * math.sin(angle)
        dx = length * math.cos(angle)

        arrow_dy1 = arrow_size * length * math.sin(angle + 0.3)
        arrow_dx1 = arrow_size * length * math.cos(angle + 0.3)

        arrow_dy2 = arrow_size * length * math.sin(angle - 0.3)
        arrow_dx2 = arrow_size * length * math.cos(angle - 0.3)

        line_x1, line_y1 = self.to_screen(drawable, x + dx, y + dy)
        line_x2, line_y2 = self.to_screen(drawable, x - dx, y - dy)

        drawable.draw_line(gc, line_x1, line_y1, line_x2, line_y2)

        drawable.draw_polygon(gc, True,
            [self.to_screen(drawable, x + 1.1 * dx, y + 1.1 * dy),
             self.to_screen(drawable, x + arrow_dx1, y + arrow_dy1),
             self.to_screen(drawable, x + arrow_dx2, y + arrow_dy2)])


if __name__ == "__main__":
    w = MainWindow()
    w.show_all()

    gtk.main()
