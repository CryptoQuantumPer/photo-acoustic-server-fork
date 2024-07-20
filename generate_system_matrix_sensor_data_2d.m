clear

addpath('/Users/nontakornbunluesriruang/Downloads/k-wave-toolbox-version-1/k-Wave')

poolobj = gcp('nocreate');
if ~isempty(poolobj)
    delete(poolobj);
end
% parpool('local'); % commment if disable parallel computation

% Set up the computational grid
Nx = 160;   % number of grid points in the x direction
Ny = 120;   % number of grid points in the y direction
% dx = 7.5e-5;  % grid point spacing in the x direction [m]
% dy = 7.5e-5;  % grid point spacing in the y direction [m]
dx = 3e-5;
dy = 3e-5;

% Define the properties of the medium
medium.sound_speed = 1500;  % [m/s]
medium.density = 1000;     % [kg/m^3]


kgrid = makeGrid(Nx, dx, Ny, dy);
num_time_steps = 600;       % Number of time steps for the simulation
cfl = 1;                   % CFL number for time step calculation
dt = cfl * dx / medium.sound_speed; % Time step size
t_end = dt * (num_time_steps - 1);  % Total simulation time
kgrid.t_array = 0:dt:t_end;  % Time array for the simulation
disp(kgrid.t_array)

% Define the source with initial pressure distribution (p0)
% --use the following source code for single source point
% source.p0 = zeros(Nx, Ny);
% source.p0(80, 70) = 2;  % setting the point source

% Define the sensor masks
sensor.mask = zeros(Nx, Ny);
sensor.mask(1, 120) = 1; % place sensor at (x, y) coordinates
% sensor.mask = zeros(Nx, Ny);
% sensor.mask(1, :) = 1; % place sensors along the top edge

% Define additional optional input arguments
input_args = {'PMLInside', false, ...
              'PMLSize', [0, 0], ...
              'PMLAlpha', 0, ...  % Disable PML by setting PMLAlpha to 0
              'Smooth', false, ...
              'PlotPML', false,}


% create A system matrix
K = {};
for m = 1:10:Ny
    for n = 1:10:Nx
        fprintf('x: %d, y: %d\n', n, m);
        source.p0 = zeros(Nx, Ny);
        source.p0(n, m) = 2;
        k_sensor_output = kspaceFirstOrder2D(kgrid, medium, source, sensor, input_args{:});
        fprintf('k_sensor_output: %d\n shape', k_sensor_output); 
        K = [K, k_sensor_output];
    end
end

save('system_matrix.mat', 'K')

% generate binary Image sensor data
binary_image = imread('vascular.png');
binary_image = im2bw(binary_image);
binary_image = imresize(binary_image, [Nx, Ny]);  % Resize the image to match the grid
source.p0 = double(binary_image);

% Run the forward simulation
sensor_data = kspaceFirstOrder2D(kgrid, medium, source, sensor, input_args{:});

% Add noise to the sensor data
signal_to_noise_ratio = 40;
sensor_data_noisy = addNoise(sensor_data, signal_to_noise_ratio, 'peak');

% Plot the noisy sensor data
figure;
plot(sensor_data_noisy);
xlabel('Time Index');
ylabel('Pressure');
title('Simulated Noisy Sensor Data');

% Calculate mode shapes
[X, Y] = meshgrid((0:Nx-1) * dx, (0:Ny-1) * dy);
num_modes = 10;
M_0 = zeros(Nx * Ny, num_modes);
for m = 1:num_modes
    phi_m = sin(m * pi * X / (Nx * dx)) .* sin(m * pi * Y / (Ny * dy));
    M_0(:, m) = reshape(phi_m, [], 1);  % Reshape mode shape to column vector
end

% Reshape recorded data to match the number of spatial points
p_recorded = reshape(sensor_data_noisy, [], 1);  % Reshape to a vector

save("sensor_data_noisy.mat", "p_recorded", "M_0", "sensor_data_noisy", "sensor", "medium")