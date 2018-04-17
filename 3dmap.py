import vtk
import sys


def main():
    filename = "altitudes.txt"
    colors = vtk.vtkNamedColors()

    # To read from file
    sizeX = 3001
    sizeY = 3001
    sizeZ = 1
    dims = [sizeX, sizeY, sizeZ]

    radius = 6371009

    mapGrid = vtk.vtkStructuredGrid()
    mapGrid.SetDimensions(dims)

    x = 0
    y = 0

    minZ = sys.maxsize
    maxZ = -sys.maxsize - 1

    points = vtk.vtkPoints()

    with open(filename) as f:
        next(f)
        for line in f:
            x += 1
            y = 0
            for i in line.split():
                y += 1
                altitude = radius + int(i)
                if altitude < minZ:
                    minZ = altitude
                if altitude > maxZ:
                    maxZ = altitude
                longitude = y * (2.5 / (sizeX - 1))
                latitude = x * (2.5 / (sizeY - 1))

                p = [0, 0, altitude]

                transform = vtk.vtkTransform()
                transform.RotateX(latitude)
                transform.RotateY(longitude)

                # Apply the transform to the point p
                p = transform.TransformPoint(p)

                points.InsertNextPoint(p)

    mapGrid.SetPoints(points)

    # Create    the    color    map
    colorLookupTable = vtk.vtkLookupTable()
    colorLookupTable.SetTableRange(minZ, maxZ)
    colorLookupTable.Build()
    #
    # numPoints = mapGrid.GetNumberOfPoints()
    # for i in range(0, numPoints):
    #     point = mapGrid.GetPoint(i)
    #     color = colorLookupTable.GetColor(point[2])

    sgridMapper = vtk.vtkDataSetMapper()
    sgridMapper.SetInputData(mapGrid)
    sgridMapper.SetLookupTable(colorLookupTable)
    sgridMapper.SetScalarModeToUsePointFieldData()

    sgridActor = vtk.vtkActor()
    sgridActor.SetMapper(sgridMapper)
    # sgridActor.GetProperty().SetColor(colors.GetColor3d("peacock"))

    # Create the usual rendering stuff
    renderer = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(renderer)

    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    renderer.AddActor(sgridActor)
    renderer.SetBackground(colors.GetColor3d("Beige"))
    renderer.ResetCamera()

    # camera = vtk.vtkCamera()
    # camera.SetPosition(0, 0, 10000)
    #
    # renderer.SetActiveCamera(camera)
    # renderer.GetActiveCamera().Elevation(60.0)
    # renderer.GetActiveCamera().Azimuth(30.0)
    # renderer.GetActiveCamera().Dolly(1.25)
    renWin.SetSize(1000, 1000)

    # Interact with the data.
    renWin.Render()
    iren.Start()


if __name__ == "__main__":
    main()
