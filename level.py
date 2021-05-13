#!/usr/bin/python

import pygame
import tkinter as tk
from tkinter import *
from tkinter import constants, filedialog

import os
import urllib
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from math import radians
import math
import csv
from pygame.locals import *
#from OpenGLContext.arrays import array
import collections
import argparse
from tkintertable import TableCanvas, TableModel, RowHeader

SCREEN_SIZE = (700, 600)
SCALAR = .5
SCALAR2 = 0.2


lines = []
file_pointer = -1
reader = 0
time = ''
x_angle = 0
y_angle = 0
day = ''
month = ''
year = ''
table = None
model = None
data = {}
index = 0

# tk init
root = tk.Tk()
root.title('Smart Egg 3D Visualisation')
root.geometry("800x600")    #Set the size of the app to be 800x600
root.resizable(0, 0)        #Don't allow resizing in the x or y direction

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

def keyPressed(*args):
    if args[0] == tk.ESCAPE:
      glutDestroyWindow(tk.window)
      sys.exit()

def dist(a,b):
    return math.sqrt((a*a)+(b*b))

def get_roll(x,y,z):
    radians = math.atan2(x, y)
    return math.degrees(radians)

def get_pitch(x,y,z):
    radians = math.atan2((-z) , dist(x,y))
    return math.degrees(radians)


