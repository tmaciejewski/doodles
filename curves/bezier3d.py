#!/usr/bin/python

import sys, time
import numpy as np
import scipy
from scipy import misc
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

def deCasteljou():
    global vertices

    combs_i = [float(scipy.misc.comb(control_points_i - 1, i)) for i in range(control_points_i)]
    combs_j = [float(scipy.misc.comb(control_points_j - 1, j)) for j in range(control_points_j)]

    t = time.time()
    vertices = [[] for _ in range(surface_count)]

    for u in np.linspace(0, 1, vertices_i):
        for v in np.linspace(0, 1, vertices_j):
            u_powers = [u**i for i in range(control_points_i)]
            u1_powers = [(1 - u)**i for i in range(control_points_i)]

            v_powers = [v**j for j in range(control_points_j)]
            v1_powers = [(1 - v)**j for j in range(control_points_j)]

            tmp = [np.array([0,0,0]) for _ in range(surface_count)]
            for i in range(control_points_i):
                B1 = combs_i[i] * u_powers[i] * u1_powers[control_points_i - i - 1]
                for j in range(control_points_j):
                    B2 = combs_j[j] * v_powers[j] * v1_powers[control_points_j - j - 1]
                    for surface in range(surface_count):
                        tmp[surface] = tmp[surface] + B1 * B2 * control_points[surface][control_points_j * i + j]

            for surface in range(surface_count):
                vertices[surface].append(tmp[surface][0])
                vertices[surface].append(tmp[surface][1])
                vertices[surface].append(tmp[surface][2])

    #print 'time:', time.time() - t, 'seconds'

def controlPointsVertices(control_points):
    res = []
    for p in control_points:
        for c in p:
            res.append(c)
    return res

def init():
    # depth buffer
    glEnable(GL_DEPTH_TEST)

    # perspective correction
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

    # culling

    glDisable(GL_CULL_FACE)

    glShadeModel(GL_SMOOTH)

def display():
    global control_points_changed

    if control_points_changed == True:
        deCasteljou()
        control_points_changed = False

    glMatrixMode(GL_MODELVIEW)
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glClearColor(1.0, 1.0, 1.0, 0.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glLoadIdentity()
    glTranslate(0, 0, zoom)
    glRotate(angle_y, 0.0, 1.0, 0.0)
    glRotate(angle_x, 1.0, 0.0, 0.0)
    glTranslate(- surface_count * .5, -.5, 0)

    glEnableClientState(GL_VERTEX_ARRAY)

    for surface in range(surface_count):
        # points
        glColor(0.7, 0.7, 0.7)
        glPointSize(5.0)
        glVertexPointer(3, GL_FLOAT, 0, controlPointsVertices(control_points[surface]))
        glDrawArrays(GL_POINTS, 0, len(control_points[surface]))

        # surface
        glColor(0, 0, 0)
        glVertexPointer(3, GL_FLOAT, 0, vertices[surface])
        glDrawElements(GL_QUADS, len(indices), GL_UNSIGNED_INT, indices)

    # active point
    glPointSize(8.0)
    active_x, active_y, active_z = control_points[active_surface][active_point]
    glBegin(GL_POINTS)
    glColor(0.8, 0.2, 0.2)
    glVertex(active_x, active_y, active_z)
    glEnd()

    glDisableClientState(GL_VERTEX_ARRAY)

    glutSwapBuffers()

def reshape(w, h):
    global window_height, window_width
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, float(w) / h, 0.1, 100.0)
    window_width = w
    window_height = h

def keyboard(key, x, y):
    global angle_y, angle_x, active_point, zoom

    if key == 'q':
        exit(0)

    if key == 'a':
        angle_y -= 2.0

    if key == 'd':
        angle_y += 2.0

    if key == 'w':
        angle_x += 2.0

    if key == 's':
        angle_x -= 2.0

    if key == 'r':
        zoom += 0.1

    if key == 'f':
        zoom -= 0.1

    glutPostRedisplay()

def line_dist(clicked_point, control_point):
    return np.linalg.norm(np.cross(control_point, control_point - clicked_point)) \
        / np.linalg.norm(clicked_point)

