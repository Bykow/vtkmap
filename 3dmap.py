import math
import vtk

FILENAME = "altitudes.txt"
# Size of the data to read
SIZE_X = 3001
SIZE_Y = 3001
SIZE_Z = 1

# Latitude and longitude bounds
MIN_LONG = 5.0
MAX_LONG = 7.5
MIN_LAT = 45.0
MAX_LAT = 47.5

# Different parameters, in meters above sea
EARTH_RADIUS = 6371009
FOREST_LIMIT = 1800
SNOW_LIMIT = 2200
SEA_LEVEL = 0
CAMERA_ALTITUDE = 1000000


def loadingBar(current, total, info):
    """
       Displays a loading bar with a custom message

        :param current: current value
        :param total: total number of values
        :param infos: message to display next to the loading bar
        """
    if current % int(total / 100) == 0:
        loaded = int(current // int(total / 100))
        print('[' + '#' * loaded + '-' * (100 - loaded) + ']' + str(loaded) + '% ' + info)


def sphericalToCartesian(r, phi, theta):
    phi = math.radians(phi)
    theta = math.radians(theta)
    return (
        r * math.sin(phi) * math.cos(theta),
        r * math.sin(phi) * math.sin(theta),
        r * math.cos(phi)
    )


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

    # Computing edges values to avoid out of bounds effect
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
    namedColors = vtk.vtkNamedColors()
    sphericalTransform = vtk.vtkSphericalTransform()

    dims = [SIZE_X, SIZE_Y, SIZE_Z]

    # Structured Grid because space between points is always the same
    structuredGrid = vtk.vtkStructuredGrid()
    structuredGrid.SetDimensions(dims)

    # Points to insert into Structured Grid
    points = vtk.vtkPoints()

    # Array that saves only the heights, used for color
    heights = vtk.vtkIntArray()

    x = 0
    with open(FILENAME) as f:
        next(f)
        for line in f:
            loadingBar(x, SIZE_X, 'Loading file')

            x += 1
            y = 0
            for i in line.split():
                y += 1

                # Allows to modify the sea level
                currentValue = max(SEA_LEVEL, int(i))
                height = EARTH_RADIUS + currentValue
                heights.InsertNextValue(currentValue)

                longitude = MIN_LONG + y * ((MAX_LONG - MIN_LONG) / SIZE_Y)
                latitude = MIN_LAT + x * ((MAX_LAT - MIN_LAT) / SIZE_X)

                p = [height, math.radians(latitude), math.radians(longitude)]
                # Applies a spherical transform to the point, given a distance (height)
                # and two angles (longitude, latitude) expressed in radians

                # Apply the transform to the point p
                p = sphericalTransform.TransformPoint(p)

                points.InsertNextPoint(p)

    structuredGrid.SetPoints(points)

    # Get the range (min, max) values of the array
    a, b = heights.GetValueRange()

    # Water detection, we save a new array of index to modify after compute of said points
    waterIndexes = []
    numberOfPoints = structuredGrid.GetNumberOfPoints()
    for i in range(0, numberOfPoints):
        loadingBar(i, numberOfPoints, 'Detecting water')
        if isPointWater(heights, i):
            waterIndexes.append(i)

    # Setting height of water to 0
    for index in waterIndexes:
        heights.SetValue(index, 0)

    structuredGrid.GetPointData().SetScalars(heights)

    def addRGBPoint(p, r, g, b):
        """
        Adds a RGB point to the lookup table. Divides the color by 255
        Example: (3000, 45, 45, 45)

        :param p: point (height)
        :param r: red
        :param g: green
        :param b: blue
        :return:
        """
        lut.AddRGBPoint(p, r / 255, g / 255, b / 255)

    lut = vtk.vtkColorTransferFunction()
    # The water scalars has a value 0 which is below the color range
    lut.SetBelowRangeColor(64 / 255, 61 / 255, 128 / 255)
    lut.SetUseBelowRangeColor(True)

    # Minimal altitude is forest
    addRGBPoint(a, 53, 96, 48)
    # Forest limit
    addRGBPoint(FOREST_LIMIT, 237, 215, 187)
    # Snow limit
    addRGBPoint(SNOW_LIMIT, 255, 255, 255)
    # Upper bound of scale
    addRGBPoint(b, 255, 255, 255)

    lut.Build()

    structuredGridMapper = vtk.vtkDataSetMapper()
    structuredGridMapper.SetInputData(structuredGrid)

    structuredGridMapper.SetLookupTable(lut)
    structuredGridMapper.SetScalarRange(a, b)
    structuredGridMapper.SetScalarModeToUsePointData()

    # A colorbar to display the colormap
    scalarBar = vtk.vtkScalarBarActor()
    scalarBar.SetLookupTable(structuredGridMapper.GetLookupTable())
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

    structuredGridActor = vtk.vtkActor()
    structuredGridActor.SetMapper(structuredGridMapper)

    # Create the usual rendering stuff
    renderer = vtk.vtkRenderer()

    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(renderer)

    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    renderer.AddActor(structuredGridActor)
    renderer.AddActor(scalarBar)
    renderer.SetBackground(namedColors.GetColor3d("Grey"))

    camera = vtk.vtkCamera()

    # The focal point is the center of the map
    center = [EARTH_RADIUS,
              math.radians(MIN_LAT + (MAX_LAT - MIN_LAT) / 2.0),
              math.radians(MIN_LONG + (MAX_LONG - MIN_LONG) / 2.0)
              ]

    camera.SetFocalPoint(sphericalTransform.TransformPoint(center))

    # The camera is positioned in front of the center of the map
    center[0] += CAMERA_ALTITUDE

    camera.SetPosition(sphericalTransform.TransformPoint(center))

    # Rotate the camera to display the map correctly
    camera.Roll(-94)

    renderer.SetActiveCamera(camera)
    renderer.ResetCameraClippingRange()

    renWin.SetSize(1000, 1000)

    # Interact with the data.
    renWin.Render()
    iren.Start()


if __name__ == "__main__":
    main()
