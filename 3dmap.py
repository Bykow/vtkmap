import vtk

def main():
    filename = "altitudes.txt"
    colors = vtk.vtkNamedColors()

    # To read from file
    SIZE_X = 3001
    SIZE_Y = 3001
    SIZE_Z = 1
    dims = [SIZE_X, SIZE_Y, SIZE_Z]

    radius = 6371009

    mapGrid = vtk.vtkStructuredGrid()
    mapGrid.SetDimensions(dims)

    x = 0

    points = vtk.vtkPoints()

    with open(filename) as f:
        next(f)
        for line in f:
            x += 1
            y = 0
            for i in line.split():
                y += 1
                altitude = radius + int(i)
                longitude = y * (2.5 / (SIZE_Y - 1))
                latitude = x * (2.5 / (SIZE_X - 1))

                p = [0, 0, altitude]

                transform = vtk.vtkTransform()
                transform.RotateX(longitude)
                transform.RotateY(latitude)

                # Apply the transform to the point p
                p = transform.TransformPoint(p)

                points.InsertNextPoint(p)

    mapGrid.SetPoints(points)

    lut = vtk.vtkLookupTable()
    lut.SetNumberOfColors(16)
    lut.SetTableRange(minA, maxA)
    lut.Build()

    sgridMapper = vtk.vtkDataSetMapper()
    sgridMapper.SetInputData(mapGrid)

    sgridMapper.SetLookupTable(lut)

    sgridActor = vtk.vtkActor()
    sgridActor.SetMapper(sgridMapper)
    sgridActor.GetProperty().SetColor(colors.GetColor3d("Peacock"))

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
    renWin.SetSize(1500, 1500)

    # Interact with the data.
    renWin.Render()
    iren.Start()


if __name__ == "__main__":
    main()
