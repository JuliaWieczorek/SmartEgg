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
import subprocess
import urllib

from egg import Egg
from datetime import datetime, timedelta

SCREEN_SIZE = (700, 600)
FULLSCREEN_SIZE = (1100, 650)
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


# TODOs

# TODO1: simulate with 0,1 s interval

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


def dist(a, b):
    return math.sqrt((a * a) + (b * b))


def get_roll(x, y, z):
    radians = math.atan2(x, y)
    return math.degrees(radians)


def get_pitch(x, y, z):
    radians = math.atan2((-z), dist(x, y))
    return math.degrees(radians)


def get_roll_motion(i, roll, pivot_roll, value):
    """Function calculate movement in roll"""
    if i == 0:
        binary_roll = 0
    else:
        roll_move = roll - pivot_roll
        if roll_move > value:
            binary_roll = 1
        else:
            binary_roll = 0
    return binary_roll


def get_pitch_motion(i, pitch, pivot_pitch, value):
    """Function calculate movement in pitch"""
    if i == 0:
        binary_roll = 0
    else:
        roll_move = pitch - pivot_pitch
        if roll_move > value:
            binary_roll = 1
        else:
            binary_roll = 0
    return binary_roll


def get_roll_pitch_motion(roll, pitch):
    """Function calculate movement in vector(?) of roll and pitch"""
    if roll == 1 and pitch == 1:
        roll_pitch_motion = 1
    else:
        roll_pitch_motion = 0
    return roll_pitch_motion

def get_roll_pitch_motion(roll, pitch):
    """Function calculate movement in vector(?) of roll and pitch"""
    # shorter version - check if valid
    return 1 if roll == 1 and pitch == 1 else 0

def days_hours_minutes(td):
    return td.days, td.seconds//3600, (td.seconds//60)%60

def stat_movement_on_hour(data):
    total = 0
    l = len(data)
    first_hour = datetime.strptime(data[0]['time'], '%d-%m-%y %H:%M:%S')
    last_hour = datetime.strptime(data[l - 1]['time'], '%d-%m-%y %H:%M:%S')
    during = last_hour - first_hour
    during = days_hours_minutes(during)
    for j in data:
        if data[j]['roll motion'] > 0:
            total += 1
    if during[1] == 1:
        statement = "There was {movement} movement in one hour and {minutes} minutes.".format(movement=total, minutes=during[2])
    elif during[1] > 1:
        statement = "There were {movement} movement in {hour} hours and {minutes} minutes.".format(movement=total, hour=during[1], minutes=during[2])
    return statement

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

    mat_specular = [1.0, 1.0, 1.0, 1.0]
    mat_shininess = [50.0]
    light_position = [-15.0, 10.0, 5.0, 1.0]
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glShadeModel(GL_SMOOTH)

    glMaterialfv(GL_FRONT, GL_SPECULAR, mat_specular)
    glMaterialfv(GL_FRONT, GL_SHININESS, mat_shininess)
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_NORMALIZE)


