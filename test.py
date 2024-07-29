import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# Define grid size and spacing
Nx = 64
Ny = 64
Nz = 32
dx = 0.1e-3
dy = 0.1e-3
dz = 0.1e-3

# Initialize medium properties
medium_sound_speed = 1500 * np.ones((Nx, Ny, Nz))
medium_density = np.zeros((Nx, Ny, Nz))

# Define vertices of the triangular base
vertices_x = np.round(np.array([16, 32, 48]) / 2).astype(int)
vertices_y = np.round(np.array([16, 48, 16]) / 2).astype(int)

# Function to check if a point is inside the triangle
def inpolygon_custom(x, y, vertices_x, vertices_y):
    from matplotlib.path import Path
    points = np.array([vertices_x, vertices_y]).T
    path = Path(points)
    return path.contains_point((x, y))




def calculate_centroid_right_angle_triangle(vertices):
    A, B, C = vertices
    centroid = ((A[0] + B[0] + C[0]) / 3, (A[1] + B[1] + C[1]) / 3)
    return centroid
A = (0, 0)  # Vertex at the origin
B = (4, 0)  # Vertex on the x-axis
C = (0, 3)  # Vertex on the y-axis
centroid = calculate_centroid_right_angle_triangle([A, B, C])
centroid


# define the gird as the initial height & width of the prism, face
# coor  -   (0, 0, 0), (0, y_l, 0) (x_l, 0, 0)

# vertices of a 5 cm, 7 cm base 90 deg prism
prism_z_end = 30 # z-axis prism in mm
vertices_x = [0, 50, 0]
vertices_y = [0, 0, 50]
for z in range(Nz):
    for x in range(Nx):
        for y in range(Ny):
            if inpolygon_custom(x, y, vertices_x, vertices_y):
                medium_density[x, y, z] = 1000


fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
base_triangle = [[(vertices_x[0], vertices_y[0], 0),
                  (vertices_x[1], vertices_y[1], 0),
                  (vertices_x[2], vertices_y[2], 0)]]

# Extend the triangle to create the prism
for z in range(0, prism_z_end + 1):
    ax.add_collection3d(Poly3DCollection(base_triangle, facecolors='cyan', linewidths=1, edgecolors='r', alpha=.25))
    base_triangle = [[(vertices_x[0], vertices_y[0], z),
                      (vertices_x[1], vertices_y[1], z),
                      (vertices_x[2], vertices_y[2], z)]]
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

ax.scatter(0, 50, 0, color='magenta', s=100)  # s is the size of the point

ax.set_xlim([0, Nx])
ax.set_ylim([0, Ny])
ax.set_zlim([0, Nz])

plt.show()
    