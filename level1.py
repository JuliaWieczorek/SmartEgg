#!/usr/bin/python

import pygame
from tkinter import *
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog, constants
from tkintertable import TableCanvas, TableModel, RowHeader

from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import os
import math
import csv
import collections

SCREEN_SIZE = (700, 600)
SCALAR = .5
SCALAR2 = 0.2

# Tkinter objects
root = None
embedFrame = None
recordsFrame = None

# pygame loop control variable
play = True

# current record variables
time = ''
x_angle = 0
y_angle = 0
day = ''
month = ''
year = ''

# data collections
table = None
model = None

def resize(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(width) / height, 1, 10.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(-7.0, 3.0, 0.0,
              0.0, 0.0, 0.0,
              0.0, 1.0, 0.0)

def dist(a,b):
    return math.sqrt((a*a)+(b*b))

def get_roll(x,y,z):
    radians = math.atan2(x, y)
    return math.degrees(radians)

def get_pitch(x,y,z):
    radians = math.atan2((-z) , dist(x,y))
    return math.degrees(radians)

def init_opengl():
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_BLEND)
    glEnable(GL_POLYGON_SMOOTH)
    glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_LIGHTING)

    mat_specular = [ 1.0, 1.0, 1.0, 1.0 ]
    mat_shininess = [ 50.0 ]
    light_position = [ -15.0, 10.0, 5.0, 1.0 ]
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glShadeModel(GL_SMOOTH)

    glMaterialfv(GL_FRONT, GL_SPECULAR, mat_specular)
    glMaterialfv(GL_FRONT, GL_SHININESS, mat_shininess)
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_NORMALIZE)

