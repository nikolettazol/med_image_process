from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from math import sqrt
from math import pow
import numpy as np
import pydicom


class Image:
    width =None
    height = None
    image_type = None
    max_brightness = None
    image = None


    def __init__(self, width, height, image_type, max_brightness, image):
        self.width, self.height = width, height
        self.image_type = image_type
        self.image_pixels = self.normalize(np.array(image.pixel_array))
        self.max_brightness = max_brightness
        self.min_brightness = 0
        self.point = None
        self.isOverlay = False
        self.Check = False

    def init(self):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glShadeModel(GL_FLAT)
        glClearColor(0, 0, 0, 0.0)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.width, 0, self.height)

    def display(self):
        result_table = np.copy(self.image_pixels)
        glClear(GL_COLOR_BUFFER_BIT)
        pixels_to_draw = np.copy(self.image_pixels)
        pixels_to_draw_2 = np.copy(self.image_pixels)
        glPushMatrix()
        if self.isOverlay == True:
            for x in range(0, 255):
                for y in range(0, 255):
                    if pixels_to_draw[x][y] > 85:
                        pixels_to_draw[x][y] = 255
                        result_table[x][y] = 1
                    else:
                        pixels_to_draw[x][y] = 0
                        result_table[x][y] = 0
            for x in range(0, 255):
                print(result_table[x])
        self.drawTexture(pixels_to_draw_2)
        self.Check = True
        self.drawTexture(pixels_to_draw)
        self.Check = False
        glPopMatrix()
        glutSwapBuffers()

    def get_strait_coef(self, x1, x2, y1, y2):
        A = y2 + y1
        B = x1 + x2
        C = (x2 * y1) - (x1 * y2)
        return A, B, C

    def historgam(self, pixels):
        hist = np.zeros(self.max_brightness + 1)
        for row in pixels:
            for pixel in row:
                hist[pixel] += 1
        new_hist = np.delete(hist, [0])
        return new_hist

    def transform_in(self, pixels, b0):
        new_pixels = []
        for row in pixels:
            new_row = []
            for pixel in row:
                if pixel < b0:
                    new_pixel = 0
                else:
                    new_pixel = self.max_brightness
                new_row.append(new_pixel)
            new_pixels.append(new_row)
        return new_pixels

    def get_dist(self, x0, x1, A, B, C):
        y1 = (C - (A * x1)) / B
        # print(y1)
        d = sqrt(pow(x1 - x0, 2) + pow(y1, 2))
        return d

    def min_distance(self, distances, max_ind, min_ind):
        min_d = distances[max_ind + 1]
        ind = max_ind + 1
        for i in range(max_ind + 1, min_ind, 1):
            # print(distances[i])
            if distances[i] < min_d:
                ind = i
                min_d = distances[i]
        return ind

    def segmentation(self, pixels):
       resultBuffer = [bufferLength * 4];
    for i in bufferLength:
        currentIndex = i * 4;
        if (markedMap[i] == mapValue):
            resultBuffer[currentIndex] = pixels[i];
            resultBuffer[currentIndex + 1] = 0;
            resultBuffer[currentIndex + 2] = 0;
            resultBuffer[currentIndex + 3] = 0;
        }
        else {
            resultBuffer[currentIndex] = pixels[i];
            resultBuffer[currentIndex + 1] = pixels[i];
            resultBuffer[currentIndex + 2] = pixels[i];
            resultBuffer[currentIndex + 3] = 0;
        }
    }
    return resultBuffer;

    def min_max_pixels(self, pixels):
        pixels_array = []
        for row in pixels:
            for pixel in row:
                pixels_array.append(pixel)
        return {'min': min(pixels_array), 'max': max(pixels_array)}

    def normalize(self, pixels):
        min = np.min(pixels)
        max = np.max(pixels)
        dmin = 0
        dmax = 255
        norm = (pixels - min) / (max - min) * (dmax - dmin) + dmin
        return norm.astype(int)

    def drawTexture(self, data):
        if self.isOverlay == True & self.Check == True:
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height, 0, GL_GREEN, GL_UNSIGNED_BYTE, data)
        else:
            glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, self.width, self.height, 0, GL_LUMINANCE, GL_UNSIGNED_BYTE,
                         data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)

        glEnable(GL_TEXTURE_2D)
        if self.isOverlay == True & self.Check == True:
            glColor4f(1.0, 1.0, 1.0, 0.5)
        else:
            glColor4f(1.0, 1.0, 1.0, 1.0)
        glBegin(GL_QUADS)
        glTexCoord2d(0.0, 0.0)
        glVertex2d(0.0, 0.0)
        glTexCoord2d(1.0, 0.0)
        glVertex2d(self.width, 0.0)
        glTexCoord2d(1.0, 1.0)
        glVertex2d(self.width, self.height)
        glTexCoord2d(0.0, 1.0)
        glVertex2d(0.0, self.height)
        glEnd()
        glDisable(GL_TEXTURE_2D)

    def keyPressed(self, bkey, x, y):
        key = unicode(bkey, errors='ignore')
        if key == "r":
            self.isOverlay = False
        if key == "q":
            self.isOverlay = True
        self.display()

def load_image(filename):
    global width, height, image, image_type, max_brightness
    image = pydicom.read_file(filename)
    width = image['0028', '0011'].value
    height = image['0028', '0010'].value
    image_type = np.dtype('int' + str(image['0028', '0100'].value))
    max_brightness = np.iinfo(image_type).max

def initWindow(width, height):
    glutInitWindowSize(width, height)
    glutInitWindowPosition((glutGet(GLUT_SCREEN_WIDTH) - width) // 2, (glutGet(GLUT_SCREEN_HEIGHT) - height) // 2)
    glutCreateWindow(b’Laba4')

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    filename= "DICOM_Image_16b.dcm"
    load_image(filename)
    im = Image(width, height, image_type, max_brightness, image)
    initWindow(im.width, im.height)
    im.init()
    glutDisplayFunc(im.display)
    glutKeyboardFunc(im.keyPressed)
    glutMainLoop()


main()
