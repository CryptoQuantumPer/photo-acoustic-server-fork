clear

addpath('/Users/nontakornbunluesriruang/Downloads/k-wave-toolbox-version-1/k-Wave')

poolobj = gcp('nocreate');
if ~isempty(poolobj)
    delete(poolobj);
end
bool_parallel_computation = true;
if bool_parallel_computation == true
    parpool('local'); % commment if disable parallel computation
end

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
% num_time_steps = 10000;       % Number of time steps for the simulation
% cfl = 2;                   % CFL number for time step calculation
% dt = cfl * dx / medium.sound_speed; % Time step size
% t_end = dt * (num_time_steps - 1);  % Total simulation time
% kgrid.t_array = 0:dt:t_end;  % Time array for the simulation
% disp(kgrid.t_array)

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
              'PlotPML', false,};

             
% false : if skip the generation of system matrix
num_xy_steps_pixel = 1;
bool_generate_system_matrix = true;
bool_save_system_matrix_k = true;
if bool_generate_system_matrix == true
    K = {};
    for m = 1:num_xy_steps_pixel:Ny
        for n = 1:num_xy_steps_pixel:Nx
            fprintf('x: %d, y: %d\n', n, m);
            source.p0 = zeros(Nx, Ny); 
            source.p0(n, m) = 1;
            k_sensor_output = kspaceFirstOrder2D(kgrid, medium, source, sensor, input_args{:});
            disp(size(k_sensor_output))
            K = [K, k_sensor_output];
        end
    end
    if bool_save_system_matrix_k == true
        save('system_matrix.mat', 'K');
    end
end


% load binary Image for inputing as sensor data
source.p0 = zeros(Nx, Ny);
binary_image = imread('vascular.png');
binary_image = im2bw(binary_image);
binary_image = imresize(binary_image, [Nx, Ny]);  % Resize the image to match the grid
% source.p0 = double(binary_image);
% source.p0(80, 70) = 1;  % setting the point source

center_x = 50;  % X coordinate of the center
center_y = 60;  % Y coordinate of the center
width = 10;     % Width of the square
height = 10;    % Height of the square
grid = zeros(Nx, Ny);

half_width = width / 2;
half_height = height / 2;

x_start = round(center_x - half_width);
x_end = round(center_x + half_width - 1);
y_start = round(center_y - half_height);
y_end = round(center_y + half_height - 1);
x_start = max(x_start, 1);
x_end = min(x_end, Nx);
y_start = max(y_start, 1);
y_end = min(y_end, Ny);
grid(x_start:x_end, y_start:y_end) = 1;

imagesc(grid);
axis equal;
colorbar;
title('Square Source in the Grid');

source.p0 = grid;


% Run the forward simulation
sensor_data = kspaceFirstOrder2D(kgrid, medium, source, sensor, input_args{:});

% Add noise to the sensor data
% signal_to_noise_ratio = 0;
% sensor_data_noisy = addNoise(sensor_data, signal_to_noise_ratio, 'peak');
sensor_data_noisy = sensor_data;

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
disp(size(p_recorded))

save("sensor_data_noisy.mat", "p_recorded", "M_0", "sensor_data_noisy", "sensor", "medium", "sensor_data");