def init():
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
    global data, day, month, year

    with open(filename, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        i = 0
        for row in reader:
            # get values from file
            time    = day+"-"+month+"-"+year+"/"+row[0]
            x       = float(row[1])
            y       = float(row[2])
            z       = float(row[3])
            # add tuple to a dictionary
            data.update( { i : dict(zip(['time', 'x', 'y', 'z'], [time, x, y, z]))} )
            i += 1

def get_record(index):  
    record = table.model.getRecordAtRow(index)

    time              = day+"-"+month+"-"+year+"/"+record.get('time')
    accel_xout_scaled = float(record.get('x'))
    accel_yout_scaled = float(record.get('y'))
    accel_zout_scaled = float(record.get('z'))

    result = str(time)+" "+str(get_roll(accel_xout_scaled,accel_yout_scaled,accel_zout_scaled))+" "+str(get_pitch(accel_xout_scaled,accel_yout_scaled,accel_zout_scaled))
    return result.split(" ")
    
    #return data.get(index)

def read_previous_values():
    global reader
    global file_pointer
    if file_pointer <= 0:
        return

    file_pointer = file_pointer-1
    line = lines[file_pointer]
    
    print("Rekord nr:"+ str(file_pointer))
    print(str(line))
    
    time              = day+"-"+month+"-"+year+"/"+line[0]
    accel_xout_scaled = float(line[1])
    accel_yout_scaled = float(line[2])
    accel_zout_scaled = float(line[3])

    result = str(time)+" "+str(get_roll(accel_xout_scaled,accel_yout_scaled,accel_zout_scaled))+" "+str(get_pitch(accel_xout_scaled,accel_yout_scaled,accel_zout_scaled))
    return result.split(" ")

def read_next_values():
    global reader
    global file_pointer

    if file_pointer >= len(lines)-1:
        line = next(reader, None)
        if line == None:
            return
        lines.append(line)

    file_pointer = file_pointer+1
    line = lines[file_pointer]
    
    print("Rekord nr:"+ str(file_pointer))
    print(str(line))
    
    time              = day+"-"+month+"-"+year+"/"+line[0]
    accel_xout_scaled = float(line[1])
    accel_yout_scaled = float(line[2])
    accel_zout_scaled = float(line[3])

    result = str(time)+" "+str(get_roll(accel_xout_scaled,accel_yout_scaled,accel_zout_scaled))+" "+str(get_pitch(accel_xout_scaled,accel_yout_scaled,accel_zout_scaled))
    return result.split(" ")

def drawText(x, y, text):                                                
    position = (x, y, -3)                                                       
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

def donothing():
    filewin = Toplevel(root)
    button = Button(filewin, text="Do nothing button")
    button.pack()

def openfile():
    #global reader, time, x_angle, y_angle,day, month, year, table, model, data
    name = filedialog.askopenfilename(initialdir = ".",title = "Select file", filetypes =(("Text File", "*.txt"),("All Files","*.*")))
    
    #Using try in case user types in unknown file or closes without choosing a file.
    try:

        path = name.split('/')
        date = path[len(path)-1]
        day = date[6:8]
        month = date[4:6]
        year = date[2:4]

        # load data
        '''load_data(name)
        model = table.model
        model.importDict(data)
        # arrange columns width and order
        model.moveColumn(model.getColumnIndex('time'),1)
        model.moveColumn(model.getColumnIndex('x'),2)
        model.moveColumn(model.getColumnIndex('y'),3)
        model.moveColumn(model.getColumnIndex('z'),4)
        model.columnwidths['time'] = 150
        
        table.redrawTable()
        
        csvfile = open(name, 'rb')
        reader = csv.reader(csvfile, delimiter=',')

        # read first element
        values = read_next_values()
        if values != None:
            time = values[0]
            x_angle = values[1]
            y_angle = values[2]
        '''
    except:
        print("No file exists")
    

def closefile():
    global reader, time, x_angle, y_angle,day, month, year, file_pointer, data, model, table, index
    name = ''
    reader = 0
    time = ''
    x_angle = 0
    y_angle = 0
    day = ''
    month = ''
    year = ''
    file_pointer = -1
    index = 0
    # clear dataset
    data = {}
    model = table.model
    model.createEmptyModel()
    table.redrawTable()
    
def clicked(event):  #Click event callback function.
    global table, time, x_angle, y_angle, index

    if isinstance(event.widget, (TableCanvas, RowHeader)):
        try:
            index = table.get_row_clicked(event)
            values = get_record(index)
            time = values[0]
            x_angle = values[1]
            y_angle = values[2]
            
        except:
            print('Error')

    # TODO - record selection handling

    #Probably needs better exception handling, but w/e.
    '''try:
        rclicked = table.get_row_clicked(event)
        cclicked = table.get_col_clicked(event)
        clicks = (rclicked, cclicked)
        print 'clicks:', clicks
    except: 
        print 'Error'
    if clicks:
        #Now we try to get the value of the row+col that was clicked.
        try: print 'single cell:', table.model.getValueAt(clicks[0], clicks[1])
        except: print 'No record at:', clicks

        #This is how you can get the entire contents of a row.
        try: print 'entire record:', table.model.getRecordAtRow(clicks[0])
        except: print 'No record at:', clicks
    '''        
def run():
    global reader, time, x_angle, y_angle, day, month, year, table, model, index
    
    # tk init
    root = tk.Tk()
    root.title('Smart Egg 3D Visualisation')
    root.geometry("1100x650")    #Set the size of the app to be 800x600
    #root.resizable(0, 0)        #Don't allow resizing in the x or y direction

    # Initializa Menubar
    menubar = Menu(root)
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="Open file", command=openfile)
    filemenu.add_command(label="Close file", command=closefile)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=filemenu)
    root.config(menu=menubar)

    # TODO create rest only when file selected
    
    # Create embed frame for pygame window
    embed = tk.Frame(root, width=700, height=600) 
    embed.grid(row=0,column=0)
    # Create embed frame for records preview console
    records = tk.Frame(root, width=300, height=600)
    records.grid(row=0,column=1)
    records.pack_propagate(0)
    # Create Table for records preview
    model = TableModel()
    table = TableCanvas(records,name="tablica",model=model, width=300, height=600, cols=0, rows=0,  cellwidth=50, editable=False, showkeynamesinheader=True, reverseorder=0)
    table.grid(row=0,sticky=W+N+S)
    table.createTableFrame()

    root.bind('<ButtonRelease-1>', clicked)   #Bind the click release event
    
    #data = {"age":25}#dict((k,2) for k in a)
    #data = {'rec1': {'time': '12:04:44', 'x': 99.88, 'y': 108.79, 'z': 108.79},
    #        'rec2': {'time': '12:04:45','x': 99.88, 'y': 108.79, 'z': 108.79}}
    #model = table.model
    #model.importDict(data) #can import from a dictionary to populate model
    #model.moveColumn(model.getColumnIndex('time'),0)
    #model.moveColumn(model.getColumnIndex('x'),1)
    #model.moveColumn(model.getColumnIndex('y'),2)
    #model.moveColumn(model.getColumnIndex('z'),3)
    #table.autoResizeColumns()
    #table.redrawTable()
    #button1 = Button(records,text = 'Draw',  command=donothing)
    #button1.pack(side=LEFT)

    #child_env = dict(os.environ)
    #child_env['SDL_WINDOWID'] = str(embed.winfo_id())#the_window_id
    #child_env['SDL_VIDEO_WINDOW_POS'] = '{},{}'.format(left, top)
    #p = subprocess.Popen(['lib/'],env=child_env)
    root.update()
    

    os.environ['SDL_WINDOWID'] = str(embed.winfo_id())
   # os.environ['SDL_VIDEODRIVER'] = 'windib'
    #HWSURFACE |
    # TODO 1: load pygame and table only when file loaded
    screen = pygame.display.set_mode(SCREEN_SIZE, OPENGL | DOUBLEBUF)
    resize(*SCREEN_SIZE)
    pygame.init()
    pygame.display.init()
    #pygame.display.update()

    root.update()  

    init()
    clock = pygame.time.Clock()
    
    egg = Egg((0.7, 0.0, 0.0), (1, .95, .8))
    #cube = Cube((0.0, 0.0, 0.0), (1, .95, .8))
    
    # turn off autoplay
    play = False
    if file_pointer != -1:
        # read first element
        values = read_next_values()
        if values != None:
            time = values[0]
            x_angle = values[1]
            y_angle = values[2]
    
    while True:
        drawXYZCoordinate()

        #then = pygame.time.get_ticks()
        

        # TODO 1: Key control
        # TODO 2: Mark Temperature sensors are reference
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            if event.type == KEYUP:
                if event.key == K_UP:
                    if table.getSelectedRow() > 0: 
                        table.gotoprevRow()
                    #play = True
                if event.key == K_DOWN:
                    if table.getSelectedRow() < table.model.getRowCount()-1:
                        table.gotonextRow()
                    #play = False
                if play or event.key == K_RIGHT:
                    values = get_record(index)
                    #values = read_next_values()
                    print(values)
                    if values == None:
                        print("Koniec Pliku")
                    else:
                        time = values[0]
                        x_angle = values[1]
                        y_angle = values[2]
                if event.key == K_LEFT:
                    values = get_record(index)
                    print(values)
                    #values = read_previous_values()
                    if values == None:
                        print("Poczatek pliku!")
                    else:
                        time = values[0]
                        x_angle = values[1]
                        y_angle = values[2]
                if event.key == K_ESCAPE:
                    return

        # autoplay mode
        if play:
            values = read_next_values()
            if values == None:
                print("Koniec Pliku!")
            else:
                    time = values[0]
                    x_angle = values[1]
                    y_angle = values[2]

        if file_pointer != -1:
            glPushMatrix()
            # Correct
            glRotate(float(x_angle), 0, 0, 1)
            glRotate(float(y_angle), 1, 0, 0)
            egg.render()
            glPopMatrix()

            drawText(0, 2, time)
            
        pygame.display.flip()
        root.update() 


