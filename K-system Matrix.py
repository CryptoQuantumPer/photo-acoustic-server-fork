import numpy as np
import scipy


# Load data from the MATLAB file
def load_kwave_data(filename):
    data = scipy.io.loadmat(filename)
    sensor_data = data['sensor_data_noisy']
    # kgrid = data['kgrid_struct']
    medium = data['medium']
    sensor = data['sensor']
    return sensor_data, medium, sensor


# Example usage
sensor_data, medium, sensor = load_kwave_data('sensor_data_noisy.mat')


def generate_system_matrix(sensor_data, kgrid, medium, sensor):
    Nx = int(kgrid['Nx'][0][0])
    Ny = int(kgrid['Ny'][0][0])
    dx = float(kgrid['dx'][0][0])
    dy = float(kgrid['dy'][0][0])
    dt = float(kgrid['dt'][0][0])
    sound_speed = float(medium['sound_speed'][0][0])
    sensor_mask = sensor['mask']

    num_sensors = sensor_mask.shape[1]
    num_time_points = sensor_data.shape[0]
    num_voxels = Nx * Ny

    K = np.zeros((num_sensors * num_time_points, num_voxels))

    for ix in range(Nx):
        for iy in range(Ny):
            # Generate an impulse response for voxel (ix, iy)
            p0 = np.zeros((Nx, Ny))
            print(p0[ix, iy], p0)
            p0[ix, iy] = 1

            # Flatten the initial pressure distribution
            p0_flat = p0.flatten()

            # Calculate the contribution of this voxel to each sensor's measurement
            for sensor_idx in range(num_sensors):
                # Find the position of the sensor in the grid
                sensor_positions = np.column_stack(np.where(sensor_mask))
                sensor_position = sensor_positions[sensor_idx]

                # Calculate the distance from the voxel to the sensor
                distance = np.sqrt(((ix - sensor_position[0]) * dx) ** 2 + ((iy - sensor_position[1]) * dy) ** 2)
                time_delay = int(distance / sound_speed / dt)

                if time_delay < num_time_points:
                    K[sensor_idx * num_time_points + time_delay, ix * Ny + iy] = 1

    return K


# Generate the system matrix
K = generate_system_matrix(sensor_data, medium, sensor)

# Save the system matrix to a .mat file
scipy.io.savemat('system_matrix_generated.mat', {'K': K})
