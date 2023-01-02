import os
import sys

# Qt
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame, QLabel, QFileDialog)
from PyQt6.QtGui import (QIcon, QAction, QPixmap, QFont)
from PyQt6.QtCore import (QThread, QObject)

# vtk
# import vtkmodules.vtkInteractionStyle
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleImage,vtkInteractorStyleTrackballCamera
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersSources import (vtkCylinderSource, vtkConeSource)
# render flow
from vtkmodules.vtkRenderingCore import (vtkImageMapper, vtkImageSliceMapper,  vtkImageActor, vtkActor, vtkPolyDataMapper, vtkRenderWindow, vtkRenderWindowInteractor3D, vtkRenderWindowInteractor, vtkRenderer, vtkInteractorStyle, vtkInteractorStyle3D, vtkCamera, vtkColorTransferFunction, vtkVolumeProperty, vtkVolume, vtkPointPicker)
from vtkmodules.vtkRenderingUI import vtkGenericRenderWindowInteractor
# vtk - qt
from vtkmodules.qt.QVTKRenderWindowInteractor import (QVTKRenderWindowInteractor, QVTKRenderWidgetConeExample)
# reader
from vtkmodules.vtkIOImage import vtkDICOMImageReader
# vtk widgets
from vtkmodules.vtkInteractionWidgets import (vtkImagePlaneWidget, vtkOrientationMarkerWidget)
from vtkmodules.vtkRenderingAnnotation import (vtkAxesActor)

from vtkmodules.vtkImagingCore import vtkImageReslice, vtkImageMapToColors
from vtkmodules.vtkCommonDataModel import vtkImageData, vtkPiecewiseFunction
from vtkmodules.vtkCommonMath import vtkMatrix4x4
from vtkmodules.vtkCommonCore import vtkLookupTable

from vtkmodules.vtkFiltersSources import vtkPlaneSource
from vtkmodules.vtkImagingGeneral import vtkImageGaussianSmooth
from vtkmodules.vtkRenderingVolumeOpenGL2 import vtkOpenGLGPUVolumeRayCastMapper
from vtkmodules.vtkCommonMisc import vtkContourValues
from vtkmodules.vtkFiltersCore import vtkMarchingCubes, vtkSmoothPolyDataFilter, vtkStripper


import itk


