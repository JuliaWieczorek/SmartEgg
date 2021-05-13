#!/usr/bin/python

import pygame
# import urllib
from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *
import time
import numpy as np

SCREEN_SIZE = (800, 600)

def resize(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(width) / height, 1, 10.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0.0, 1.0, -5.0,
              0.0, 0.0, 0.0,
              0.0, 1.0, 0.0)

def init():
    glEnable(GL_DEPTH_TEST)
    # The following don't seem to have any effect, so I've commented out
    # glClearColor(0.0, 0.0, 0.0, 0.0)
    # glShadeModel(GL_SMOOTH)
    # glEnable(GL_BLEND)
    # glEnable(GL_POLYGON_SMOOTH)
    # glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_LIGHTING)   # this one
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.3, 0.3, 0.3, 1.0));

def run():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE, HWSURFACE | OPENGL | DOUBLEBUF)
    resize(*SCREEN_SIZE)
    init()
    clock = pygame.time.Clock()
    cube = Cube((0.0, 0.0, 0.0), (.5, .5, .7))

    x_angle = -30.
    y_angle =  60.

    toggle = True

    while True:
        time.sleep(1)
        if toggle:
            toggle = False
            glDisable(GL_LIGHTING)
        else:
            toggle = True
            glEnable(GL_LIGHTING)
        
        then = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            if event.type == KEYUP and event.key == K_ESCAPE:
                return

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glPushMatrix()
        glRotate(float(x_angle), 1, 0, 0)
        glRotate(float(y_angle), 0, 1, 0)
        cube.render()
        glPopMatrix()
        pygame.display.flip()

class Cube(object):

    def __init__(self, position, color):
        self.position = position
        self.color = color

    num_faces = 6

    vertices = [ (-1.0, -0.25,  0.5),
                 ( 1.0, -0.25,  0.5),
                 ( 1.0, -0.25, -0.5),
                 (-1.0, -0.25, -0.5), # bottom y<0
                 (-1.0,  0.25,  0.5),
                 ( 1.0,  0.25,  0.5),
                 ( 1.0,  0.25, -0.5),
                 (-1.0,  0.25,- 0.5) ] # top y>0

    normals = [ ( 0.0, -1.0,  0.0),  # bottom
                ( 0.0, +1.0,  0.0),  # top
                (-1.0,  0.0,  0.0),  # left
                (+1.0,  0.0,  0.0),  # right
                ( 0.0,  0.0, -1.0),  # back
                ( 0.0,  0.0, +1.0) ] # front

    vertex_indices = [ (0, 1, 2, 3),  # bottom
                       (4, 5, 6, 7),  # top
                       (0, 3, 7, 4),  # left
                       (1, 2, 6, 5),  # right
                       (2, 6, 7, 3),  # back
                       (0, 1, 5, 4) ]  # front


    def render(self):
        then = pygame.time.get_ticks()
        glColor(self.color)

        vertices = self.vertices

        glBegin(GL_QUADS)

        for face_no in range(self.num_faces):
            glNormal3dv(self.normals[face_no])
            v1, v2, v3, v4 = self.vertex_indices[face_no]
            glVertex(vertices[v1])
            glVertex(vertices[v2])
            glVertex(vertices[v3])
            glVertex(vertices[v4])
        glEnd()

if __name__ == "__main__":
    run()
