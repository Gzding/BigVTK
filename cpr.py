import vtk


def SweepLine(line, direction, distance, cols):
    rows = line.GetNumberOfPoints()
    # 点的space大小
    spacing = distance / cols
    surface = vtk.vtkPolyData()
    # Generate the points
    cols += 1
    numberOfPoints = rows * cols # 点集
    numberOfPolys = (rows - 1) * (cols - 1) # 线段集
    points = vtk.vtkPoints()
    points.Allocate(numberOfPoints)
    polys = vtk.vtkCellArray()
    polys.Allocate(numberOfPolys * 4)
    x = [0] * 3
    # double    x[3];
    cnt = 0
    for row in range(0, rows):
        for col in range(0, cols):
            p = [0]*3
            line.GetPoint(row, p)
            x[0] = p[0] + direction[0] * col * spacing
            x[1] = p[1] + direction[1] * col * spacing
            x[2] = p[2] + direction[2] * col * spacing
            cnt += 1
            points.InsertPoint(cnt, x)

    # Generate the quads
    # vtkIdType pts[4]
    pts = [0]*4
    for row in range(0, rows-1):
        for col in range(0, cols-1):
            pts[0] = col + row * (cols)
            pts[1] = pts[0] + 1
            pts[2] = pts[0] + cols + 1
            pts[3] = pts[0] + cols
            polys.InsertNextCell(4, pts)
    surface.SetPoints(points)
    surface.SetPolys(polys)

    return surface


if __name__ == '__main__':
    # colors = vtk.vtkNamedColors()
    imageReader = vtk.vtkDICOMImageReader()
    # imageReader.SetDirectoryName("./data/heartSystolicDicom")
    imageReader.SetDirectoryName("D:/Desktop/BigVTK/data/heartSystolicDicom")
    imageReader.Update()
    # 读取曲线数据
    polyLineReader =vtk.vtkPolyDataReader()
    # polyLineReader.SetFileName("./test.vtk")
    polyLineReader.SetFileName("D:/Desktop/BigVTK/tes_line.vtk")
    polyLineReader.Update()
    #从多段线的输入集生成输出多段线的Filter
    spline = vtk.vtkSplineFilter()
    resolution = 200
    spline.SetInputConnection(polyLineReader.GetOutputPort())
    spline.SetSubdivideToSpecified() #设置为多段线创建的细分数目
    spline.SetNumberOfSubdivisions(resolution)
    #扫线形成一个曲面
    # double direction[3];
    direction = [0] * 3
    direction[0] = 0.0
    direction[1] = 0.0
    direction[2] = 1.0
    distance = 164
    spline.Update()
    #自定义SweepLine方法
    surface = SweepLine(spline.GetOutput(), direction, distance, resolution)
    # Probe the volume with the extruded surface根据点和法向量截取图片(vtkProbeFilter)
    sampleVolume = vtk.vtkProbeFilter()
    sampleVolume.SetInputConnection(1, imageReader.GetOutputPort())
    sampleVolume.SetInputData(0, surface)
    # 基于标量范围计算一个简单的窗口 / 级别
    wlLut = vtk.vtkWindowLevelLookupTable()
    range = imageReader.GetOutput().GetScalarRange()[1] - imageReader.GetOutput().GetScalarRange()[0]
    level = (imageReader.GetOutput().GetScalarRange()[1] +
                                   imageReader.GetOutput().GetScalarRange()[0]) /2.0
    wlLut.SetWindow(range)
    wlLut.SetLevel(level)

    # Create a mapper and actor.
    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputConnection(sampleVolume.GetOutputPort())
    mapper.SetLookupTable(wlLut)
    mapper.SetScalarRange(0, 255)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # Create a renderer, render window, and interactor
    renderer = vtk.vtkRenderer()
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    renderWindow.SetWindowName("CurvedReformation")

    renderWindowInteractor = vtk.vtkRenderWindowInteractor()
    # style = vtk.vtkInteractorStyleTrackballCamera()
    # renderWindowInteractor.SetInteractorStyle(style)
    renderWindowInteractor.SetRenderWindow(renderWindow)

    #Add the actors to the scene
    renderer.AddActor(actor)
    renderer.SetBackground(0.1, 0.2, 0.4)

    # Set the camera for viewing medical images
    renderer.GetActiveCamera().SetViewUp(0, 0, 1)
    renderer.GetActiveCamera().SetPosition(0, 0, 0)
    renderer.GetActiveCamera().SetFocalPoint(0, 1, 0)
    renderer.ResetCamera()

    # Render and interact
    renderWindow.Render()
    renderWindowInteractor.Start()



