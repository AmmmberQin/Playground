
import os
import math
import sys
import numpy

import OpenGL
from OpenGL.GL import *

import glfw
import glutils

#顶点着色器
strVS = '''
#version 330 core

layout(location = 0) in vec3 aVert;

uniform mat4 uMVMatrix;
uniform mat4 uPMatrix;
uniform float uTheta;
//二维矢量
out vec2 vTexCoord;

void main(){
    //设置旋转矩阵，围绕z轴旋转给定的角度
    mat4 rot = mat4(
        vec4(cos(uTheta), sin(uTheta), 0.0, 0.0),
        vec4(-sin(uTheta), cos(uTheta), 0.0, 0.0),
        vec4(0.0, 0.0, 1.0, 0.0),
        vec4(0.0, 0.0, 0.0, 1.0)
    );
    //利用投影、模型视图和旋转矩阵级联来计算gl_Position
    gl_Position = uPMatrix * uMVMatrix * rot * vec4(aVert, 1.0);
    //设置二维向量作为纹理坐标
    vTexCoord = aVert.xy + vec2(0.5, 0.5);
}
'''

#片段着色器
strFS = '''
#version 330 core

//片段着色器的输入，设置为顶点着色器的输出变量的那些颜色和纹理坐标变量
in vec2 vTexCoord;

//用于连接到一个特定的纹理单元，用于查找纹理值
uniform sampler2D tex2D;
//从python代码中设置的
uniform bool showCircle;

//片段着色器的输出
out vec4 fragColor;

void main(){
    if (showCircle){

        if (distance(vTexCoord, vec2(0.5, 0.5)) > 0.5)
        {
            //如果距离大于阈值，丢弃当前像素
            discard;
        }
        else
        {
            //绘制纹理
            fragColor = texture(tex2D, vTexCoord);
        }
    }
    else
    {
        //查找纹理颜色值，利用了纹理坐标和采样
        fragColor = texture(tex2D, vTexCoord);
    }
}
'''

class Scene:
    def __init__(self):
        #从字符串调用着色器，编译并链接成一个OpenGL程序对象
        self.program = glutils.loadShaders(strVS, strFS)
        #设置代码使用特定的“程序对象”（一个项目可能有多个程序）
        glUseProgram(self.program)

        #从着色器中取到pMatrixUniform，mvMatrixUniform，tex2D参数的值
        self.pMatrixUniform = glGetUniformLocation(self.program, b"uPMatrix")
        self.mvMatrixUniform = glGetUniformLocation(self.program, b"uMVMatrix")
        self.tex2D = glGetUniformLocation(self.program, b"tex2D")

        #定义三角形带的顶点数组，用于绘制正方形
        vertexData = numpy.array(
            [-0.5, -0.5, 0.0,
            0.5, -0.5, 0.0,
            -0.5, 0.5, 0.0,
            0.5, 0.5, 0.0], numpy.float32)

        #创建一个VAO，并绑定到该VAO，接下来的所有调用将绑定到它
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        #创建一个VBO用来管理顶点数据和渲染
        self.vertexBuffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vertexBuffer)
        #根据已定义的顶点，设置缓冲区数据
        glBufferData(GL_ARRAY_BUFFER, 4*len(vertexData), vertexData, GL_STATIC_DRAW)
        #着色区可以访问这些数据
        glEnableVertexAttribArray(0)
        #设置顶点属性数组的位置和数据格式，属性的下标是0，组件个数是3，顶点的数据类型是GL_FLOAT
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        #取消VAO绑定
        glBindVertexArray(0)

        self.t = 0
        #将图像加载为OpenGL的纹理，返回的纹理ID用于渲染
        self.texId = glutils.loadTexture('test.png')

        self.showCircle = False

    def step(self):
        #更新Scene对象中的变量，让正方形在屏幕上旋转
        self.t = (self.t + 1) % 360
        #在着色器中设置uTheta
        glUniform1f(glGetUniformLocation(self.program, 'uTheta'), math.radians(self.t))

    def render(self, pMatrix, mvMatirx):
        #设置渲染使用着色器程序
        glUseProgram(self.program)
        #在着色器中设置计算好的投影和模型视图矩阵
        glUniformMatrix4fv(self.pMatrixUniform, 1, GL_FALSE, pMatrix)
        glUniformMatrix4fv(self.mvMatrixUniform, 1, GL_FALSE, mvMatirx)
        #设置片段着色器中showCircle值
        glUniform1i(glGetUniformLocation(self.program, b"showCircle"), self.showCircle)
        #激活纹理单元0
        glActiveTexture(GL_TEXTURE0)
        #绑定前面生成的纹理ID，激活，准备渲染
        glBindTexture(GL_TEXTURE_2D, self.texId)
        #纹理单元设置为0
        glUniform1i(self.tex2D, 0)
        #绑定到先前创建的VAO
        glBindVertexArray(self.vao)
        #渲染绑定的顶点缓冲区，图元是一个三角形带，有4个顶点要渲染
        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)
        #取消绑定VAO
        glBindVertexArray(0)

