clear

addpath('/Users/nontakornbunluesriruang/Downloads/k-wave-toolbox-version-1/k-Wave')
addpath('E:/Necleotide Codes/k-wave-toolbox-version-1/k-Wave');

% Clear any existing parallel pools
poolobj = gcp('nocreate');
if ~isempty(poolobj)
    delete(poolobj);
end

% Enable parallel computation
bool_parallel_computation = false;
if bool_parallel_computation == true
    parpool('local'); % Comment out to disable parallel computation
end

% Define grid size and spacing
Nx = 64;
Ny = 64;
Nz = 32;
dx = 0.1e-3;
dy = 0.1e-3;
dz = 0.1e-3;
kgrid = kWaveGrid(Nx, dx, Ny, dy, Nz, dz);

% Define medium properties
medium.sound_speed = 1500 * ones(Nx, Ny, Nz);
medium.density = 1000 * ones(Nx, Ny, Nz);

% Custom function for inpolygon check
function inside = inpolygon_custom(x, y, vertices_x, vertices_y)
    inside = inpolygon(x, y, vertices_x, vertices_y);
end

% Define the prism
x_length = 50;
prism_z_length = 30;
sensor.mask = zeros(Nx, Ny, Nz);
sensor.mask(1, 50, 1) = 1;
vertices_x = [0, 50, 0];
vertices_y = [0, 0, 50];
for z = 1:Nz
    for x = 1:Nx
        for y = 1:Ny
            if inpolygon_custom(x, y, vertices_x, vertices_y)
                medium.density(x, y, z) = 1500;
            end
        end
    end
end

% Define additional optional input arguments
input_args = {'PMLInside', false, ...
              'PMLSize', [0, 0], ...
              'PMLAlpha', 0, ...  % Disable PML by setting PMLAlpha to 0
              'Smooth', false, ...
              'PlotPML', false, ...
              'DataCast', 'gpuArray-single'};  % Use GPU for faster computation


% Generate system matrix with parallel computation
bool_generate_system_matrix = true;
bool_save_system_matrix_k = true;

if bool_generate_system_matrix
    K = cell(x_length * prism_z_length, 1);  % Preallocate cell array
    
    % Use parallel for loop to speed up the computation
    if bool_parallel_computation == true

        input_args = {'PMLInside', false, ...
              'PMLSize', [0, 0], ...
              'PMLAlpha', 0, ...  % Disable PML by setting PMLAlpha to 0
              'Smooth', false, ...
              'PlotPML', false, ...
              'DataCast', 'gpuArray-single'};  % Use GPU for faster computation

        parfor idx = 1:(x_length * prism_z_length)
            [x, z] = ind2sub([x_length, prism_z_length], idx);
            % Define source within parfor loop
            source = struct();
            source.p0 = zeros(Nx, Ny, Nz);
            source.p0(x, 1, z) = 1;
            sensor_data_sys_matrix = kspaceFirstOrder3D(kgrid, medium, source, sensor, input_args{:});
            K{idx} = gather(sensor_data_sys_matrix);  % Gather results from GPU to CPU
        end
    else
        input_args = {'PMLInside', false, ...
              'PMLSize', [0, 0], ...
              'PMLAlpha', 0, ...  % Disable PML by setting PMLAlpha to 0
              'Smooth', false, ...
              'PlotPML', false, ...
              'DataCast', 'single'};
              
        for idx = 1:(x_length * prism_z_length)
            [x, z] = ind2sub([x_length, prism_z_length], idx);
            source.p0 = zeros(Nx, Ny, Nz);
            source.p0(x, 1, z) = 1;
            sensor_data_sys_matrix = kspaceFirstOrder3D(kgrid, medium, source, sensor, input_args{:});
            K{idx} = gather(sensor_data_sys_matrix);
        end
    end

    if bool_save_system_matrix_k
        save('system_matrix.mat', 'K');
        disp("Successfully saved system_matrix data")
    end
end

% Load binary image for inputting as sensor data
binary_image = imread('vascular.png');
binary_image = imbinarize(binary_image);
binary_image = imresize(binary_image, [Nx, Ny]);  % Resize the image to match the grid

% Define source
source = struct();
source.p0 = zeros(Nx, Ny, Nz);

% Define the position of the binary image in the grid
center_y = 10;
source.p0(:, center_y, :) = permute(repmat(binary_image, [1, 1, Nz]), [1, 3, 2]);

% Run the forward simulation
sensor_data = kspaceFirstOrder3D(kgrid, medium, source, sensor, input_args{:});

% Plot the simulated sensor data
figure;
plot(sensor_data);
xlabel('Time Index');
ylabel('Pressure');
title('Simulated Sensor Data');

% Save data
save("sensor_data_noisy.mat", "sensor_data", "medium", "sensor");

disp('Simulation completed successfully');