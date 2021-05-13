#!/usr/bin/python
import math
import collections

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

class Egg(object):

    # Egg model
    radius = -(math.pi/2)

    # vertex number
    N = 8   

    # vertices buffer
    vertices = []

    # surface vertices indeces
    vertex_indices = []
    
    # surface normals buffer
    surfaceNormals = []
    
    # vertex normals buffer
    vertexNormals = []

    Point3D = collections.namedtuple('Point3D', 'x y z')

    # temperature sensor location
    temp1 = Point3D(0.0,0.0,0.0)
    temp2 = Point3D(0.0,0.0,0.0)
    temp3 = Point3D(0.0,0.0,0.0)
    temp4 = Point3D(0.0,0.0,0.0)
    # temperature sensor desc location
    tempDesc1 = Point3D(0.0,0.0,0.0)
    tempDesc2 = Point3D(0.0,0.0,0.0)
    tempDesc3 = Point3D(0.0,0.0,0.0)
    tempDesc4 = Point3D(0.0,0.0,0.0)

    def __init__(self, position, color):
        self.position = position
        self.color = color
        
        # start vertex
        self.vertices = [(0,0,-1.85)]
        
        # calculate egg vertices
        for z in range(-18, 2, 2):
            i=0

            self.radius = self.radius - ((math.pi/2)/10)
            for j in xrange(self.N):
                i= i+math.pi/4
                self.vertices.append((math.cos(i) * math.cos(self.radius), math.sin(i) * math.cos(self.radius), float(z)/10))

        for z in range(2, 10, 2):
            i=0
            self.radius = self.radius + ((math.pi/2)/5)
            for j in xrange(self.N):
                i= i+math.pi/4
                self.vertices.append((math.cos(i) * math.cos(self.radius), math.sin(i) * math.cos(self.radius), float(z)/10))

        self.vertices.append((0,0,0.85))

        # start vertex indices
        self.vertex_indices = [(0,1,2),
                              (0,2,3),
                              (0,3,4),
                              (0,4,5),
                              (0,5,6),
                              (0,6,7),
                              (0,7,8),
                              (0,8,1)]
                                     
        # calculate egg faces through vertex indices
        for i in range(0, ((len(self.vertices)-1)/self.N)-1, 1):
            for j in range(1,self.N,1):
                self.vertex_indices.append(((i*8)+j, (i*8)+(j+1), (i*8)+(j+9), (i*8)+(j+8)))
            self.vertex_indices.append(((i*8)+(j+1), (i*8)+1, (i*8)+(j+2), (i*8)+(j+9)))  


        self.vertex_indices.append((113,105,106))
        self.vertex_indices.append((113,106,107))
        self.vertex_indices.append((113,107,108))
        self.vertex_indices.append((113,108,109))
        self.vertex_indices.append((113,109,110))
        self.vertex_indices.append((113,110,111))
        self.vertex_indices.append((113,111,112))
        self.vertex_indices.append((113,112,105))

        # calculate egg surface normals
        for face_no in range(0,8,1):
            v1, v2, v3 = self.vertex_indices[face_no]
            poly = [self.Point3D(self.vertices[v1][0], self.vertices[v1][1], self.vertices[v1][2]),
                    self.Point3D(self.vertices[v2][0], self.vertices[v2][1], self.vertices[v2][2]),
                    self.Point3D(self.vertices[v3][0], self.vertices[v3][1], self.vertices[v3][2])]
            self.surfaceNormals.append(self.surface_normal(poly))

        for face_no in range(8,112,1):
            v1, v2, v3, v4 = self.vertex_indices[face_no]
            poly = [self.Point3D(self.vertices[v1][0], self.vertices[v1][1], self.vertices[v1][2]),
                    self.Point3D(self.vertices[v2][0], self.vertices[v2][1], self.vertices[v2][2]),
                    self.Point3D(self.vertices[v3][0], self.vertices[v3][1], self.vertices[v3][2]),
                    self.Point3D(self.vertices[v4][0], self.vertices[v4][1], self.vertices[v4][2])]
            self.surfaceNormals.append(self.surface_normal(poly))

        for face_no in range(112,120,1):
            v1, v2, v3 = self.vertex_indices[face_no]
            poly = [self.Point3D(self.vertices[v1][0], self.vertices[v1][1], self.vertices[v1][2]),
                    self.Point3D(self.vertices[v2][0], self.vertices[v2][1], self.vertices[v2][2]),
                    self.Point3D(self.vertices[v3][0], self.vertices[v3][1], self.vertices[v3][2])]
            self.surfaceNormals.append(self.surface_normal(poly))

        # calculate egg vertex normals
        self.vertex_normal()

        # TODO 1:calibration 
        self.temp1 = self.pointOnCircle(1.02, 135, self.Point3D(0.0, 0.0, 0.0))
        self.temp2 = self.pointOnCircle(1.02, 45, self.Point3D(0.0, 0.0, 0.0))
        self.temp3 = self.pointOnCircle(1.02, 315, self.Point3D(0.0, 0.0, 0.0))
        self.temp4 = self.pointOnCircle(1.02, 225, self.Point3D(0.0, 0.0, 0.0))

        self.tempDesc1 = self.pointOnCircle(1.1, 135, self.Point3D(0.0, 0.0, 0.0))
        self.tempDesc2 = self.pointOnCircle(1.1, 45, self.Point3D(0.0, 0.0, 0.0))
        self.tempDesc3 = self.pointOnCircle(1.1, 315, self.Point3D(0.0, 0.0, 0.0))
        self.tempDesc4 = self.pointOnCircle(1.1, 225, self.Point3D(0.0, 0.0, 0.0))

    def surface_normal(self, poly):
        n = [0.0, 0.0, 0.0]

        for i, v_curr in enumerate(poly):
            v_next = poly[(i+1) % len(poly)]
            n[0] += (v_curr.y - v_next.y) * (v_curr.z + v_next.z)
            n[1] += (v_curr.z - v_next.z) * (v_curr.x + v_next.x)
            n[2] += (v_curr.x - v_next.x) * (v_curr.y + v_next.y)

        return n

    def test_surface_normal(self):
        poly = [self.Point3D(0.0, 0.0, 0.0),
                self.Point3D(0.0, 1.0, 0.0),
                self.Point3D(1.0, 1.0, 0.0),
                self.Point3D(1.0, 0.0, 0.0)]

        assert self.surface_normal(poly) == [0.0, 0.0, 1.0]

    def vertex_normal(self):
        for i in xrange(len(self.vertices)):
            tempNorm = [0.0, 0.0, 0.0]
            numFaces = 0
            for idx, face in enumerate(self.vertex_indices):
                if i in face:
                    tempNorm[0] += self.surfaceNormals[idx][0]
                    tempNorm[1] += self.surfaceNormals[idx][1]
                    tempNorm[2] += self.surfaceNormals[idx][2]
                    numFaces += 1
            newList = [x / numFaces for x in tempNorm]
            self.vertexNormals.append(newList)

    def drawText(self, pygame, x, y, z, text, fontSize):
        position = (x, y, z)                                                       
        font = pygame.font.Font(None, fontSize)                                          
        textSurface = font.render(text, True, (255,255,255,255),(0,0,0,255))                                     
        textData = pygame.image.tostring(textSurface, "RGBA", True)                
        glRasterPos3d(*position)                                                
        glDrawPixels(textSurface.get_width(), textSurface.get_height(),         
                    GL_RGBA, GL_UNSIGNED_BYTE, textData)

    def drawText3D(x, y, z, text):                                                
        position = (x, y, z)                                                       
        font = pygame.font.Font(None, 30)                                          
        textSurface = font.render(text, True, (255,255,255,255),(0,0,0,255))                                     
        textData = pygame.image.tostring(textSurface, "RGBA", True)                
        glRasterPos3d(*position)                                                
        glDrawPixels(textSurface.get_width(), textSurface.get_height(),         
                    GL_RGBA, GL_UNSIGNED_BYTE, textData)

    def pointOnCircle(self, radius, angleInDegrees, origin):
        # Convert from degrees to radians via multiplication by PI/180        
        x = radius * math.cos(angleInDegrees * math.pi / 180.0) + origin[0];
        y = radius * math.sin(angleInDegrees * math.pi / 180.0) + origin[1];
        return self.Point3D(x, y, origin[2])
    
    def render(self, pygame):
        glColor(self.color)

        vertices = self.vertices
        
        glBegin(GL_TRIANGLES)

        # Draw sharp end faces of the egg
        for face_no in range(0,8,1):
            v1, v2, v3 = self.vertex_indices[face_no]
            glNormal3dv(self.vertexNormals[v1])
            glVertex(self.vertices[v1])
            glNormal3dv(self.vertexNormals[v2])
            glVertex(self.vertices[v2])
            glNormal3dv(self.vertexNormals[v3])
            glVertex(self.vertices[v3])

        # Draw flat end faces of the egg
        for face_no in range(112,120,1):
            v1, v2, v3 = self.vertex_indices[face_no]
            glNormal3dv(self.vertexNormals[v1])
            glVertex(self.vertices[v1])
            glNormal3dv(self.vertexNormals[v2])
            glVertex(self.vertices[v2])
            glNormal3dv(self.vertexNormals[v3])
            glVertex(self.vertices[v3])
            
        glEnd()
        
        # Draw all main faces of the egg
        glBegin(GL_QUADS)
        for face_no in range(8,112,1):
            v1, v2, v3, v4 = self.vertex_indices[face_no]
            glNormal3dv(self.vertexNormals[v1])
            glVertex(self.vertices[v1])
            glNormal3dv(self.vertexNormals[v2])
            glVertex(self.vertices[v2])
            glNormal3dv(self.vertexNormals[v3])
            glVertex(self.vertices[v3])
            glNormal3dv(self.vertexNormals[v4])
            glVertex(self.vertices[v4])
            
        glEnd()

        # TODO 2: This needs to be done through calibration
        # Draw 4 temperature sensors
        glPointSize(7)
        glBegin(GL_POINTS)
        
        # temp #
        glColor((0.92,0,0.25))  # light red
        glVertex(self.temp1)
        # temp #
        glColor((0.2,1,0))      # light green
        glVertex(self.temp2)
        # temp #
        glColor((0,0.8,1))      # light blue
        glVertex(self.temp3)
        # temp #
        glColor((0.78,0,0.9))   # light purple
        glVertex(self.temp4)
        glEnd()
        
        # Label temperature sensor
        self.drawText(pygame, self.tempDesc1[0], self.tempDesc1[1], 0.2, "TEMP1", 20)
        self.drawText(pygame, self.tempDesc2[0], self.tempDesc2[1], 0.2, "TEMP2", 20)
        self.drawText(pygame, self.tempDesc3[0], self.tempDesc3[1], 0.2, "TEMP3", 20)
        self.drawText(pygame, self.tempDesc4[0], self.tempDesc4[1], 0.2, "TEMP4", 20)
