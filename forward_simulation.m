% forward_simulation.m
clear

addpath('/Users/nontakornbunluesriruang/Downloads/k-wave-toolbox-version-1/k-Wave')

% Set up the computational grid
Nx = 200;   % number of grid points in the x direction
Ny = 150;   % number of grid points in the y direction
dx = 7.5e-5;  % grid point spacing in the x direction [m]
dy = 7.5e-5;  % grid point spacing in the y direction [m]
kgrid = makeGrid(Nx, dx, Ny, dy);

% Define the properties of the medium
medium.sound_speed = 1500;  % [m/s]
medium.density = 1000;     % [kg/m^3]

% Define the source with initial pressure distribution (p0)
source.p0 = zeros(Nx, Ny);
source.p0(80, 70) = 2;  % setting the point source

% Define the sensor masks
sensor.mask = zeros(Nx, Ny);
sensor.mask(1, 150) = 1; % place sensor at (x, y) coordinates
% sensor.record = {'p'};
% sensor.mask = zeros(Nx, Ny);
% sensor.mask(1, :) = 1; % place sensors along the top edge


% Define additional optional input arguments
% Optional input arguments (including setting PMLAlpha to 0)
input_args = {'PMLInside', false, ...
              'PMLSize', [0, 0], ...
              'PMLAlpha', 1, ...  % Disable PML by setting PMLAlpha to 0
              'Smooth', false, ...
              'PlotPML', false}; 

% Run the forward simulation
sensor_data = kspaceFirstOrder2D(kgrid, medium, source, sensor, input_args{:});

% Add noise to the sensor data
signal_to_noise_ratio = 40;
sensor_data_noisy = addNoise(sensor_data, signal_to_noise_ratio, 'peak');
kgrid_struct = struct('Nx', 128, 'Ny', 128, 'dx', 0.1e-3, 'dy', 0.1e-3, 'dt', 50e-9, 't_array', 0:50e-9:1e-5);

% sensor_data_noisy = sensor_data;

% Save the noisy sensor data
save('sensor_data_noisy.mat', 'sensor_data_noisy', 'kgrid', 'kgrid_struct', 'medium', 'sensor', 'input_args');

% Plot the noisy sensor data
figure;
plot(sensor_data_noisy);
xlabel('Time Index');
ylabel('Pressure');
title('Noisy Sensor Data');



% Calculate mode shapes
[X, Y] = meshgrid((0:Nx-1) * dx, (0:Ny-1) * dy);
num_modes = 10;
M_0 = zeros(Nx * Ny, num_modes);
for m = 1:num_modes
    phi_m = sin(m * pi * X / (Nx * dx)) .* sin(m * pi * Y / (Ny * dy));
    M_0(:, m) = reshape(phi_m, [], 1);  % Reshape mode shape to column vector
end
% Reshape recorded data to match the number of spatial points
p_recorded = reshape(sensor_data_noisy, [], 1);  % 30,000 x 1 vector

save("sensor_data_noisy.mat", "p_recorded", "M_0", "sensor_data_noisy", "sensor", "medium")

A = M_0 \ p_recorded;  % Solve the system of equations
p0_reconstructed = reshape(M_0 * A, Nx, Ny);

% Display the reconstructed pressure distribution
figure;
imagesc(p0_reconstructed);
colorbar;
title('Reconstructed Initial Pressure Distribution');

