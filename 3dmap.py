import math
import vtk
import sys

# To read from file
SIZE_X = 3001
SIZE_Y = 3001


def loadingBar(current, total, info):
    if current % int(total / 100) == 0:
        loaded = int(current // int(total / 100))
        print('[' + '#' * loaded + '-' * (100 - loaded) + ']' + str(loaded) + '% ' + info)


def isPointWater(array, idx):
    def matrixToInline(x, y):
        return x + SIZE_X * y

    def inlineToMatrix(idx):
        x = idx % SIZE_X
        y = idx // SIZE_X
        return x, y

    x, y = inlineToMatrix(idx)
    minX = max(0, x - 1)
    maxX = min(x + 1, SIZE_X - 1)
    minY = max(0, y - 1)
    maxY = min(y + 1, SIZE_Y - 1)

    altitude = array.GetValue(idx)

    p1 = matrixToInline(maxX, minY)
    p2 = matrixToInline(maxX, y)
    p3 = matrixToInline(maxX, maxY)
    p4 = matrixToInline(x, minY)
    p5 = matrixToInline(x, maxY)
    p6 = matrixToInline(minX, minY)
    p7 = matrixToInline(minX, y)
    p8 = matrixToInline(minX, maxY)

    return altitude == array.GetValue(p1) == array.GetValue(p2) == array.GetValue(p3) == array.GetValue(
        p4) == array.GetValue(p5) == array.GetValue(p6) == array.GetValue(p7) == array.GetValue(p8)


def main():
    filename = "altitudes.txt"
    colors = vtk.vtkNamedColors()

    SIZE_Z = 1
    dims = [SIZE_X, SIZE_Y, SIZE_Z]

    radius = 6371009

    mapGrid = vtk.vtkStructuredGrid()
    mapGrid.SetDimensions(dims)

    array = vtk.vtkIntArray()

    x = 0

    points = vtk.vtkPoints()

    with open(filename) as f:
        next(f)
        for line in f:
            loadingBar(x, SIZE_X, 'Loading file')
            x += 1
            y = 0
            for i in line.split():
                y += 1

                # High water mode
                # currentValue = max(370, int(i))
                currentValue = int(i)
                altitude = radius + currentValue
                array.InsertNextValue(currentValue)

                longitude = 5 + y * (2.5 / SIZE_Y)
                latitude = 45 + x * (2.5 / SIZE_X)

                longitude = math.radians(longitude)
                latitude = math.radians(latitude)

                p = [altitude, latitude, longitude]
                transform = vtk.vtkSphericalTransform()

                # Apply the transform to the point p
                p = transform.TransformPoint(p)

                points.InsertNextPoint(p)

    mapGrid.SetPoints(points)

    a, b = array.GetValueRange()

    waterIndexes = []
    numberOfPoints = mapGrid.GetNumberOfPoints()
    # for i in range(0, numberOfPoints):
    #     loadingBar(i, numberOfPoints, 'Checking water')
    #     if isPointWater(array, i):
    #         waterIndexes.append(i)

    for index in waterIndexes:
        array.SetValue(index, 0)

    mapGrid.GetPointData().SetScalars(array)

    def addRGBPoint(p, r, g, b):
        lut.AddRGBPoint(p, r / 255, g / 255, b / 255)

    lut = vtk.vtkColorTransferFunction()
    # The water has value 0 which is below the color range
    lut.SetBelowRangeColor(64 / 255, 61 / 255, 128 / 255)
    lut.SetUseBelowRangeColor(True)

    # Minimal altitude is forest
    addRGBPoint(a, 53, 96, 48)
    # No forest after 1800 meters
    addRGBPoint(1800, 237, 215, 187)
    # Snow from 2200 meters
    addRGBPoint(2200, 255, 255, 255)
    addRGBPoint(b, 255, 255, 255)

    lut.Build()

    sgridMapper = vtk.vtkDataSetMapper()
    sgridMapper.SetInputData(mapGrid)

    sgridMapper.SetLookupTable(lut)
    sgridMapper.SetScalarRange(a, b)
    sgridMapper.SetScalarModeToUsePointData()

    # a colorbar to display the colormap
    scalarBar = vtk.vtkScalarBarActor()
    scalarBar.SetLookupTable(sgridMapper.GetLookupTable())
    scalarBar.SetTitle("Altitude")
    scalarBar.SetOrientationToVertical()
    scalarBar.GetLabelTextProperty().SetColor(0, 0, 0)
    scalarBar.GetTitleTextProperty().SetColor(0, 0, 0)
    scalarBar.DrawBelowRangeSwatchOn()
    scalarBar.SetBelowRangeAnnotation("Water")
    scalarBar.AnnotationTextScalingOn()
    scalarBar.GetAnnotationTextProperty().SetColor(0, 0, 0)
    scalarBar.SetLabelFormat("%4.0f")

    # position it in window
    coord = scalarBar.GetPositionCoordinate()
    coord.SetCoordinateSystemToNormalizedViewport()
    coord.SetValue(0.82, 0.1)
    scalarBar.SetWidth(.15)
    scalarBar.SetHeight(.7)

    sgridActor = vtk.vtkActor()
    sgridActor.SetMapper(sgridMapper)

    # Create the usual rendering stuff
    renderer = vtk.vtkRenderer()

    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(renderer)

    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    renderer.AddActor(sgridActor)
    renderer.AddActor(scalarBar)
    renderer.SetBackground(colors.GetColor3d("Grey"))

    camera = vtk.vtkCamera()
    r = radius
    phi = math.radians(46.25)
    theta = math.radians(6.25)
    camera.SetFocalPoint(
        r * math.sin(phi) * math.cos(theta),
        r * math.sin(phi) * math.sin(theta),
        r * math.cos(phi))

    r = radius * 1.5
    phi = math.radians(46.25)
    theta = math.radians(6.25)
    camera.SetPosition(
        r * math.sin(phi) * math.cos(theta),
        r * math.sin(phi) * math.sin(theta),
        r * math.cos(phi))

    renderer.SetActiveCamera(camera)
    renderer.ResetCameraClippingRange()

    renWin.SetSize(1000, 1000)

    # Interact with the data.
    renWin.Render()
    iren.Start()


if __name__ == "__main__":
    main()
