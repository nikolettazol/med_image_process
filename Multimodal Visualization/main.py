import pydicom
from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *


class ImageService:
    def __init__(self, image1, image2):
        self.image1 = image1

        self.image2 = image2
        self.pixels = []

    def draw(self):
        return self.pixels

    def set_image1(self):
        self.pixels = self.image1.get_colored_image()

    def set_image2(self):
        self.pixels = self.image2.get_colored_image()

    def set_multi_image(self):
        pixels = []

        for i, row in enumerate(self.image1.get_pixels()):
            new_row = []
            for j, value in enumerate(row):
                new_row.append([self.image1.get_pixel(i, j), 0, self.image2.get_pixel(i, j)])
            pixels.append(new_row)
        self.pixels = pixels

    def set_half_multi_image(self):
        pixels = []

        half = self.image1.get_width() / 2
        for i, row in enumerate(self.image1.get_pixels()):
            new_row = []
            for j, value in enumerate(row):
                if j < half:
                    new_row.append([self.image1.get_pixel(i, j),
                                   0,  self.image2.get_pixel(i, j)])
                else:
                    pixel = self.image2.get_pixel(i, j)
                    new_row.append([pixel, pixel, pixel])
            pixels.append(new_row)
        self.pixels = pixels


class Image:
    def __init__(self, image):
        self.image = image

    def get_bits_allocated(self):
        return self.image['0028', '0100'].value

    def get_width(self):
        return self.image['0028', '0011'].value

    def get_height(self):
        return self.image['0028', '0010'].value

    def get_pixels(self):
        return self.image.pixel_array

    def get_pixel(self, x, y):
        return self.image.pixel_array[x][y]

    def get_colored_image(self, color=None):
        pixels = []

        for row in self.get_pixels():
            new_row = []
            for value in row:
                if 'r' == color:
                    new_row.append([value, 0, 0])
                elif 'g' == color:
                    new_row.append([0, value, 0])
                elif 'b' == color:
                    new_row.append([0, 0, value])
                else:
                    new_row.append([value, value, value])
            pixels.append(new_row)
        return pixels


def load_image():
    global image_service
    image_service = ImageService(Image(pydicom.read_file('2-ct.dcm')),
                                 Image(pydicom.read_file('2-mri.dcm')))
    if image_service.image1.get_bits_allocated() != 8:
        sys.exit()


def init():
    glBindTexture(GL_TEXTURE_2D, glGenTextures(1))
    gl_tex_image_2d()
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glEnable(GL_TEXTURE_2D)
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glMatrixMode(GL_MODELVIEW)


def display():
    glClearColor(0.0, 0.0, 0.0, 0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glBegin(GL_QUADS)
    width = image_service.image2.get_width()
    height = image_service.image2.get_height()
    glTexCoord(1.0, 1.0);
    glVertex(-width / 2, -height / 2)
    glTexCoord(0.0, 1.0);
    glVertex(width / 2, -height / 2)
    glTexCoord(0.0, 0.0);
    glVertex(width / 2, height / 2)
    glTexCoord(1.0, 0.0);
    glVertex(-width / 2, height / 2)
    glEnd()
    glFlush()


def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    # gluOrtho2D(0.0, w, 0.0, h)
    width = image_service.image2.get_width()
    height = image_service.image2.get_height()
    gluOrtho2D(-width / 2, width / 2, -height / 2, height / 2)


def gl_tex_image_2d():
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image_service.image1.get_width(), image_service.image1.get_height(), 0, GL_RGB, GL_UNSIGNED_BYTE, image_service.draw())


def keyboard(key, x, y):
    if key == chr(27).encode():
        sys.exit(0)
    if key == b'1':
        image_service.set_image1()
    if key == b'2':
        image_service.set_image2()
    if key == b'3':
        image_service.set_multi_image()
    if key == b'4':
        image_service.set_half_multi_image()
    gl_tex_image_2d()
    display()


glutInit(sys.argv)
glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
load_image()
glutInitWindowSize(image_service.image2.get_width(),
                   image_service.image2.get_height())
glutInitWindowPosition(200, 200)
glutCreateWindow('Lab 8')
init()
glutDisplayFunc(display)
glutReshapeFunc(reshape)
glutKeyboardFunc(keyboard)
glutMainLoop()
