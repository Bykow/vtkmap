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

    array = vtk.vtkIntArray()

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

                array.InsertNextValue(altitude)

                transform = vtk.vtkTransform()
                transform.RotateX(longitude)
                transform.RotateY(latitude)

                # Apply the transform to the point p
                p = transform.TransformPoint(p)

                points.InsertNextPoint(p)

    mapGrid.SetPoints(points)
    mapGrid.GetPointData().SetScalars(array)

    a, b = array.GetValueRange()

    lut = vtk.vtkColorTransferFunction()
    lut.AddRGBPoint(a, 0.3, 1.0, 0.3)
    lut.AddRGBPoint(a + (b - a) / 4, 0.5, 1.0, 0.5)
    lut.AddRGBPoint(a + (b - a) / 2, 0.6, 0.4, 0)
    lut.AddRGBPoint(b - (b - a) / 4, 0.8, 0.8, 0.8)
    lut.AddRGBPoint(b, 1.0, 1.0, 1.0)
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

    # position it in window
    coord = scalarBar.GetPositionCoordinate()
    coord.SetCoordinateSystemToNormalizedViewport()
    coord.SetValue(0.85, 0.1)
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
    renderer.ResetCamera()

    renWin.SetSize(1500, 1500)

    # Interact with the data.
    renWin.Render()
    iren.Start()


if __name__ == "__main__":
    main()
