'''
@author: Darren Janeczek
'''

from vtk import *
import os


def viewer_callback(points, screenshot_file=None):
    view_polydata(mesh_from_point_matrix(points), screenshot_file)


def mesh_from_point_matrix(P):
    ''' Utility '''
    

    M, N, _ = P.shape

    cells = vtkCellArray()
    points = vtkPoints()
    polydata = vtkPolyData()

    polydata.SetPolys(cells)
    polydata.SetPoints(points)

    for i in range(M):
        for j in range(N):
            points.InsertNextPoint(P[i,j])
            

    for i in range(M-1):
        for j in range(N-1):
            cells.InsertNextCell(3)
            cells.InsertCellPoint(i * N + j)
            cells.InsertCellPoint(i * N + j + 1)
            cells.InsertCellPoint((i+1) * N + j)

            cells.InsertNextCell(3)
            cells.InsertCellPoint((i+1) * N + j)
            cells.InsertCellPoint((i+1) * N + j + 1)
            cells.InsertCellPoint(i * N + j + 1)



    return polydata


def view_polydata(mesh, screenshot_file=None):
    ''' Utility '''

    mapper = vtkPolyDataMapper()

    mapper.SetInputData(mesh)
    mapper.SetScalarRange(0, 0)

    actor = vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().ShadingOn()
    actor.GetProperty().SetColor(.6, .3, .15)
    actor.GetProperty().SetSpecular(1.0)

    mapper.ScalarVisibilityOff()

    renderer = vtkRenderer()
    renderer.SetTwoSidedLighting(1)

    renderWindow = vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    renderWindowInteractor = vtkRenderWindowInteractor()
    renderWindowInteractor.SetInteractorStyle(vtkInteractorStyleTrackballCamera())
    renderWindowInteractor.SetRenderWindow(renderWindow)
    renderWindow.SetSize(1920, 1080)

    renderer.AddActor(actor)
    renderer.SetBackground(.2, .3, .4)

    camera = vtkCamera()
    camera.SetPosition(0.5, -1.0, 0.5)
    center = mesh.GetCenter()
    camera.SetFocalPoint(*center)

    renderer.SetActiveCamera(camera)
    renderer.SetUseDepthPeeling(0)
    camera.SetViewUp(0, 0, 1.0)

    renderWindow.Render()


    if screenshot_file:
        windowToImageFilter = vtkWindowToImageFilter()

        magnification = 1

        windowToImageFilter.SetInput(renderWindow)
        windowToImageFilter.SetScale(magnification, magnification)
        windowToImageFilter.SetInputBufferTypeToRGBA()
        windowToImageFilter.ReadFrontBufferOn()
        windowToImageFilter.SetShouldRerender(1)
        windowToImageFilter.Update()

        writer = vtkPNGWriter()
        writer.SetFileName(screenshot_file)
        writer.SetInputConnection(windowToImageFilter.GetOutputPort())
        ensure_directory_exists(screenshot_file)
        writer.Write()

    else:
        renderWindowInteractor.Start()
    


def ensure_directory_exists(screenshot_file):
    directory = os.path.dirname(screenshot_file)
    if not os.path.exists(directory):
        os.makedirs(directory)