class Egg(object):

    # Egg model
    radius = -(math.pi/2)

    # vertex number
    N = 8   

    # vertices buffer
    vertices = [(0,0,-1.85)]

    # surface vertices indeces
    vertex_indices = [(0,1,2),
                      (0,2,3),
                      (0,3,4),
                      (0,4,5),
                      (0,5,6),
                      (0,6,7),
                      (0,7,8),
                      (0,8,1)]
    
   
    # surface normals buffer
    surfaceNormals = []
    
    # vertex normals buffer
    vertexNormals = []

    Point3D = collections.namedtuple('Point3D', 'x y z')

    def __init__(self, position, color):
        self.position = position
        self.color = color

        # calculate egg vertices
        for z in range(-18, 2, 2):
            i=0

            self.radius = self.radius - ((math.pi/2)/10)
            for j in range(self.N):   # xrange(2.7) to range (3.6)
                i= i+math.pi/4
                self.vertices.append((math.cos(i) * math.cos(self.radius), math.sin(i) * math.cos(self.radius), float(z)/10))

        for z in range(2, 10, 2):
            i=0
            self.radius = self.radius + ((math.pi/2)/5)
            for j in range(self.N):   # xrange(2.7) to range (3.6)
                i= i+math.pi/4
                self.vertices.append((math.cos(i) * math.cos(self.radius), math.sin(i) * math.cos(self.radius), float(z)/10))

        self.vertices.append((0,0,0.85))
                                     
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
        for i in range(len(self.vertices)):   # xrange(2.7) to range (3.6)
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
