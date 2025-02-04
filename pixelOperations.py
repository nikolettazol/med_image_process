import pydicom
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.arrays.numpymodule import ARRAY_TO_GL_TYPE_MAPPING

filename = 'DICOM_Image_for_Lab_2.dcm'
image = pydicom.read_file(filename)
pixels_ar = image.pixel_array
height = image['0028', '0010'].value
width = image['0028', '0011'].value

def logical_background_transformation():
   pixels = []
   bit_map = get_logical_mask()
   for i, row in enumerate(pixels_ar):
       new_row = []
       for j, pixel in enumerate(row):
           new_row.append(bit_map[i][j] & pixel)
       pixels.append(new_row)
   return np.array(pixels, np.uint8)

def get_logical_mask():
   bit_map = []
   for i, row in enumerate(pixels_ar):
       new_row = []
       for j, pixel in enumerate(row):
           bit_map_value = 0
           if width - j > i:
               bit_map_value = 255
           new_row.append(bit_map_value)
       bit_map.append(new_row)
   return bit_map

def color_modeling():
   pixels = np.array(pixels_ar)
   gradient = {}
   for key in range(255, -1, -1):
        gradient[key] = (255 – key) + 1
   print(gradient)
   output = []
   for pixel_list in pixels:
       output_inner = []
       for pixel in pixel_list:
           output_inner.append(gradient[pixel])
       output.append(output_inner)
   return np.array(output)

def gradient_transform():
   pixels = color_modeling()
   rgb = np.zeros((height, width, 3), 'uint8')
   print(rgb)
   rgb[..., 0] = 0
   rgb[..., 1] = pixels
   rgb[..., 2] = 0
   print(rgb)
   return rgb

def load_texture(pixels, type, height, width):
   gl_type = ARRAY_TO_GL_TYPE_MAPPING.get(pixels.dtype)
   glBindTexture(GL_TEXTURE_2D, glGenTextures(1))
   glTexImage2D(GL_TEXTURE_2D, 0, type, width, height, 0, type, gl_type,
                pixels)
   glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
   glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

def init():
   load_texture(pixels_ar, GL_LUMINANCE, height, width)
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

def define_texture(new_pixels, type):
   glTexImage2D(GL_TEXTURE_2D, 0, type, width, height,
                0, type, GL_UNSIGNED_BYTE, new_pixels)

def keyboard(key, x, y):
   if key == chr(27).encode():
       sys.exit(0)
   elif key == b'b':
       new_pixels = logical_background_transformation()
       define_texture(new_pixels, GL_LUMINANCE)
       display()
   elif key == b'c':
       new_pixels = gradient_transform()
       define_texture(new_pixels, GL_RGB)
       display()
   elif key == b'r':
       new_pixels = pixels_ar
       define_texture(new_pixels, GL_LUMINANCE)

def main():
   if image['0028', '0100'].value != 8:
       sys.exit()
   glutInit(sys.argv)
   glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
   glutInitWindowSize(width, height)
   glutInitWindowPosition(100, 100)
   glutCreateWindow('Lab1')
   init()
   glutDisplayFunc(display)
   glutReshapeFunc(reshape)
   glutKeyboardFunc(keyboard)
   glutMainLoop()

main()