class RenderWindow:
    def __init__(self):
        cwd = os.getcwd()
        glfw.glfwInit()
        os.chdir(cwd)

        #将OpenGL版本设置为OpenGL 3.3的核心模式
        glfw.glfwWindowHint(glfw.GLFW_CONTEXT_VERSION_MAJOR, 3)
        glfw.glfwWindowHint(glfw.GLFW_CONTEXT_VERSION_MINOR, 3)
        glfw.glfwWindowHint(glfw.GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE)
        glfw.glfwWindowHint(glfw.GLFW_OPENGL_PROFILE, glfw.GLFW_OPENGL_CORE_PROFILE)

        self.width, self.height = 640, 480
        self.aspect = self.width/self.height
        #创建尺寸为640x480,支持OpenGL的窗口
        self.win = glfw.glfwCreateWindow(self.width, self.height,b"simpleglfw")

        #该窗口设为当前OpenGL的上下文
        glfw.glfwMakeContextCurrent(self.win)

        glViewport(0, 0, self.width, self.height)
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.5, 0.5, 0.5, 1.0)

        glfw.glfwSetMouseButtonCallback(self.win, self.onMouseButton)
        glfw.glfwSetKeyCallback(self.win, self.onKeyboard)
        glfw.glfwSetWindowSizeCallback(self.win, self.onSize)

        self.scene = Scene()
        self.exitNow = False

    def onKeyboard(self, win, key, scancode, action, mods):
        if action == glfw.GLFW_PRESS:
            if key == glfw.GLFW_KEY_ESCAPE:
                self.exitNow = True
            else:
                self.scene.showCircle = not self.scene.showCircle

    def onMouseButton(self, win, button, action, mods):
        pass

    def onSize(self, win, width, height):
        self.width = width
        self.height = height
        self.aspect = self.width / self.height
        glViewport(0, 0, self.width, self.height)

    def run(self):
        glfw.glfwSetTime(0)
        t = 0.0
        while not glfw.glfwWindowShouldClose(self.win) and not self.exitNow:
            currT = glfw.glfwGetTime()
            #每隔0.1s绘一次图
            if currT - t > 0.1:
                t = currT
                #清除深度和颜色缓冲区
                glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
                #计算投影矩阵，45度视场，近/远裁剪平面的距离为0.1/100.0
                pMatrix = glutils.perspective(45.0, self.aspect, 0.1, 100.0)
                #设置模型视图矩阵，眼睛位置设置在(0,0,-2)，用一个向上的矢量(0,1,0)看向原点(0,0,0)
                mvMatirx = glutils.lookAt([0.0, 0.0, -2.0], [0.0, 0.0, 0.0], [0.0, 1.0, 0.0])
                self.scene.render(pMatrix, mvMatirx)
                self.scene.step()
                #交换前后缓冲区， 显示更新的三维图像（双缓冲，更加流畅的视觉效果）
                glfw.glfwSwapBuffers(self.win)
                #调用检查所有UI事件，将控制返回给while循环
                glfw.glfwPollEvents()
        glfw.glfwTerminate()

def main():
    print("Starting simpleglfw. "
          "Press any key to toggle cut. Press ESC to quit.")
    rw = RenderWindow()
    rw.run()

if __name__ == '__main__':
    main()

