import pydicom
from math import sqrt
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.arrays.numpymodule import ARRAY_TO_GL_TYPE_MAPPING
import scipy.signal as conv

global current_pixels, max_brightness, image_type
MIN = 0.0
MAX = 0.3
filename = "DICOM_Image_16b.dcm"
image = pydicom.read_file(filename)
width = image['0028', '0011'].value
height = image['0028', '0010'].value
min_brightness = 0
np_pixels = np.array(image.pixel_array)
mask_x = np.array([[-1, -1, -1],
                   [-1, 9, -1],
                   [-1, -1, -1]])

mask_y = np.array([[-0, -1, -0],
                   [-1, 5, -1],
                   [0, -1, 0]])
mask_size = 3
mask_centr_x = 1
mask_centr_y = 1


def get_index(x, y):
    x_new = x + mask_centr_x
    y_new = y + mask_centr_y
    return x_new, y_new


def mask_convolution(mask, local_arr):
    conv = 0
    print(local_arr)
    for i in range(-1, 2, 1):
        for j in range(-1, 2, 1):
            x, y = get_index(i, j)
            w = mask[x][y]
            I = local_arr[1 - i][1 - j]
            conv += w * I
    return conv


def get_array_for_convolution(pixels):
    result_array = []
    for i in range(0, width + 2):
        row = []
        for j in range(0, height + 2):
            el = 0
            if i == 0:
                if j == 0:
                    el = pixels[i][j]
                elif j == height + 1:
                    el = pixels[i][j - 2]
                else:
                    el = pixels[i][j - 1]
            elif i == width + 1:
                if j == 0:
                    el = pixels[i - 2][j]
                elif j == height + 1:
                    el = pixels[i - 2][j - 2]
                else:
                    el = pixels[i - 2][j - 1]
            else:
                if j == 0:
                    el = pixels[i - 1][j]
                elif j == height + 1:
                    el = pixels[i - 1][j - 2]
                else:
                    el = pixels[i - 1][j - 1]
            row.append(el)
        result_array.append(row)
    return result_array


def convolve2d(pixels, mask):
    # width = len(pixels)
    # height = len(pixels[0])
    conv_arr = get_array_for_convolution(pixels)
    # print(pixels)
    # print(conv_arr)
    result_array = []
    for i in range(0, width):
        row = []
        for j in range(0, height):

            local_arr = []
            for k in range(0, mask_size):
                loc_row = []
                for l in range(0, mask_size):
                    loc_row.append(conv_arr[i + k][j + l])
                local_arr.append(loc_row)
            print(local_arr)

            row.append(mask_convolution(mask, local_arr))
        result_array.append(row)
    print(result_array)
    return result_array


def convolution(pixels):
    # res_x = conv.convolve2d(pixels, mask_x)
    # res_y = conv.convolve2d(pixels, mask_y)

    res_x = convolve2d(pixels, mask_x)
    res_y = convolve2d(pixels, mask_y)
    result = []
    for i in range(0, height):
        new_row = []
        for j in range(0, width):
            new_row.append(sqrt(res_x[i][j] * res_x[i][j] + res_y[i][j] * res_y[i][j]))
        result.append(new_row)
    print(pixels)
    return np.array(result, image_type)


def load_texture(pixels, type):
    gl_type = ARRAY_TO_GL_TYPE_MAPPING.get(pixels.dtype)
    glBindTexture(GL_TEXTURE_2D, glGenTextures(1))
    glTexImage2D(GL_TEXTURE_2D, 0, type, width, height, 0, type, gl_type,
                 pixels)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)


def load_image():
    global current_pixels, max_brightness, image_type
    current_pixels = image.pixel_array
    image_type = np.dtype('int' + str(image['0028', '0100'].value))
    max_brightness = np.iinfo(image_type).max


def init():
    load_texture(image.pixel_array, GL_LUMINANCE)
    glEnable(GL_TEXTURE_2D)
    glClearColor(0.0, 0.0, 0.0, 0.0)


def display():
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
    global current_pixels
    if key == chr(27).encode():
        sys.exit(0)
    elif key == b'f':
        current_pixels = normalize(convolution(np_pixels))
    elif key == b'r':
        current_pixels = image.pixel_array
    load_texture(current_pixels, GL_LUMINANCE)
    display()


def draw_text(text, x, y):
    glDisable(GL_TEXTURE_2D)
    glColor3f(255, 255, 255)
    glRasterPos2f(x, y)
    for character in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(character))
    glEnable(GL_TEXTURE_2D)


def motion(x, y):
    global current_pixels
    width = glutGet(GLUT_WINDOW_WIDTH)
    height = glutGet(GLUT_WINDOW_HEIGHT)
    if 0 < x < width and 0 < y < height:
        text = "brightness: " + str(current_pixels[x][y])
        display()
        draw_text(text, 5, height - 15)
    else:
        display()
    glFlush()


def min_max_pixels(pixels):
    pixels_array = []
    for row in pixels:
        for pixel in row:
            pixels_array.append(pixel)
    return {'min': min(pixels_array), 'max': max(pixels_array)}


def normalize(pixels):
    amax = np.amax(pixels)
    max_peak = int(float(amax) * MAX)
    min_peak = int(float(amax) * MIN)
    new_min = 0
    new_max = max_brightness
    result = []
    for row in pixels:
        new_row = []
        for pixel in row:
            new_pixel = ((pixel - min_peak) / (max_peak - min_peak)) * (new_max
                                                                        - new_min)
            if new_pixel < 0:
                new_pixel = 0
            if new_pixel > new_max:
                new_pixel = new_max
            new_row.append(new_pixel)
        result.append(new_row)
    return np.array(result, image_type)

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    load_image()
    glutInitWindowSize(width, height)
    glutInitWindowPosition(100, 100)
    glutCreateWindow('Lab3')
    init()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutPassiveMotionFunc(motion)
    glutMainLoop()


main()