def mouse(button, state, mouse_x, mouse_y):
    global active_point, active_surface, control_points, control_points_changed

    point_step = None

    if state == GLUT_UP:
        return

    if button == 3:
        point_step = 0.02

    if button == 4:
        point_step = -0.02

    if point_step:
        control_points[active_surface][active_point][2] += point_step

        if active_point < control_points_i and active_surface > 0:
            neighbor_point = (control_points_i - 1) * control_points_j + active_point % control_points_i
            sec_neighbor_point = neighbor_point - control_points_j
            control_points[active_surface - 1][neighbor_point][2] = control_points[active_surface][active_point][2]
            control_points[active_surface - 1][sec_neighbor_point][2] += point_step
            control_points[active_surface][active_point + control_points_j][2] += point_step

        if active_point >= (control_points_i - 1) * control_points_j and active_surface < surface_count - 1:
            neighbor_point = active_point % control_points_i
            sec_neighbor_point = neighbor_point + control_points_j
            control_points[active_surface + 1][neighbor_point][2] = control_points[active_surface][active_point][2]
            control_points[active_surface + 1][sec_neighbor_point][2] += point_step
            control_points[active_surface][active_point - control_points_j][2] += point_step

        if active_point / control_points_i == 1 and active_surface > 0:
            neighbor_point = (control_points_i - 2) * control_points_j + active_point % control_points_i
            control_points[active_surface - 1][neighbor_point][2] -= point_step

        if active_point / control_points_i == control_points_i - 2 and active_surface < surface_count - 1:
            neighbor_point = control_points_j + active_point % control_points_i
            control_points[active_surface + 1][neighbor_point][2] -= point_step

        control_points_changed = True

    if button == GLUT_LEFT_BUTTON:
        viewport_matrix = [0, 0, window_width, window_height]
        projection_matrix = glGetDouble(GL_PROJECTION_MATRIX)
        modelview_matrix = glGetDouble(GL_MODELVIEW_MATRIX)
        id_matrix = [[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,1]]

        #print modelview_matrix
        #print projection_matrix
        #print viewport_matrix

        click_point = np.array(gluUnProject(mouse_x, window_height - mouse_y, 0.0,
             id_matrix,
             projection_matrix,
             viewport_matrix))

        #print 'clicked:', click_point

        active_point = 0
        active_surface = 0
        dist = np.linalg.norm(control_points[0] - click_point)
        for surface in range(surface_count):
            for i, point in enumerate(control_points[surface]):
                transf_point = np.dot(np.append(point, 1.0), modelview_matrix).flatten()[:3]
                new_dist = line_dist(click_point, transf_point)

                #print surface, transf_point, new_dist,

                if new_dist < dist:
                    active_point = i
                    active_surface = surface
                    dist = new_dist
                    #print '*',

                #print

    glutPostRedisplay()

angle_x, angle_y = 0.0, 0.0
zoom = -1.5
surface_count = 3
active_point = 0
active_surface = 0

window_width = 800
window_height = 400

control_points_i = 5
control_points_j = 5

control_points_changed = True

vertices_i = 20
vertices_j = 20

vertices = [[] for _ in range(surface_count)]

control_points = [ [np.array([surface + i, j, 0.0]) \
    for i in np.linspace(0, 1, control_points_i) \
    for j in np.linspace(0, 1, control_points_j)] for surface in range(surface_count) ]

indices = []
for i in range(vertices_i - 1):
    for j in range(vertices_j - 1):
        indices.append(vertices_j * i + j)
        indices.append(vertices_j * i + (j + 1))
        indices.append(vertices_j * (i + 1) + (j + 1))
        indices.append(vertices_j * (i + 1) + j)

glutInit(sys.argv)
glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)

init()

glutCreateWindow('Bezier surface')
glutReshapeWindow(window_width, window_height)
glutShowWindow()

glutDisplayFunc(display)
glutReshapeFunc(reshape)
glutKeyboardFunc(keyboard)
glutMouseFunc(mouse)

glutMainLoop()
