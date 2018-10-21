# -*- coding: utf-8 -*-
import math
import turtle

def drawCircleTurtle(x, y, r):
    turtle.up()
    turtle.setpos(x+r, y)
    turtle.down()

    for i in range(0, 365, 5):
        a = math.radians(i)
        turtle.setpos(x+r*math.cos(a), y+r*math.sin(a))

class Spiro:
    def __init__(self, xc, yc, col, R, r, l):
        self.t = turtle.Turtle()
        self.t.shape('turtle')
        self.step = 5
        self.drawingComplete = False

        self.setparams(xc, yc, col, R, r, l)
        self.restart()

    def setparams(self, xc, yc, col, R, r, l):
        self.xc = xc
        self.yc = yc
        self.col = col
        self.R = int(R)
        self.r = int(r)
        self.l = l
        self.col = col
        gcdVal = gcd(self.r, self.R)
        self.nRot = self.r // gcdVal
        self.k = r/float(R)
        self.t.color(*col)
        self.a = 0

    def restart(self):
        self.drawingComplete = False
        self.t.showturtle()
        self.t.up()
        R, k, l = self.R, self.k, self.l
        a = 0.0

        x = R*((l-k)*math.cos(a) + l*k*math.cos((l-k)*a/k))
        y = R*((l-k)*math.sin(a) - l*k*math.sin((l-k)*a/k))
        self.t.setpos(self.xc + x, setpos.yc + y)
        self.t.down()

