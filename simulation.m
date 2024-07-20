addpath('/Users/nontakornbunluesriruang/Downloads/k-wave-toolbox-version-1/k-Wave')

clear

% Set up the computational grid
Nx = 200;   % number of grid points in the x direction
Ny = 150;   % number of grid points in the y direction
dx = 0.1e-3;  % grid point spacing in the x direction [m]
dy = 0.1e-3;  % grid point spacing in the y direction [m]
kgrid = makeGrid(Nx, dx, Ny, dy);

% Define the properties of the medium
medium.sound_speed = 1500;  % [m/s]
medium.density = 1000;     % [kg/m^3]

% Define the source
source.p0 = zeros(Nx, Ny);
source.p0(80, 70) = 1;  % setting the point source

sensor_mask = zeros(Nx, Ny);
sensor_mask(1, 150) = 1; % place sensor at (x, y) Corrdinance
sensor.mask = sensor_mask;


% Run the simulation
sensor_data = kspaceFirstOrder2D(kgrid, medium, source, sensor);

signal_to_noise_ratio = 40;
sensor_data = addNoise(sensor_data, signal_to_noise_ratio, 'peak');

plot(sensor_data)


source_reversed.p_mask = sensor.mask;
source_reversed.p = fliplr(sensor_data);



% Time reversal: use the noisy sensor data as the time-varying pressure source
source_reversed.p_mask = sensor.mask;
source_reversed.p = fliplr(sensor_data);

% Run the time reversal reconstruction
p0_recon = kspaceFirstOrder2D(kgrid, medium, source_reversed, sensor);

figure;
imagesc(kgrid.x_vec * 1e3, kgrid.y_vec * 1e3, p0_recon);
xlabel('x-position [mm]');
ylabel('y-position [mm]');
title('Reconstructed Initial Pressure Distribution');
colorbar;
axis image;


% set the initial model times series to be zero
modelled_time_series = zeros(size(sensor_data));

source.p_mode = 'additive';

difference = modelled_time_series - sensor_data;


% assign the difference time series as an adjoint source
% (see Appendix B in Arridge et al. Inverse Problems 32, 115012 (2016))
time_reversed_data = fliplr(difference);
source.p = [time_reversed_data(:, 1), time_reversed_data(:, 1), time_reversed_data(:, 1:end-1)] + [zeros(size(time_reversed_data(:, 1))), time_reversed_data(:, 1:end-1), 2 * time_reversed_data(:, end)];
	
% send difference through adjoint model
image_update = kspaceFirstOrder2D(kgrid, medium, source, sensor);

figure;
imagesc(kgrid.x_vec * 1e3, kgrid.y_vec * 1e3, image_update);
xlabel('x-position [mm]');
ylabel('y-position [mm]');
title('Reconstructed Initial Pressure Distribution');
colorbar;
axis image;
