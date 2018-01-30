# # -*- coding: utf-8 -*-
#
# # PyQT5 imports
# #from PyQt5 import QtGui, QtCore, QtOpenGL, QtWidgets
# #from ctypes import *
#
# # PyOpenGL imports
# from OpenGL.GL import *
# from PyQt5 import QtGui
# from PyQt5.QtCore import *
# from PyQt5.QtGui import *
# from PyQt5.QtWidgets import QOpenGLWidget
#
# from utils.config import *
#
#
# class QtTexture():
#     def __init__(self):
#         super(QtTexture, self).__init__()
#
#         self._qt_texture = QOpenGLTexture(QOpenGLTexture.Target2D)
#         # self._gl = OpenGL.getInstance().getBindingsObject()
#         self._file_name = None
#         self._image = None
#
#     def getTextureId(self):
#         return self._qt_texture.textureId()
#
#     def bind(self, unit):
#         if not self._qt_texture.isCreated():
#             if self._file_name is None:
#                 self._image = QImage(self._file_name).mirrored()
#             elif self._image is None:  # No filename or image set.
#                 self._image = QImage(1, 1, QImage.Format_ARGB32)
#             self._qt_texture.setData(self._image)
#             self._qt_texture.setMinMagFilters(QOpenGLTexture.Linear, QOpenGLTexture.Linear)
#
#         self._qt_texture.bind(unit)
#
#     def release(self, unit):
#         self._qt_texture.release(unit)
#
#     def setImage(self, image):
#         self._image = image
#
#     def load(self, file_name):
#         self._file_name = file_name
#
#
# class TongOpenGLWidget(QOpenGLWidget):
#     # OenGL绘图参数
#     m_proj = QMatrix4x4()
#     m_quadSize = QSizeF()
#     # OpenGL绘图程序
#     m_shaderDisplay = QOpenGLShaderProgram()
#     # OpenGL绘图纹理
#     texVideoRGBA = QOpenGLTexture(0)
#
#     #  OpenGL纹理是否就绪
#     myTexture_is_OK = False
#
#     def __init__(self, parent=None):
#         super(TongOpenGLWidget, self).__init__(parent)
#
#
#     def initializeGL(self):
#         ctx = QOpenGLContext.currentContext()  # 查询当前的opengl上下文, 环境
#         if ctx.format().renderableType() == QSurfaceFormat.OpenGLES:
#             gles_gl = " GLES"
#         else:
#             gles_gl = " GL"
#         print("Got a "+str(ctx.format().majorVersion())+"."+str(ctx.format().minorVersion())+gles_gl+" context")
#
#         #视频窗口显示 demo图片
#
#         #file_name = "D:/sip/happy.jpg"
#         file_name = "C:/zt_python/school/face01.jpg"
#         self.render_RGBA(QImage(file_name))
#         self.paintGL_01()
#         pass
#
#     def computeProjection(self, winWidth, winHeight, imgWidth, imgHeight):
#         ratioImg    = float(imgWidth) / float(imgHeight)
#         ratioCanvas = float(winWidth) / float(winHeight)
#
#         correction = ratioImg / ratioCanvas  # 矫正比率 图像宽高比/画板宽高比
#         rescaleFactor = 1.0
#         quadWidth     = 1.0
#         quadHeight    = 1.0
#
#         if correction < 1.0:  # canvas larger than image -- height = 1.0, vertical black bands
#             quadHeight  = 1.0                  # 四边形高
#             quadWidth    = 1.0 * ratioImg        # 四边形宽
#             rescaleFactor = ratioCanvas
#             correction    = 1.0 / rescaleFactor
#         else:                    # image larger than canvas -- width = 1.0, horizontal black bands
#             quadWidth  = 1.0
#             quadHeight = 1.0 / ratioImg
#             correction = 1.0 / ratioCanvas
#
#         frustumWidth  = 1.0 * rescaleFactor               #片元宽
#         frustumHeight = 1.0 * rescaleFactor * correction  #高
#
#         outP = QMatrix4x4()
#         outP.ortho(
#                 -frustumWidth,
#                 frustumWidth,
#                 -frustumHeight,
#                 frustumHeight,
#                 -1.0,
#                 1.0)
#         self.m_proj = outP
#         self.m_quadSize = QSizeF(quadWidth, quadHeight)
#
#     def resizeGL(self, w, h):
#
#         print("resize-1")
#
#         if not self.myTexture_is_OK:
#             return
#         print("resize-2", w, h)
#
#         print("resize-3", w, h)
#         self.computeProjection(w, h, self.texVideoRGBA.width(), self.texVideoRGBA.height())
#         print("resize-4")
#
#     # 外部调用此函数显示 视频图片
#     def set_image_filename(self, filename):
#         img_filename = filename
#
#         if not check_file(img_filename):
#             return False
#
#         img = QImage(img_filename)
#         self.render_RGBA(img)
#         self.paintGL_01()
#         return  True
#
#     # 外部调用此函数显示 视频图片-Qimage
#     def set_image_Qimage(self, img):
#
#         if img is None:
#             return False
#         print("img w = ", img.width(), "  h = ", img.height())
#         self.render_RGBA(img)
#         #self.update()
#         #self.paintGL_01()
#         return True
#
#     def render_RGBA(self, img):
#
#         img001 = img.mirrored()
#         img001.convertToFormat(QImage.Format_RGBA8888)
#         m_VideoW = img001.width()
#         m_VideoH = img001.height()
#
#         print("img001 w = ", img001.width(), "  h = ", img001.height())
#
#         if img001 is None:
#             print("视频文件为空")
#             return False
#         print("a-------------------------------a")
#         if m_VideoW == 0 or m_VideoH == 0:
#             return False
#
#         print("b-------------------------------b")
#
#         # 如果 图片尺寸未改变 且纹理已建立 则直接将纹理图片替换
#         # 否则， 重新建立纹理
#         if self.myTexture_is_OK:
#             if m_VideoW == self.texVideoRGBA.width() and m_VideoH == self.texVideoRGBA.height():
#                 self.texVideoRGBA.setData(QOpenGLTexture.RGBA, QOpenGLTexture.UInt8, img001.bits())
#                 print("++++++++++++++++++++++++++++++++++++++++++++")
#                 print("img w = ", self.texVideoRGBA.width(), "  h = ", self.texVideoRGBA.height())
#                 return
#
#         print("c-------------------------------c")
#         vsDisplaySource = '''
#                     #version 430 core
#                     //矩形的四个顶点
#                     const vec4 vertices[4] = vec4[4] (
#                             vec4( -1.0,  1.0, 0.0, 1.0),
#                             vec4( -1.0, -1.0, 0.0, 1.0),
#                             vec4(  1.0,  1.0, 0.0, 1.0),
#                             vec4(  1.0, -1.0, 0.0, 1.0)
#                     );
#                     //贴图坐标方向
#                     const vec2 texCoords[4] = vec2[4] (
#                             vec2( 0.0,  1.0),
#                             vec2( 0.0,  0.0),
#                             vec2( 1.0,  1.0),
#                             vec2( 1.0,  0.0)
#                     );
#                     out vec2 texCoord;
#                     //声明输入变量matProjection
#                     uniform mat4 matProjection;
#                     //声明输入变量imageRatio
#                    uniform vec2 imageRatio;
#                     void main() {
#                        gl_Position = matProjection * ( vertices[gl_VertexID] * vec4(imageRatio,0,1)  );
#                        texCoord = texCoords[gl_VertexID];
#                     }
#             '''
#         fsDisplaySource = '''
#                     #version 430 core
#                     in lowp vec2 texCoord;
#                     uniform sampler2D samImage;
#                     layout(location = 0) out lowp vec4 color;
#                     void main() {
#                       lowp vec4 texColor = texture(samImage,texCoord);
#                        color = vec4(texColor.rgb, 1.0);
#                     }
#             '''
#
#         img002 = QImage(m_VideoW, m_VideoH, QImage.Format_RGBA8888)
#
#         self.texVideoRGBA = QtGui.QOpenGLTexture(img002)
#
#         print("d-------------------------------d")
#
#         print("tex = ", self.texVideoRGBA.width(), self.texVideoRGBA.height())
#
#         print("e-------------------------------e")
#
#         self.texVideoRGBA.setMagnificationFilter(QOpenGLTexture.Linear)
#         self.texVideoRGBA.setMinificationFilter(QOpenGLTexture.Linear)
#         self.texVideoRGBA.setWrapMode(QOpenGLTexture.ClampToEdge)
#
#         self.texVideoRGBA.release()
#
#         #self.m_shaderDisplay = QOpenGLShaderProgram()
#         if self.m_shaderDisplay:
#             self.m_shaderDisplay = QOpenGLShaderProgram()
#
#         print("8-------------------------------8")
#
#         self.m_shaderDisplay.addShaderFromSourceCode(QOpenGLShader.Vertex, vsDisplaySource)
#         self.m_shaderDisplay.addShaderFromSourceCode(QOpenGLShader.Fragment, fsDisplaySource)
#
#         # self.m_shaderDisplay.addShaderFromSourceCode(QOpenGLShader.Vertex, versionedShaderCode(vsDisplaySource))
#         # self.m_shaderDisplay.addShaderFromSourceCode(QOpenGLShader.Fragment, versionedShaderCode(fsDisplaySource))
#         self.m_shaderDisplay.link()
#         self.m_vao = QOpenGLVertexArrayObject()
#         self.m_vao.create()
#         print("Z_______________________________1")
#         self.texVideoRGBA.setData(QOpenGLTexture.RGBA, QOpenGLTexture.UInt8, img001.bits())
#         print("Z_______________________________2")
#         print(self.width(), self.height(), self.texVideoRGBA.width(), self.texVideoRGBA.height())
#         # 首次生成 调整显示比例
#         self.computeProjection(self.width(), self.height(), self.texVideoRGBA.width(), self.texVideoRGBA.height())
#         print("Z_______________________________3")
#         print(self.myTexture_is_OK)
#         self.myTexture_is_OK = True
#
#         self.update()
#         print("Z_______________________________4")
#         return True
#
#     def paintGL(self):
#
#         if not self.myTexture_is_OK:
#             print("P----------------------")
#             return
#         print("P+++++++++++++++++++++++")
#         self.paintGL_01()
#
#
#     def paintGL_01(self):
#         if not self.myTexture_is_OK:
#             return
#         print("X+++++++++++++++++++++++")
#         glClearColor(0, 0, 0, 1)
#         glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
#         self.texVideoRGBA.bind(0)
#         self.m_shaderDisplay.bind()
#         self.m_shaderDisplay.setUniformValue("matProjection", self.m_proj)
#         self.m_shaderDisplay.setUniformValue("imageRatio", self.m_quadSize)
#
#         self.m_shaderDisplay.setUniformValue("samImage", 0)
#         self.m_vao.bind()
#
#         print("X___________________________1")
#
#         # 绘制三角形
#         # GL_TRIANGLE_STRIP: 以左右编号顺序
#         # 从上到下交叉绘制三角形， 0: 起点在缓冲区中的索引, 4: 共绘制4个定点(2 个三角形())
#         glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)
#
#         print("X___________________________2")
#
#         self.m_vao.release()
#         self.m_shaderDisplay.release()
#         self.texVideoRGBA.release(0)
#         print("WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW")
#         #self.update()