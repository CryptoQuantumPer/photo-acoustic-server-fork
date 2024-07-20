import matlab.engine

# Start MATLAB engine
eng = matlab.engine.start_matlab()

# Add k-Wave toolbox path
eng.addpath('path_to_kwave_toolbox', nargout=0)

# Example usage of k-Wave functions
Nx = 128
Ny = 128
dx = 0.1  # Grid point spacing in x direction [m]
dy = 0.1  # Grid point spacing in y direction [m]
dt = 1e-7  # Time step [s]
Nt = 100  # Number of time steps

# Create computational grid
kgrid = eng.makeGrid(Nx, dx, Ny, dy)

# Create initial pressure distribution
source.p0 = eng.gaussian_source(Nx, Ny, 50, 50, 10)

# Define the properties of the propagation medium
medium.sound_speed = eng.ones(Nx, Ny) * 1500  # [m/s]
medium.density = eng.ones(Nx, Ny) * 1000  # [kg/m^3]

# Run the simulation
sensor_data = eng.kspaceFirstOrder2D(kgrid, medium, source)

# Process the simulation results in Python
sensor_data = eng.workspace['sensor_data']
print(sensor_data)

# Stop MATLAB engine
eng.quit()
