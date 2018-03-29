import vtk

filename = "altitudes.txt"

with open(filename) as f:
    content = f.readlines()

# To read from file
sizeX = 3001
sizeY = 3001


radius = 6371009

mapGrid = vtk.vtkStructuredGrid(sizeX, sizeY, 1)

x = 0
y = 0

points = vtk.vtkPoints()

with open(filename) as f:
    for line in f:
        x += 1
        for i in line.split():
            y += 1
            altitude = radius + i
            longitude = y*(2.5/3000)
            latitude = x*(2.5/3000)
            p = vtk.vtkPoint(0, 0, altitude)

            transform = vtk.vtkTransform()
            transform.RotateX(latitude)
            transform.RotateY(longitude)

            # Apply the transform to the point p
            transform.Transform(p)

            points.InsertNextPoint(p)



