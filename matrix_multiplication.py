import scipy
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from numpy.linalg import inv

def load_kwave_data(filename):
    data = scipy.io.loadmat(filename)
    sensor_data = data['sensor_data_noisy']
    medium = data['medium']
    sensor = data['sensor']
    M_0 = data['M_0']
    p_recorded = data['p_recorded']
    return sensor_data, medium, sensor, M_0, p_recorded


sensor_data, medium, sensor, M_0, p_recorded = load_kwave_data('sensor_data_noisy')
# matrix_inv = inv(M_0) * p_recorded
# matrix_div = M_0/p_recorded
print(M_0)
plt.plot(p_recorded)
plt.show()
# print(np.shape(M_0[0]))

result = [[sum(a*b for a,b in zip(X_row,Y_col)) for Y_col in zip(*p_recorded)] for X_row in M_0]

for r in result:
   print(r)
plt.imshow(result)
plt.show()


import numpy as np

# Example grid parameters
Nx = 200
Ny = 150
dx = 7.5e-5
dy = 7.5e-5
num_modes = 10

# Generate a grid
x = np.linspace(0, (Nx-1)*dx, Nx)
y = np.linspace(0, (Ny-1)*dy, Ny)
X, Y = np.meshgrid(x, y)

# Calculate mode shapes
M_0 = np.zeros((Nx * Ny, num_modes))
for m in range(1, num_modes + 1):
    phi_m = np.sin(m * np.pi * X / (Nx * dx)) * np.sin(m * np.pi * Y / (Ny * dy))
    M_0[:, m - 1] = phi_m.flatten()

# Generate an example p_recorded array (using random values for this example)
np.random.seed(0)  # For reproducibility
p_recorded = np.random.rand(Nx * Ny)

# Ensure compatibility of dimensions
assert M_0.shape[0] == len(p_recorded), 'Dimensions of M_0 and p_recorded must match'

# Solve for mode amplitudes using matrix inversion
# Note: Direct inversion might not be numerically stable for all cases
# A = np.linalg.inv(M_0.T @ M_0) @ M_0.T @ p_recorded
# A more stable approach would be to use a solver
A = np.linalg.lstsq(M_0, p_recorded, rcond=None)[0]

# Reconstruct initial pressure distribution
p0_reconstructed = M_0 @ A
p0_reconstructed = p0_reconstructed.reshape(Nx, Ny)

# Display the reconstructed pressure distribution (requires matplotlib)
import matplotlib.pyplot as plt
plt.imshow(p0_reconstructed, extent=(0, Nx*dx, 0, Ny*dy))
plt.colorbar()
plt.title('Reconstructed Initial Pressure Distribution')
plt.xlabel('x [m]')
plt.ylabel('y [m]')
plt.show()