def load_data(filename, *value):
    global day, month, year, date
    print('settings: ', value)
    data = dict()  # empty dict

    with open(filename, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        pivot_roll = 0
        pivot_pitch = 0
        i = 0
        # date = []
        for row in reader:
            # get values from file
            time = day + "-" + month + "-" + year + " " + row[0]
            # clock_time = row[0].split(':') # hour
            # date_ = datetime(int(year), int(month), int(day), int(clock_time[0]), int(clock_time[1]), int(clock_time[2]))
            # date.append(date_)
            x = float(row[1])
            y = float(row[2])
            z = float(row[3])

            # create new values
            roll = get_roll(x, y, z)
            pitch = get_pitch(x, y, z)

            binary_roll = get_roll_motion(i, roll, pivot_roll, value[0][0])
            pivot_roll = roll

            binary_pitch = get_pitch_motion(i, pitch, pivot_pitch, value[0][1])
            pivot_pitch = pitch

            binary_roll_pitch = get_roll_pitch_motion(binary_roll, binary_pitch)

            # add tuple to a dictionary
            data.update({i: dict(zip(['time', 'x', 'y', 'z', 'roll', 'pitch', 'roll motion', 'pitch motion', 'roll and pitch motion'],
                                     [time, x, y, z, round(roll, 2), round(pitch, 2), binary_roll, binary_pitch, binary_roll_pitch]))})
            i += 1
    return data

def get_record(index):
    record = table.model.getRecordAtRow(index)

    time = record.get('time')
    accel_xout_scaled = float(record.get('x'))
    accel_yout_scaled = float(record.get('y'))
    accel_zout_scaled = float(record.get('z'))

    result = str(time) + " " + str(get_roll(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)) + " " + str(
        get_pitch(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled))
    return result.split(" ")


def drawText(x, y, text):
    position = (x, y, -3)
    font = pygame.font.Font(None, 30)
    textSurface = font.render(text, True, (255, 255, 255, 255), (0, 0, 0, 255))
    textData = pygame.image.tostring(textSurface, "RGBA", True)
    glRasterPos3d(*position)
    glDrawPixels(textSurface.get_width(), textSurface.get_height(),
                 GL_RGBA, GL_UNSIGNED_BYTE, textData)


def drawText3D(x, y, z, text):
    position = (x, y, z)
    font = pygame.font.Font(None, 30)
    textSurface = font.render(text, True, (255, 255, 255, 255), (0, 0, 0, 255))
    textData = pygame.image.tostring(textSurface, "RGBA", True)
    glRasterPos3d(*position)
    glDrawPixels(textSurface.get_width(), textSurface.get_height(),
                 GL_RGBA, GL_UNSIGNED_BYTE, textData)


def drawXYZCoordinate():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glColor((1., 1., 1.))
    glLineWidth(1)
    glBegin(GL_LINES)

    # draw coordinate system (x, y, z)
    for x in range(-20, 22, 2):
        glVertex3f(x / 10., -1, -2)
        glVertex3f(x / 10., -1, 2)

    for z in range(-20, 22, 2):
        glVertex3f(-2, -1, z / 10.)
        glVertex3f(2, -1, z / 10.)

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


def read_values():
    link = "http://localhost:8080"  # TODO 5: Change this address to your settings
    f = urllib.urlopen(link)
    myfile = f.read()
    return myfile.split(" ")


# TODO stream mode + BLUETOOTH  - http://blog.bitify.co.uk/2013/11/3d-opengl-visualisation-of-data-from.html
def connect():
    global table, x_angle, y_angle, root, embedFrame, play

    server = filedialog.askopenfilename(initialdir=".", title="Select server",
                                        filetypes=(("Python files", "*.py"), ("All Files", "*.*")))

    print(server)
    if server == "":
        # if server openning was cancelled then return
        return
    else:
        try:
            path = server.split('/')
            serverfilename = path[len(path) - 1]

            cmd = 'python ' + server

            p = subprocess.Popen(cmd, shell=False)  # p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
            # out, err = p.communicate()
            # result = out.split('\n')
            # for lin in result:
            #    if not lin.startswith('#'):
            #        print(lin)
            # TODO 4: improve process control: https://stackoverflow.com/questions/3781851/run-a-python-script-from-another-python-script-passing-in-args
            # Show Confirmation if the connection was set up correctly
        except:
            tk.messagebox.showerror("Error", "Server failed!")
            return

    # TODO 3: Check if another process is not open and if is close it before staretin gthe new one.

    # If another file is open already then close it
    if table != None:
        closefile()

    # Change App title to include currently open file
    root.title('Smart Egg 3D Visualisation - ' + serverfilename)

    # Create embed frame for pygame window
    embedFrame = tk.Frame(root, width=1100, height=650)
    embedFrame.grid(row=0, column=0)

    # Initiate and embed pygame
    os.environ['SDL_WINDOWID'] = str(embedFrame.winfo_id())
    screen = pygame.display.set_mode(SCREEN_SIZE, HWSURFACE | OPENGL | DOUBLEBUF)
    resize(*FULLSCREEN_SIZE)
    pygame.init()
    pygame.display.init()

    # Initiate OpenGL
    init_opengl()

    # clock = pygame.time.Clock()

    # Create OpenGL object
    egg = Egg((0.7, 0.0, 0.0), (1, .95, .8))

    root.update()

    # loop control variable
    play = True

    while play:
        # then = pygame.time.get_ticks()

        values = read_values()
        x_angle = values[1]
        y_angle = values[2]

        drawXYZCoordinate()
        # Draw XYZ axis labels
        drawText3D(-1.2, -1.0, -2.4, 'x')
        drawText3D(-2.2, -0.6, -2.4, 'y')
        drawText3D(-2.2, -1.0, -2.0, 'z')

        glPushMatrix()
        # rotate object
        glRotate(float(x_angle), 0, 0, 1)
        glRotate(float(y_angle), 1, 0, 0)
        # render object and text
        egg.render(pygame)
        glPopMatrix()
        # refresh screen    
        pygame.display.flip()
        # root.update()


def openfile():
    # TODO: problem with data loading
    global table, time, x_angle, y_angle, day, month, year, root, embedFrame, recordsFrame, play, name, table

    name = filedialog.askopenfilename(initialdir=".", title="Select file",
                                      filetypes=(("Text File", "*.txt"), ("All Files", "*.*")))

    if name == "":
        # if file openning was cancelled then return
        return
    else:
        try:
            path = name.split("/")
            # get date from file name
            filename = path[len(path) - 1]
            day = filename[6:8]
            month = filename[4:6]
            year = filename[2:4]

            # create data
            model = TableModel()
            # load data
            data = load_data(name, (5, 5, 5))
            # import data to tablemodel
            model.importDict(data)

        except:
            tk.messagebox.showerror("Error", "File reading failed!")
            return

    # If another file is open already then close it
    if table != None:
        closefile()

    # Change App title to include currently open file
    root.title('Smart Egg 3D Visualisation ver.1.1 - ' + filename)

    # Create embed frame for pygame window
    embedFrame = tk.Frame(root, width=700, height=600)
    embedFrame.grid(row=0, column=0)
    # Create embed frame for table
    recordsFrame = tk.Frame(root, width=600, height=600)
    recordsFrame.grid(row=0, column=1)
    recordsFrame.pack_propagate(0)
    # Create table for records preview
    table = TableCanvas(recordsFrame, name="tablica", model=model, width=800, height=600, cols=0, rows=0, cellwidth=50,
                        editable=False, showkeynamesinheader=True, reverseorder=0)
    table.grid(row=0, sticky=W + N + S)

    stat_text = stat_movement_on_hour(data)
    statLabel = Label(root, text=stat_text)
    statLabel.grid(column=0, row=1)

    table.createTableFrame()
    # arrange columns width and order
    model.moveColumn(model.getColumnIndex('time'), 1)
    model.moveColumn(model.getColumnIndex('x'), 2)
    model.moveColumn(model.getColumnIndex('y'), 3)
    model.moveColumn(model.getColumnIndex('z'), 4)
    model.moveColumn(model.getColumnIndex('roll'), 5)
    model.moveColumn(model.getColumnIndex('pitch'), 6)
    model.moveColumn(model.getColumnIndex('roll movement'), 7)
    model.moveColumn(model.getColumnIndex('pitch movement'), 8)
    model.moveColumn(model.getColumnIndex('roll and pitch movement'), 9)


    model.columnwidths['time'] = 150

    table.redrawTable()

    # Initiate and embed pygame
    os.environ['SDL_WINDOWID'] = str(embedFrame.winfo_id())
    # os.environ['SDL_VIDEODRIVER'] = 'windib'
    screen = pygame.display.set_mode(SCREEN_SIZE, HWSURFACE | OPENGL | DOUBLEBUF)
    resize(*SCREEN_SIZE)
    pygame.init()
    pygame.display.init()

    # Bind keys and buttons events
    root.bind('<ButtonRelease-1>', handle_click)  # click release event
    root.bind_all("<Up>", handle_arrow_keys)  # press Up key event
    root.bind_all("<Down>", handle_arrow_keys)  # press Down key event
    root.bind_all("<Left>", handle_arrow_keys)  # press Left key event
    root.bind_all("<Right>", handle_arrow_keys)  # press Right key event

    # Initiate OpenGL
    init_opengl()

    # Create OpenGL object
    egg = Egg((0.7, 0.0, 0.0), (1, .95, .8))

    # Load first element
    values = get_record(0)
    if values != None:
        time = values[0] + ' ' + values[1]
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

        glPushMatrix()
        # rotate object
        glRotate(float(x_angle), 0, 0, 1)
        glRotate(float(y_angle), 1, 0, 0)
        # render object and text
        egg.render(pygame)
        glPopMatrix()
        drawText(0, 2, time)
        # refresh screen    
        pygame.display.flip()
        root.update()


def closefile():
    global time, x_angle, y_angle, day, month, year, table, root, embedFrame, recordsFrame, play
    # reset app title
    root.title('Smart Egg 3D Visualisation ver.1.1')

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


# Click event callback function.
def handle_click(event):
    global table, time, x_angle, y_angle

    if isinstance(event.widget, (TableCanvas, RowHeader)):
        try:
            index = table.get_row_clicked(event)
            values = get_record(index)
            time = values[0] + ' ' + values[1]
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
        if table.getSelectedRow() < table.model.getRowCount() - 1:
            table.gotonextRow()
        # check if move scroll down is needed
        if (endvisiblerow - table.getSelectedRow()) < 3:
            table.yview_scroll(1, UNITS)
            table.tablerowheader.yview_scroll(1, UNITS)
            table.redrawVisible()

    # display move on the pygame
    index = table.getSelectedRow()
    values = get_record(index)
    time = values[0] + ' ' + values[1]
    x_angle = values[2]
    y_angle = values[3]


def submit(*value):
    print('_____________________________________________________________')

    model = TableModel()
    # load data
    data = load_data(name, value)
    # import data to tablemodel
    model.importDict(data)

    # Create table for records preview
    table = TableCanvas(recordsFrame, name="tablica", model=model, width=420, height=600, cols=0, rows=0, cellwidth=50,
                        editable=False, showkeynamesinheader=True, reverseorder=0)
    table.grid(row=0, sticky=W + N + S)
    table.createTableFrame()
    table.redrawTable()


def settings():
    """Create Settings window"""
    root = tk.Tk()
    root.title('Settings')
    root.geometry("400x100")
    root.resizable(0, 0)  # Don't allow resizing in the x or y direction

    v1 = StringVar(root, "1")
    v2 = StringVar(root, "1")
    v3 = StringVar(root, "1")

    values = {"5": 5, "10": 10, "15": 15, "20": 20, "50": 50}

    roll_entry = Label(root, text="ROLL")
    roll_entry.grid(column=0, row=0)
    col = 0
    for (name, value) in values.items():
        radio = Radiobutton(root, text=name, variable=v1, value=value)
        radio.grid(column=1 + col, row=0, sticky=tk.W)
        col += 1

    pitch_entry = Label(root, text="PITCH")
    pitch_entry.grid(column=0, row=2)
    col = 0
    for (name, value) in values.items():
        radio = Radiobutton(root, text=name, variable=v2, value=value)
        radio.grid(column=1 + col, row=2, sticky=tk.W)
        col += 1

    rollpitch_entry = Label(root, text="ROLL AND PITCH")
    rollpitch_entry.grid(column=0, row=4)
    col = 0
    for (name, value) in values.items():
        radio = Radiobutton(root, text=name, variable=v3, value=value)
        radio.grid(column=1 + col, row=4, sticky=tk.W)
        col += 1

    submit_btn = Button(root, text="Submit", width=5,
                        command=lambda: submit(int(v1.get()), int(v2.get()), int(v3.get())))
    submit_btn.grid(row=2, column=7)

    root.mainloop()


def run():
    global root

    # tk init
    root = tk.Tk()
    root.title('Smart Egg 3D Visualisation')
    root.geometry("1200x650")  # Set the size of the app to be 800x600
    root.resizable(0, 0)  # Don't allow resizing in the x or y direction

    # Initializa Menubar
    menubar = Menu(root)
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="Open file", command=openfile)
    filemenu.add_command(label="Close file", command=closefile)
    filemenu.add_separator()
    filemenu.add_command(label="Connect...", command=connect)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=exitapp)
    menubar.add_cascade(label="File", menu=filemenu)

    settingsmenu = Menu(menubar, tearoff=0)
    settingsmenu.add_command(label="Settings", command=settings)
    menubar.add_cascade(label="Settings", menu=settingsmenu)
    root.config(menu=menubar)

    # Enter mainlopp
    root.mainloop()


if __name__ == "__main__":
    run()
