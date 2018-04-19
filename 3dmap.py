import math
import vtk
import sys

# Size of the data to read
SIZE_X = 3001
SIZE_Y = 3001


def loadingBar(current, total, info):
    if current % int(total / 100) == 0:
        loaded = int(current // int(total / 100))
        print('[' + '#' * loaded + '-' * (100 - loaded) + ']' + str(loaded) + '% ' + info)


def isPointWater(array, idx):
    """
    Defines wether a point is suppose to be water or not

    :param array: array of data
    :param idx: index to check
    :return: boolean, true if water, false otherwise
    """
    def matrixToInline(x, y):
        """
        Convert a matrix (n,m) representation to linear array

        :param x: x linked to n
        :param y: y linked to m
        :return: linear index
        """
        return x + SIZE_X * y

    def inlineToMatrix(idx):
        """
        Convert a linear index to matrix representation

        :param idx: index to convert
        :return: (x,y) index in matrix
        """
        x = idx % SIZE_X
        y = idx // SIZE_X
        return x, y

    # Computing edges values to avoid out of bounds efect
    x, y = inlineToMatrix(idx)
    minX = max(0, x - 1)
    maxX = min(x + 1, SIZE_X - 1)
    minY = max(0, y - 1)
    maxY = min(y + 1, SIZE_Y - 1)

    # Current altitude
    altitude = array.GetValue(idx)

    # Look for neighbours altitude
    p1 = matrixToInline(maxX, minY)
    p2 = matrixToInline(maxX, y)
    p3 = matrixToInline(maxX, maxY)
    p4 = matrixToInline(x, minY)
    p5 = matrixToInline(x, maxY)
    p6 = matrixToInline(minX, minY)
    p7 = matrixToInline(minX, y)
    p8 = matrixToInline(minX, maxY)

    # Is all the points at same altitude ?
    return altitude == array.GetValue(p1) == array.GetValue(p2) == array.GetValue(p3) == array.GetValue(
        p4) == array.GetValue(p5) == array.GetValue(p6) == array.GetValue(p7) == array.GetValue(p8)


def main():
    filename = "altitudes.txt"
    colors = vtk.vtkNamedColors()

    radius = 6371009

    SIZE_Z = 1
    dims = [SIZE_X, SIZE_Y, SIZE_Z]

    # Structured Grid because space between points is always the same
    mapGrid = vtk.vtkStructuredGrid()
    mapGrid.SetDimensions(dims)

    # Points to insert into Structured Grid
    points = vtk.vtkPoints()

    # Array that saves only the heights, uses for color
    heights = vtk.vtkIntArray()

    x = 0

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
                height = radius + currentValue
                heights.InsertNextValue(currentValue)

                longitude = 5 + y * (2.5 / SIZE_Y)
                latitude = 45 + x * (2.5 / SIZE_X)

                longitude = math.radians(longitude)
                latitude = math.radians(latitude)

                p = [height, latitude, longitude]
                # Applies a spherical transform to the point, given a distance (height)
                # and two angles (longitude, latitude) expressed in radians
                transform = vtk.vtkSphericalTransform()

                # Apply the transform to the point p
                p = transform.TransformPoint(p)

                points.InsertNextPoint(p)

    mapGrid.SetPoints(points)

    # Get the range (min, max) values of the array
    a, b = heights.GetValueRange()

    # Water detection, we save a new array of index to modify after compute of said points
    waterIndexes = []

    for i in range(0, mapGrid.GetNumberOfPoints()):
        if isPointWater(heights, i):
            waterIndexes.append(i)

    # Setting height of water to 0
    for index in waterIndexes:
        heights.SetValue(index, 0)

    mapGrid.GetPointData().SetScalars(heights)

    def addRGBPoint(p, r, g, b):
        """
        Adds a RGB point to the lookup table. Devides the color by 255
        Example: (3000, 45, 45, 45)

        :param p: point (height)
        :param r: red
        :param g: green
        :param b: blue
        :return:
        """
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
    # Upper bound of scale
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
