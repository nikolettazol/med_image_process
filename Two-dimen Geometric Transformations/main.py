import pydicom
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.arrays.numpymodule import ARRAY_TO_GL_TYPE_MAPPING
import math

point = [50, 50]
sx = float(input("Enter sx: "))
#sx = 0.5

def reflection():
    return [
        [1, 0, 0, 0],
        [0, -1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]

    ]

def scale_from_point(point, sx):
    return [
        [sx, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 1],
        [point[0]*(1-sx), point[1], 0, 1]
    ]

def load_texture(pixels, type):
    gl_type = ARRAY_TO_GL_TYPE_MAPPING.get(pixels.dtype)
    glBindTexture(GL_TEXTURE_2D, glGenTextures(1))
    glTexImage2D(GL_TEXTURE_2D, 0, type, width, height, 0, type, gl_type, pixels)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

def load_image(filename):
    global width, height, image, image_type, max_brightness
    image = pydicom.read_file(filename)
    width = image['0028', '0011'].value
    height = image['0028', '0010'].value
    image_type = np.dtype('int' + str(image['0028', '0100'].value))
    max_brightness = np.iinfo(image_type).max

def init():
    global image, normalized_pixels
    normalized_pixels = normalize(np.array(image.pixel_array))
    load_texture(normalized_pixels, GL_LUMINANCE)
    glEnable(GL_TEXTURE_2D)
    glClearColor(0.0, 0.0, 0.0, 0.0)

def display():
    global width, height
    glClear(GL_COLOR_BUFFER_BIT)
    glBegin(GL_QUADS)
    half = width / 2
    glTexCoord3f(0.0, 0.0, 0.0)
    glVertex3f(-half, -half, 0.0)
    glTexCoord3f(0.0, 1.0, 0.0)
    glVertex3f(-half, half, 0.0)
    glTexCoord3f(1.0, 1.0, 0.0)
    glVertex3f(half, half, 0.0)
    glTexCoord3f(1.0, 0.0, 0.0)
    glVertex3f(half, -half, 0.0)
    glEnd()
    glFlush()


def reshape(w, h):
    global default_matrix, width, height
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluOrtho2D(-w / 2, w / 2, -h / 2, h / 2)
    default_matrix = glGetFloatv(GL_MODELVIEW_MATRIX)

def keyboard(key, x, y):
    global image, normalized_pixels, default_matrix
    load_texture(normalized_pixels, GL_LUMINANCE)
    glLoadMatrixf(default_matrix)

    if key == chr(27).encode():
        sys.exit(0)
    elif key ==b'm':
        matrix = np.array(scale_from_point(point, sx) @ np.array(reflection()))
        inverse = np.linalg.inv(matrix)
        matrix1 = matrix @ inverse
        glMultMatrixf(matrix1)
    elif key == b'a':
        matrix = np.array(scale_from_point(point, sx) @ np.array(reflection()))
        glMultMatrixf(matrix)
    elif key == b'r':
        matrix = reflection()
        glMultMatrixf(matrix)
    elif key == b's':
        matrix = scale_from_point(point, sx)
        glMultMatrixf(matrix)
    display()
    glDisable(GL_TEXTURE_2D)
    glPointSize(5)
    glColor4f(100, 1, 1, 1)
    glBegin(GL_POINTS)
    glVertex2i(point[0], point[1])
    glEnd()
    glFlush()
    glEnable(GL_TEXTURE_2D)


def min_max_pixels(pixels):
    pixels_array = []
    for row in pixels:
        for pixel in row:
            pixels_array.append(pixel)
    return {'min': min(pixels_array), 'max': max(pixels_array)}


def normalize(pixels):
    global height, width, max_brightness, image_type
    min_max = min_max_pixels(pixels)
    max = min_max['max']
    min = min_max['min']
    new_min = 0
    new_max = max_brightness
    result = []
    for row in pixels:
        new_row = []
        for pixel in row:
            new_pixel = ((pixel - min) / (max - min)) * (new_max - new_min)
            if new_pixel < 0:
                new_pixel = 0
            if new_pixel > new_max:
                new_pixel = new_max
            new_row.append(new_pixel)
        result.append(new_row)
    return np.array(result, image_type)

def main(filename):
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    load_image(filename)
    glutInitWindowSize(width * 2, height * 2)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b'Laba6')
    init()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutMainLoop()

main('DICOM_Image_16b.dcm')
