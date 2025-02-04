from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
import pydicom
import math

class TreeD:
    def init(self):
        glClearColor(0, 0, 0, 0.0)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-1.0, 1.0, -1.0, 1.0, -1.0, 1.0)
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_MODELVIEW)
        glRotatef(-60, 1, 0, 0)
        glRotatef(45, 0, 0, 1)

    def __init__(self):
        self.transvers, self.coronal, self.sagital = 0, 0, 0
        self.angle = 0
        self.flag = False
        self.n = 20
        self.width, self.height = 256, 256
        self.image_pixels = np.zeros((self.n, self.height, self.width))
        self.front_pixels = np.zeros((self.height, self.n + 12, self.width))
        self.sag_pixels = np.zeros((self.width, self.n + 12, self.height))

        for i in range(self.n):
            path = "DICOM_set_16bits/brain_0"
            if i < 9:
                path += "0"
            file = path+str(i+1)+".dcm"
            self.image = pydicom.read_file(file)
            self.image_pixels[i] = self.normalize(self.image.pixel_array)

        for i in range(self.height):
            for j in range(self.n):
                for k in range(self.width):
                    self.front_pixels[i][j][k] = self.image_pixels[j][i][k]
                    self.sag_pixels[k][j][i] = self.image_pixels[j][i][k]

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.drawXYZ()
        self.drawTexture(self.transvers, self.coronal, self.sagital)
        if self.flag:
            self.printText(-1.3, 0, 0.1, GLUT_BITMAP_HELVETICA_18, "x")
        else:
            self.printText(1.2, 0.1, 0, GLUT_BITMAP_HELVETICA_18, "x")
        self.printText(0.1, 1.2, 0, GLUT_BITMAP_HELVETICA_18, "y")
        self.printText(0.1, 0, 0.95, GLUT_BITMAP_HELVETICA_18, "z")
        glutSwapBuffers()


    def matrix(self):
        R = np.array([
            self.tr_data["xcoef"], 0, 0, 0,
            0, self.tr_data["ycoef"], 0, 0,
            0, 0, self.tr_data["zcoef"], 0,
            0, 0, 0, 1,
        ])
        self.flag = True
        return R

    def rev_matrix(self):
        self.flag = False
        R = np.array([
            self.tr_data["xcoef"], 0, 0, 0,
            0, self.tr_data["ycoef"], 0, 0,
            0, 0, self.tr_data["zcoef"], 0,
            0, 0, 0, 1,
        ])
        return R


    def normalize(self, pixels):
        min = np.min(pixels)
        max = np.max(pixels)
        dmin = 0
        dmax = 255
        norm = (pixels - min) / (max - min) * (dmax - dmin) + dmin
        return norm.astype(int)

    def printText(self, transvers, coronal, sagital, font, text):
        glColor3f(1, 1, 1)
        glRasterPos3f(transvers, coronal, sagital)
        for c in text:
            glutBitmapCharacter(font, ctypes.c_int(ord(c)))

    def drawXYZ(self):
        glColor3f(1, 1, 1)
        glBegin(GL_LINES)
        glVertex3f(-2.0, 0.0, 0.0)
        glVertex3f(2.0, 0.0, 0.0)
        glVertex3f(0.0, -2.0, 0.0)
        glVertex3f(0.0, 2.0, 0.0)
        glVertex3f(0.0, 0.0, -2.0)
        glVertex3f(0.0, 0.0, 2.0)
        glEnd()


    def drawTexture(self, transvers, coronal, sagital):

        glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, self.height, self.width, 0, GL_LUMINANCE, GL_UNSIGNED_BYTE, self.image_pixels[transvers])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)

        glEnable(GL_TEXTURE_2D)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0)
        glVertex3f(0, 0, transvers*2/self.height)
        glTexCoord2f(1, 0)
        glVertex3f(1, 0, transvers*2/self.height)
        glTexCoord2f(1, 1)
        glVertex3f(1, 1, transvers*2/self.height)
        glTexCoord2f(0, 1)
        glVertex3f(0, 1, transvers*2/self.height)
        glEnd()

        glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, self.height, 32, 0, GL_LUMINANCE, GL_UNSIGNED_BYTE, self.sag_pixels[coronal])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)

        glBegin(GL_QUADS)
        glTexCoord2f(0, 0)
        glVertex3f(coronal / self.height, 0, 0)
        glTexCoord2f(1, 0)
        glVertex3f(coronal / self.height, 1, 0)
        glTexCoord2f(1, self.n/32)
        glVertex3f(coronal / self.height, 1, self.n * 3 / self.height)
        glTexCoord2f(0, self.n/32)
        glVertex3f(coronal / self.height, 0, self.n * 3 / self.height)
        glEnd()

        glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, self.width, 32, 0, GL_LUMINANCE, GL_UNSIGNED_BYTE, self.front_pixels[sagital])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)

        glBegin(GL_QUADS)
        glTexCoord2f(0, 0)
        glVertex3f(0, sagital / self.height, 0)
        glTexCoord2f(1, 0)
        glVertex3f(1, sagital / self.height, 0)
        glTexCoord2f(1, self.n/32)
        glVertex3f(1, sagital / self.height, self.n * 3 / self.height)
        glTexCoord2f(0, self.n/32)
        glVertex3f(0, sagital / self.height, self.n * 3 / self.height)
        glEnd()

        glDisable(GL_TEXTURE_2D)
        glFlush()


    def keyPressed(self, bkey, x, y):
        key = unicode(bkey, errors='ignore')
        if key == "t":
            M = self.matrix()
            glMultMatrixf(M)
        elif key == "r":
            M = self.rev_matrix()
            glMultMatrixf(M)
        elif key == "w" and self.transvers < self.n - 1:
            self.transvers += 1
        elif key == "s" and self.transvers > 0:
            self.transvers -= 1
        elif key == "d" and self.coronal < self.width - 1:
            self.coronal += 1
        elif key == "a" and self.coronal > 0:
            self.coronal -= 1
        elif key == "z" and self.sagital < self.height - 1:
            self.sagital += 1
        elif key == "c" and self.sagital > 0:
            self.sagital -= 1
        self.display()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    image = TreeD()
    glutInitWindowSize(2 * image.width, 2 * image.width)
    glutInitWindowPosition((glutGet(GLUT_SCREEN_WIDTH) - image.width) // 2,
                           (glutGet(GLUT_SCREEN_HEIGHT) - image.width) // 2)
    glutCreateWindow(b'Laba7')
    image.init()
    glutDisplayFunc(image.display)
    glutKeyboardFunc(image.keyPressed)
    glutMainLoop()

main()