def load_data(filename):
    global day, month, year

    data = {}
     
    with open(filename, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        i = 0
        for row in reader:
            # get values from file
            time    = day+"-"+month+"-"+year+" "+row[0]
            x       = float(row[1])
            y       = float(row[2])
            z       = float(row[3])
            # add tuple to a dictionary
            data.update( { i : dict(zip(['time', 'x', 'y', 'z'], [time, x, y, z]))} )
            i += 1
    return data

def get_record(index):  
    record = table.model.getRecordAtRow(index)

    time              = record.get('time')
    accel_xout_scaled = float(record.get('x'))
    accel_yout_scaled = float(record.get('y'))
    accel_zout_scaled = float(record.get('z'))

    result = str(time)+" "+str(get_roll(accel_xout_scaled,accel_yout_scaled,accel_zout_scaled))+" "+str(get_pitch(accel_xout_scaled,accel_yout_scaled,accel_zout_scaled))
    print(result)
    return result.split(" ")

def drawText(x, y, text):                                                
    position = (x, y, -3)                                                       
    font = pygame.font.Font(None, 30)                                          
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


def drawXYZCoordinate():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glColor((1.,1.,1.))
    glLineWidth(1)
    glBegin(GL_LINES)

    # draw coordinate system (x, y, z)
    for x in range(-20, 22, 2):
        glVertex3f(x/10.,-1,-2)
        glVertex3f(x/10.,-1,2)
    
    for z in range(-20, 22, 2):
        glVertex3f(-2, -1, z/10.)
        glVertex3f( 2, -1, z/10.)
        
    glEnd()

    # draw xyz axis
    glLineWidth(2)
    glBegin(GL_LINES)
    # draw line with arrow for x axis
    glColor3f(1.0, 0.0, 0.0)

    glVertex3f(-2.2, -1.0, -2.4);
    glVertex3f(-1.2, -1.0, -2.4);
    glVertex3f(-1.2, -1.0, -2.4);
    glVertex3f(-1.3, -0.98, -2.4);
    glVertex3f(-1.3, -0.98, -2.4);
    glVertex3f(-1.3, -1.02, -2.4);
    glVertex3f(-1.3, -1.02, -2.4);
    glVertex3f(-1.2, -1.0, -2.4);

    # draw line with arrow for y axis
    glColor3f(0.0, 1.0, 0.0)

    glVertex3f(-2.2, -1.0, -2.4);
    glVertex3f(-2.2, -0.6, -2.4);
    glVertex3f(-2.2, -0.6, -2.4);
    glVertex3f(-2.22, -0.7, -2.4);
    glVertex3f(-2.22, -0.7, -2.4);
    glVertex3f(-2.18, -0.7, -2.4);
    glVertex3f(-2.18, -0.7, -2.4);
    glVertex3f(-2.2, -0.6, -2.4);

    # draw line with arrow for z axis
    glColor3f(0.0, 0.0, 1.0)

    glVertex3f(-2.2, -1.0, -2.4);
    glVertex3f(-2.2, -1.0, -2.0);
    glVertex3f(-2.2, -1.0, -2.0);
    glVertex3f(-2.18, -1.0, -2.1);
    glVertex3f(-2.18, -1.0, -2.1);
    glVertex3f(-2.22, -1.0, -2.1);
    glVertex3f(-2.22, -1.0, -2.1);
    glVertex3f(-2.2, -1.0, -2.0);
        
    glEnd()

def openfile():
    global table, time, x_angle, y_angle, day, month, year, root, embedFrame, recordsFrame, play

    name = filedialog.askopenfilename(initialdir = ".",title = "Select file", filetypes =(("Text File", "*.txt"),("All Files","*.*")))
    
    if name == "":
        # if file openning was cancelled then return
        return
    else:
        try:
            path = name.split('/')
            # get date from file name
            filename = path[len(path)-1]
            day = filename[6:8]
            month = filename[4:6]
            year = filename[2:4]

            # create data
            model = TableModel()
            # load data
            data = load_data(name)
            # import data ti tablemodel
            model.importDict(data)
        except:
            tk.messagebox.showerror("Error","File reading failed!")
            return

    # If another file is open already then close it
    if table != None :
        closefile()
    
    # Change App title to include currently open file
    root.title('Smart Egg 3D Visualisation - '+filename)

    # Create embed frame for pygame window
    embedFrame = tk.Frame(root, width=700, height=600) 
    embedFrame.grid(row=0,column=0)
    # Create embed frame for table
    recordsFrame = tk.Frame(root, width=300, height=600)
    recordsFrame.grid(row=0,column=1)
    recordsFrame.pack_propagate(0)
    # Create table for records preview
    table = TableCanvas(recordsFrame,name="tablica", model=model, width=300, height=600, cols=0, rows=0,  cellwidth=50, editable=False, showkeynamesinheader=True, reverseorder=0)
    table.grid(row=0,sticky=W+N+S)
    table.createTableFrame()
    # arrange columns width and order
    model.moveColumn(model.getColumnIndex('time'),1)
    model.moveColumn(model.getColumnIndex('x'),2)
    model.moveColumn(model.getColumnIndex('y'),3)
    model.moveColumn(model.getColumnIndex('z'),4)
    model.columnwidths['time'] = 150
    
    table.redrawTable()
    
    # Initiate and embed pygame
    os.environ['SDL_WINDOWID'] = str(embedFrame.winfo_id())
    #os.environ['SDL_VIDEODRIVER'] = 'windib'
    screen = pygame.display.set_mode(SCREEN_SIZE, HWSURFACE | OPENGL | DOUBLEBUF)
    resize(*SCREEN_SIZE)
    pygame.init()
    pygame.display.init()

    #Bind keys and buttons events
    root.bind('<ButtonRelease-1>', handle_click)    #click release event
    root.bind_all("<Up>", handle_arrow_keys)        #press Up key event
    root.bind_all("<Down>", handle_arrow_keys)      #press Down key event
    root.bind_all("<Left>", handle_arrow_keys)      #press Left key event
    root.bind_all("<Right>", handle_arrow_keys)     #press Right key event
    
    # Initiate OpenGL
    init_opengl()

    # Create OpenGL object
    egg = Egg((0.7, 0.0, 0.0), (1, .95, .8))

    # Load first element
    values = get_record(0)
    if values != None:
        time = values[0]+' '+values[1]
        x_angle = values[2]
        y_angle = values[3]

    root.update()

    # loop control variable
    play = True

    while play:
        drawXYZCoordinate()
        # Draw XYZ axis labels
        drawText3D(-1.2, -1.0, -2.4, 'x')
        drawText3D(-2.2, -0.6, -2.4, 'y')
        drawText3D(-2.2, -1.0, -2.0, 'z')
        for event in pygame.event.get():
            if event.type == KEYUP:
                handle_arrow_keys(event.key)

        # TODO 2: Mark Temperature sensors are reference
                
        glPushMatrix()
        # rotate object
        glRotate(float(x_angle), 0, 0, 1)
        glRotate(float(y_angle), 1, 0, 0)
        # render object and text
        egg.render()
        glPopMatrix()
        drawText(0, 2, time)
        # refresh screen    
        pygame.display.flip()
        root.update() 

def closefile():
    global time, x_angle, y_angle, day, month, year, table, root, embedFrame, recordsFrame, play
    # reset app title
    root.title('Smart Egg 3D Visualisation')

    # reset record variables
    time = ''
    x_angle = 0
    y_angle = 0
    day = ''
    month = ''
    year = ''

    # exit loop
    play = False

    # destroy frames
    try:
        table.destroy()
        embedFrame.destroy()
        recordsFrame.destroy()
        pygame.quit()
    except:
        root.update()
        return
    root.update()

def exitapp():
    closefile()
    root.destroy()

#Click event callback function.    
def handle_click(event):
    global table, time, x_angle, y_angle

    if isinstance(event.widget, (TableCanvas, RowHeader)):
        try:
            index = table.get_row_clicked(event)
            values = get_record(index)
            time = values[0]+' '+values[1]
            x_angle = values[2]
            y_angle = values[3]
        except:
            print('Error at click')

def handle_arrow_keys(event):
    global table, time, x_angle, y_angle
    
    if isinstance(event, Event):
        if event.keysym == 'Up':
            event = K_UP
        elif event.keysym == 'Down':
            event = K_DOWN
    
    # get visible region for scroll control   event != None and 
    x1, y1, x2, y2 = table.getVisibleRegion()
    startvisiblerow, endvisiblerow = table.getVisibleRows(y1, y2)
    if event == K_UP:
        if table.getSelectedRow() > 0:
            table.gotoprevRow()
        # check if move scroll up is needed
        if (table.getSelectedRow() - startvisiblerow) < 1:
            table.yview_scroll(-1, UNITS)
            table.tablerowheader.yview_scroll(-1, UNITS)
            table.redrawVisible()
    if event == K_DOWN:
        if table.getSelectedRow() < table.model.getRowCount()-1:
            table.gotonextRow()
        # check if move scroll down is needed
        if (endvisiblerow - table.getSelectedRow()) < 3:
            table.yview_scroll(1, UNITS)
            table.tablerowheader.yview_scroll(1, UNITS)
            table.redrawVisible()
            
    # display move on the pygame
    index = table.getSelectedRow()
    values = get_record(index)
    time = values[0]+' '+values[1]
    x_angle = values[2]
    y_angle = values[3]

def run():
    global root
    
    # tk init
    root = tk.Tk()
    root.title('Smart Egg 3D Visualisation')
    root.geometry("1100x650")    #Set the size of the app to be 800x600
    root.resizable(0, 0)        #Don't allow resizing in the x or y direction

    # Initializa Menubar
    menubar = Menu(root)
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="Open file", command=openfile)
    filemenu.add_command(label="Close file", command=closefile)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=exitapp)
    menubar.add_cascade(label="File", menu=filemenu)
    root.config(menu=menubar)

    #Enter mainlopp
    root.mainloop()
    

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

    def __init__(self, position, color):
        self.position = position
        self.color = color

        # start vertex
        self.vertices = [(0,0,-1.85)]
        
        # calculate egg vertices
        for z in range(-18, 2, 2):
            i=0

            self.radius = self.radius - ((math.pi/2)/10)
            for j in range(self.N):     # xrange(2.7) to range (3.6)
                i= i+math.pi/4
                self.vertices.append((math.cos(i) * math.cos(self.radius), math.sin(i) * math.cos(self.radius), float(z)/10))

        for z in range(2, 10, 2):
            i=0
            self.radius = self.radius + ((math.pi/2)/5)
            for j in range(self.N):    # xrange(2.7) to range (3.6)
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
        for i in range(len(self.vertices)): # xrange(2.7) to range (3.6)
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

    def render(self):
        then = pygame.time.get_ticks()
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

if __name__ == "__main__":
    run()