class MainWindow(QMainWindow):
    """QMainWindow派生的程序窗口类"""


    def __init__(self, windowName, iconPath):
        """构造函数"""

        super().__init__()
        
        self.setWindowTitle(windowName)
        self.setWindowIcon(QIcon(iconPath))
        self.setFixedSize(1600, 840)

        self.initUI()
        self.center()
        self.show() # 显示窗口
        
    def center(self):
        """将程序窗口居中"""

        winRect = self.frameGeometry()
        winCenter = self.screen().availableGeometry().center()
        winRect.moveCenter(winCenter)
        self.move(winRect.topLeft())

    def initUI(self):
        """初始化UI界面"""
        
        self.initStatusBar()
        self.initMenu()

        self.frame = self.initView()
        vBox = QHBoxLayout()
        vBox.addWidget(self.frame)

        self.mainWidget = QWidget()
        self.mainWidget.setLayout(vBox) # 中心窗口设置最终布局
        self.setCentralWidget(self.mainWidget)

    def initView(self):
        """ 初始化视图"""
        frame = QFrame()
        frame.setStyleSheet("QWidget{background-color:#111100;}")
        # frame.setFixedSize(1000, 1000)
        return frame
    
    def initStatusBar(self):
        """初始化状态栏"""
        self.sbar = self.statusBar()

    def initMenu(self):
        """初始化菜单栏"""

        openAction = QAction(QIcon('res/open_mso.png'), '&打开', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('打开文件')
        openAction.triggered.connect(vtkOpen)
        
        quitAction = QAction(QIcon('res/close_mso.png'), '&退出', self)
        quitAction.setShortcut('Ctrl+Q')
        quitAction.setStatusTip('退出程序')
        quitAction.triggered.connect(self.close)
 
        mb = self.menuBar()
        
        fm = mb.addMenu('&文件')

        fm.addAction(openAction)
        fm.addSeparator()
        fm.addAction(quitAction)

        action1 = QAction(QIcon("res/save_mso.png"), "&视图", self)
        # action1.setShortcut(shortcut)
        action1.setStatusTip("显示三视图和三正交视图")
        action1.triggered.connect(VtkThreeView)
        mb.addAction(action1)

        action2 = QAction(QIcon("res/save_mso.png"), "&渲染", self)
        # action1.setShortcut(shortcut)
        action2.setStatusTip("GPU体渲染")
        action2.triggered.connect(VtkGPU)
        mb.addAction(action2)

        action3 = QAction(QIcon("res/save_mso.png"), "&分割", self)
        # action1.setShortcut(shortcut)
        action3.setStatusTip("区域增长分割渲染")
        action3.triggered.connect(VtkSeg)
        mb.addAction(action3)


    def getFrame(self):
        return self.frame



def vtkOpen():
    """"""
    base_dir = "data/"
    folder = QFileDialog.getExistingDirectory(win, "选择数据文件夹", directory=base_dir)
    # data reader
    reader.SetDirectoryName(folder)
    reader.Update()
    global dataReady
    dataReady = True


def VtkThreeView():
    
    if dataReady == False:
        return

    colors = vtkNamedColors()
    
    # 渲染流程
    # renWin = vtkRenderWindow()
    iren = vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    picker = vtkPointPicker()
    iren.SetPicker(picker)
    # style = PointPickerInteractorStyle()
    style = vtkInteractorStyleTrackballCamera()
    # style = vtkInteractorStyleImage()
    iren.SetInteractorStyle(style)

    # vtk渲染结果显示在QT控件上
    box = QVBoxLayout()
    widget = QVTKRenderWindowInteractor(parent=win.getFrame(), rw=renWin, iren=iren)
    box.addWidget(widget)
    win.getFrame().setLayout(box)

    # # 测试itk-vtk image转换功能：正常
    # myitkImage = itk.image_from_vtk_image(reader.GetOutput())
    # image = itk.vtk_image_from_image(myitkImage)


    # 三正交视图
    ren = vtkRenderer()
    ren.SetViewport(*viewports[3])
    renWin.AddRenderer(ren)
    # 1-193
    slices = [190, 205, 90] # x,y,z
    # 三个平面
    planes = [None, None, None]
    for i in range(3):
        planes[i] = vtkImagePlaneWidget()
        planes[i].SetInteractor(iren)    
        planes[i].SetInputConnection(reader.GetOutputPort())
        # planes[i].SetInputData(image)
        planes[i].RestrictPlaneToVolumeOn()
        planes[i].SetResliceInterpolateToNearestNeighbour()
        # 设置三个方向的切片
        if i==0:
            planes[i].SetPlaneOrientationToXAxes()
        elif i==1:
            planes[i].SetPlaneOrientationToYAxes()
        else:
            planes[i].SetPlaneOrientationToZAxes()
        planes[i].SetSliceIndex(slices[i])
        planes[i].SetDefaultRenderer(ren)
        planes[i].DisplayTextOn()
        planes[i].On()

    # 坐标轴
    axesActor = vtkAxesActor()
    marker = vtkOrientationMarkerWidget()
    marker.SetOutlineColor(1.0, 1.0, 1.0)
    marker.SetOrientationMarker(axesActor)
    marker.SetInteractor(iren)
    marker.SetViewport(0.0, 0.0, 0.2, 0.2)
    marker.SetEnabled(1)

    # 设置相机
    ren.GetActiveCamera().Elevation(110)
    ren.GetActiveCamera().SetViewUp(0, 0, -1)
    ren.GetActiveCamera().Azimuth(45)
    ren.GetActiveCamera().Dolly(1.15)
    ren.ResetCameraClippingRange()



    # 三切片单独显示视图
    rotateAngles = [-180, -90, 0]
    for i in range(3):
        # 渲染器
        planeRen = vtkRenderer()
        planeRen.SetViewport(*viewports[i])
        renWin.AddRenderer(planeRen)

        # 切片平面
        planeSource = vtkPlaneSource()
        planeMapper = vtkPolyDataMapper()
        planeMapper.SetInputConnection(planeSource.GetOutputPort())
        planeActor = vtkActor()
        planeActor.SetMapper(planeMapper)
        planeActor.SetTexture(planes[i].GetTexture())
        planeActor.RotateZ(rotateAngles[i])
        planeRen.AddActor(planeActor)

    # 开始渲染
    widget.Render()

    ren.ResetCamera()

    widget.Initialize()
    widget.Start()

    
def VtkGPU():
    """"""

    if dataReady == False:
        return

    # 体渲染

    # 高斯平滑
    gSmooth = vtkImageGaussianSmooth()
    gSmooth.SetInputConnection(reader.GetOutputPort())
    gSmooth.SetDimensionality(3)
    gSmooth.SetRadiusFactor(5)
    gSmooth.SetStandardDeviation(1)
    gSmooth.Update()

    # 体渲染GPU
    castMapper = vtkOpenGLGPUVolumeRayCastMapper()
    castMapper.SetInputConnection(gSmooth.GetOutputPort())
    castMapper.SetBlendModeToIsoSurface()

    # 颜色转换
    colorFun = vtkColorTransferFunction()
    colorFun.RemoveAllPoints()
    colorFun.AddRGBPoint(220, 1.00, 1.00, 1.00)
    colorFun.AddRGBPoint(190, 1.00, 1.00, 1.00)
    colorFun.AddRGBPoint( 64, 1.00, 0.52, 0.30)
    colorFun.AddRGBPoint(  0, 0.00, 0.00, 0.00)

    prop = vtkVolumeProperty()
    prop.ShadeOn()
    prop.SetInterpolationTypeToLinear()
    prop.SetColor(colorFun)
    prop.SetAmbient(0.4)
    prop.SetDiffuse(0.6)
    prop.SetSpecular(0.2)

    compositeOpacity = vtkPiecewiseFunction()
    compositeOpacity.AddPoint(70, 0.00)
    compositeOpacity.AddPoint(90, 0.40)
    compositeOpacity.AddPoint(180, 0.60)

    prop.SetScalarOpacity(compositeOpacity)

    gradientOpacity = vtkPiecewiseFunction()
    gradientOpacity.AddPoint(10, 0.0)
    gradientOpacity.AddPoint(90, 0.5)
    gradientOpacity.AddPoint(100, 1.0)

    prop.SetGradientOpacity(gradientOpacity)

    for i in range(200):
        prop.GetIsoSurfaceValues().SetValue(i, 100+5*i)

    volume = vtkVolume()
    volume.SetMapper(castMapper)
    volume.SetProperty(prop)

    isoRen = vtkRenderer()
    isoRen.SetViewport(*viewports[4])
    # isoRen.SetBackground(1, 1, 1)
    isoRen.AddVolume(volume)
    isoRen.ResetCamera()

    isoCam = isoRen.GetActiveCamera()
    isoCam.SetViewUp(0, 0, -1)
    isoCam.SetPosition(0, 1, 0)
    isoCam.SetFocalPoint(0, 0, 0)
    isoCam.ComputeViewPlaneNormal()
    isoCam.Dolly(2.0)
    
    isoRen.SetActiveCamera(isoCam)
    isoRen.ResetCamera()
    isoRen.ResetCameraClippingRange()

    renWin.AddRenderer(isoRen)

# 分割过程很慢
def VtkSeg():
    """"""
    if dataReady == False:
        return

    myitkImage = itk.image_from_vtk_image(reader.GetOutput())

    # setup the pipeline
    if3 = itk.Image[itk.SS, 3]
    itkfilter = itk.NeighborhoodConnectedImageFilter[if3, if3].New()
    itkfilter.SetInput(myitkImage)
    itkfilter.SetLower(-200)
    itkfilter.SetUpper(200)
    seeds = [(255, 205, 109)]
    pixelidx = itk.Index[3]()
    for (x, y, z) in seeds:
        pixelidx.SetElement(0, x)
        pixelidx.SetElement(1, y)
        pixelidx.SetElement(2, z)
        itkfilter.AddSeed(pixelidx)	
    size = itk.Size[3]()
    size.SetElement(0, 3)
    size.SetElement(1, 3)
    size.SetElement(2, 3)
    itkfilter.SetRadius(size)
    itkfilter.SetReplaceValue(255)

    itkfilter.Update()

    vtkimage = itk.vtk_image_from_image(itkfilter.GetOutput())

    marchingcube = vtkMarchingCubes()
    marchingcube.SetInputData(vtkimage)
    marchingcube.SetValue(0, 140)

    smooth = vtkSmoothPolyDataFilter()
    smooth.AddInputConnection(marchingcube.GetOutputPort())
    smooth.SetRelaxationFactor(0.01)
    smooth.SetNumberOfIterations(10)
    smooth.SetFeatureEdgeSmoothing(False)
    smooth.SetBoundarySmoothing(False)
    smooth.Update()

    stripper = vtkStripper()
    stripper.SetInputConnection(smooth.GetOutputPort())

    mmapper = vtkPolyDataMapper()
    mmapper.SetInputConnection(stripper.GetOutputPort())
    mmapper.ScalarVisibilityOff()

    mactor = vtkActor()
    mactor.SetMapper(mmapper)
    mactor.GetProperty().SetDiffuseColor(1, 0.49, 0.25)
    mactor.GetProperty().SetSpecular(0.3)
    mactor.GetProperty().SetSpecularPower(20)
    mactor.GetProperty().SetOpacity(1.0)
    mactor.GetProperty().SetColor(1, 0, 0)
    mactor.GetProperty().SetRepresentationToWireframe()

    mcamera = vtkCamera()
    mcamera.SetViewUp(0, 0, -1)
    mcamera.SetPosition(0, 1, 0)
    mcamera.SetFocalPoint(0, 0, 0)
    mcamera.ComputeViewPlaneNormal()
    mcamera.Dolly(2.0)

    mrenderer = vtkRenderer()
    mrenderer.AddActor(mactor)
    mrenderer.SetActiveCamera(mcamera)
    # mrenderer.SetBackground(1, 1, 1)
    mrenderer.SetViewport(*viewports[4])
    mrenderer.ResetCamera()

    renWin.AddRenderer(mrenderer)

# folder = "data/result/"
reader = vtkDICOMImageReader()
dataReady = False
renWin = vtkRenderWindow()
viewports = [[0.0, 0.0, 0.25, 0.5], [0.25, 0.5, 0.5, 1.0], [0.0, 0.5, 0.25, 1.0], [0.25, 0.0, 0.5, 0.5], [0.5, 0.0, 1.0, 1.0]]

app = QApplication(sys.argv)
win = MainWindow(windowName="VTK-Final", iconPath="./image/icon.png")
sys.exit(app.exec())