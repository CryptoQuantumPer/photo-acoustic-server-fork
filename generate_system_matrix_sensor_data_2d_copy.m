clear

tic;
addpath('E:/Necleotide Codes/k-wave-toolbox-version-1/k-Wave');
poolobj = gcp('nocreate');
if ~isempty(poolobj)
    delete(poolobj);
end
bool_parallel_computation = false;
if bool_parallel_computation == true
    parpool('local'); % comment if disable parallel computation
end

% Set up the computational grid
Nx = 160;   % number of grid points in the x direction
Ny = 120;   % number of grid points in the y direction
% 25 MHz grid spacing settings
dx = 3e-5; 
dy = 3e-5;

% Define the properties of the medium
medium.sound_speed = 1500;  % [m/s]
medium.density = 1000;     % [kg/m^3]

kgrid = makeGrid(Nx, dx, Ny, dy);

% Define the sensor masks
sensor.mask = zeros(Nx, Ny);
sensor.mask(1, 120) = 1; % place sensor at (x, y) coordinates

% Define additional optional input arguments
input_args = {'PMLInside', false, ...
              'PMLSize', [0, 0], ...
              'PMLAlpha', 0, ...  % Disable PML by setting PMLAlpha to 0
              'Smooth', false, ...
              'PlotPML', false, ...
              'DataCast', 'gpuArray-single'};  % Use GPU for faster computation

% Number of steps and preallocate K matrix
bool_generate_system_matrix = true;
bool_save_system_matrix_k = true;

if bool_generate_system_matrix == true
    K = cell(Nx * Ny, 1);  % Preallocate cell array
    
    % Use parallel for loop to speed up the computation
    parfor idx = 1:(Nx * Ny)
        [n, m] = ind2sub([Nx, Ny], idx);
        fprintf('x: %d, y: %d\n', n, m);
        source_p0 = gpuArray.zeros(Nx, Ny, 'single');
        source_p0(n, m) = 1;
        k_sensor_output = kspaceFirstOrder2D(kgrid, medium, struct('p0', source_p0), sensor, input_args{:});
        K{idx} = gather(k_sensor_output);  % Gather results from GPU to CPU
    end

    if bool_save_system_matrix_k == true
        save('system_matrix.mat', 'K');
        disp("successfuly save system_matrix data")
    end
end

% load binary Image for inputting as sensor data
source.p0 = zeros(Nx, Ny);
binary_image = imread('vascular.png');
binary_image = im2bw(binary_image);
binary_image = imresize(binary_image, [Nx, Ny]);  % Resize the image to match the grid

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

% Plot the noisy sensor data
figure;
plot(sensor_data);
xlabel('Time Index');
ylabel('Pressure');
title('Simulated Sensor Data');

% Calculate mode shapes
[X, Y] = meshgrid((0:Nx-1) * dx, (0:Ny-1) * dy);
num_modes = 10;
M_0 = zeros(Nx * Ny, num_modes);
for m = 1:num_modes
    phi_m = sin(m * pi * X / (Nx * dx)) .* sin(m * pi * Y / (Ny * dy));
    M_0(:, m) = reshape(phi_m, [], 1);  % Reshape mode shape to column vector
end

% Reshape recorded data to match the number of spatial points
p_recorded = reshape(sensor_data, [], 1);  % Reshape to a vector

% Save data
save("sensor_data_noisy.mat", "p_recorded", "M_0", "sensor_data", "sensor", "medium", "sensor_data");

elapsedTime = toc;
fprintf('Total runtime: %.2f seconds\n', elapsedTime);
