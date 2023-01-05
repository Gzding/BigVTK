import vtk
from vtk.vtkRenderingCore import vtkRenderWindow,vtkActor,vtkRenderer,vtkPolyDataMapper,vtkProperty,vtkCamera,vtkRenderWindowInteractor
from vtk.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
from vtk.vtkIOImage import vtkDICOMImageReader,vtkJPEGReader
from vtk.vtkCommonDataModel import vtkPolyData,vtkPointData
from vtk.vtkFiltersCore import vtkTriangleFilter
from vmtk.vmtkcenterlines import vmtkCenterlines
from vmtk.vtkvmtk import vtkvmtkCapPolyData,vtkvmtkPolyDataCenterlines

def ExtractCenterline(inputSurface):
    #清理并三角化处理
    cappedSurface = vtkPolyData()
    surfaceCleaner = vtk.vtkCleanPolyData()
    surfaceCleaner.SetInputConnection(inputSurface)
    surfaceCleaner.Update()

    surfaceTriangulator = vtkTriangleFilter()
    surfaceTriangulator.SetInputConnection(surfaceCleaner.GetOutputPort())
    surfaceTriangulator.PassLinesOff()
    surfaceTriangulator.PassVertsOff()
    surfaceTriangulator.Update()

    cappedSurface.DeepCopy(surfaceTriangulator.GetOutputPort())

    #填补管腔
    capper = vtkvmtkCapPolyData()
    capper.SetInputConnection(cappedSurface.GetOutputPort())
    capper.Update()
    CapCenterIds = vtk.vtkIdList()
    cappedSurface.DeepCopy(capper.GetOutputPort())
    CapCenterIds.DeepCopy(capper.GetCapCenterIds())

    print("The number of the lumen is:"+capper.GetCapCenterIds().GetNumberOfIds())

    #设置起始位点
    sourceIds = vtk.vtkIdList()
    sourceIds.SetNumberOfIds()
    sourceIds.SetId(0, CapCenterIds.GetId(0))
    targetIds = vtk.vtkIdList()
    #多个目标
    targetIds.SetNumberOfIds(CapCenterIds.GetNumberOfIds() - 1)
    for i in range(1,CapCenterIds.GetNumberOfIds() - 1):
        targetIds.SetId(i - 1, CapCenterIds.GetId(i))
    #单个目标
    targetIds.SetNumberOfIds(1)
    targetIds.SetId(0, CapCenterIds.GetId(2))

    #计算中心线
    centerlinesFilter = vtkvmtkPolyDataCenterlines()
    centerlinesFilter.SetInputData(cappedSurface)
    centerlinesFilter.SetSourceSeedIds(sourceIds)
    centerlinesFilter.SetTargetSeedIds(targetIds)
    centerlinesFilter.SetAppendEndPointsToCenterlines(True)
    centerlinesFilter.SetCenterlineResampling(True)
    centerlinesFilter.SetResamplingStepLength(1)
    centerlinesFilter.SetRadiusArrayName("Radius")
    centerlinesFilter.SetEdgeArrayName("Edge")
    centerlinesFilter.SetEdgePCoordArrayName("PCoord")
    centerlinesFilter.Update()

    #获取结果
    output = vtkPolyData()
    #可能有点问题
    centerlinesRadiusArray = vtk.vtkDoubleArray()
    centerlinesRadiusArray = output.GetPointData().GetArray("Radius")

    #半径
    for i in range(0,output.GetNumberOfPoints() - 1):
        radius = centerlinesRadiusArray.GetValue(i)

    return output

if __name__ == '__main__':
    stlpath = "./segment/segment.stl"
    reader = vtk.vtkSTLReader()
    reader.SetFileName(stlpath)
    reader.Update()

    #STL文件读取
    data = vtkPolyData()
    data.DeepCopy(reader.GetOutput())

    mapper = vtkPolyDataMapper()
    mapper.SetInputConnection(reader.GetOutputPort())
    mapper.Update()

    actor = vtkActor()
    actor.SetMapper(mapper)

    property = vtkProperty()
    property.SetDiffuseColor(1, 0.49, 0.25);
    property.SetDiffuse(0.7);
    property.SetSpecular(0.3);
    property.SetSpecularPower(20);
    property.SetOpacity(0.3);
    actor.SetProperty(property); #设置透明度

    '''获取中心线
    B样条曲线拟合 '''
    pathpoints = vtk.vtkPoints()
    pathpoints.DeepCopy(ExtractCenterline(data).GetPoints())
    print("The number of points:"+pathpoints.GetNumberOfPoints())

    spline = vtk.vtkParametricSpline()
    spline.SetPoints(pathpoints)
    spline.ClosedOff()

    splineSource = vtk.vtkParametricFunctionSource()
    splineSource.SetParametricFunction(spline)

    pointMapper = vtkPolyDataMapper()
    pointMapper.SetInputConnection(splineSource.GetOutputPort())

    actorPoints = vtk.vtkLODActor()
    actorPoints.SetMapper(pointMapper)
    actorPoints.GetProperty().SetColor(0, 1, 0)
    actorPoints.GetProperty().SetLineWidth(2)

    #交互
    renderer = vtkRenderer()
    renderer.AddActor(actor)
    renderer.AddActor(actorPoints)
    renderer.SetBackground(0.1, 0.2, 0.4)

    renderWindow = vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    renderWindow.SetSize(1920, 1080)

    aCamera = vtkCamera()
    aCamera.SetPosition(0, 0, -300)
    aCamera.SetFocalPoint(0, 0, 0)
    aCamera.SetViewUp(0, -1, 0)

    interactor = vtkRenderWindowInteractor()
    interactor.SetRenderWindow(renderWindow)

    style = vtkInteractorStyleTrackballCamera()
    interactor.SetInteractorStyle(style)
    renderWindow.Render()
    interactor.Start()



