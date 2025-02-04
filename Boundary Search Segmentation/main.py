import pydicom
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.arrays.numpymodule import ARRAY_TO_GL_TYPE_MAPPING
import numpy as np
import cannyEdgeDetector

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

    glTexCoord2f(0.0, 0.0)
    glVertex2f(0.0, 0.0)
    glTexCoord2f(0.0, 1.0)
    glVertex2f(0.0, width)
    glTexCoord2f(1.0, 1.0)
    glVertex2f(height, width)
    glTexCoord2f(1.0, 0.0)
    glVertex2f(height, 0.0)

    glEnd()
    glFlush()


def reshape(w, h):
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluOrtho2D(0.0, w, 0.0, h)


def keyboard(key, x, y):
    global image, normalized_pixels

    if key == chr(27).encode():
        sys.exit(0)
    elif key == b'r':
        glEnable(GL_TEXTURE_2D)
        load_texture(normalized_pixels, GL_LUMINANCE)
        display()
    elif key == b't':
        contour = bvf(np.array(normalized_pixels))
        glEnable(GL_TEXTURE_2D)
        load_texture(normalized_pixels, GL_LUMINANCE)
        display()

        glDisable(GL_TEXTURE_2D)
        glPointSize(5)
        glColor3f(0, 0, 255)
        glBegin(GL_POINTS)

        n_points = len(contour)
        for i in range(0, n_points - 1):
            point = tuple(contour[i])
            glVertex2i(point[0], point[1])

        glEnd()

        glLineWidth(1)
        glColor3f(0, 0, 255)
        glLineWidth(2)
        glBegin(GL_LINES)
        for i in range(0, n_points):
            point1 = tuple(contour[i])
            next_index = i  if i < n_points  else 0
            point2 = tuple(contour[next_index])
            glVertex2i(point1[0], point1[1])
            glVertex2i(point2[0], point2[1])

        glEnd()

        glFlush()


def min_max_pixels(pixels):
    pixels_array = []
    for row in pixels:
        for pixel in row:
            pixels_array.append(pixel)
    return {'min': min(pixels_array), 'max': max(pixels_array)}


def normalize(pixels):
    global height, width, max_brightness, image_type
    MIN = 0.3
    MAX = 0.85
    amax = np.amax(pixels)
    max_peak = int(float(amax) * MAX)
    min_peak = int(float(amax) * MIN)
    new_min = 0
    new_max = max_brightness
    result = []
    for row in pixels:
        new_row = []
        for pixel in row:
            new_pixel = ((pixel - min_peak) / (max_peak - min_peak)) * (new_max - new_min)
            if new_pixel < 0:
                new_pixel = 0
            if new_pixel > new_max:
                new_pixel = new_max
            new_row.append(new_pixel)
        result.append(new_row)
    return np.array(result, image_type)


def bvf(pixels):
    global width, height, image_type

    ced = Canny.cannyEdgeDetector (pixels, width, height, image_type, closed=True)
    loop = 0
    while ced.step() and loop < 176:
        loop = loop + 1

    return ced.contour()


def main(filename):
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    load_image(filename)
    glutInitWindowSize(width, height)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b'Laba5')
    init()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutMainLoop()


main('DICOM_Image_16b.dcm')
