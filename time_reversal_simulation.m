% time_reversal_reconstruction.m
addpath('/Users/nontakornbunluesriruang/Downloads/k-wave-toolbox-version-1/k-Wave')

% Load the noisy sensor data
load('sensor_data_noisy.mat', 'sensor_data_noisy', 'kgrid', 'medium', 'sensor', 'input_args');

% Time reversal: use the noisy sensor data as the time-varying pressure source (p)
source_reversed.p_mask = sensor.mask;
source_reversed.p = fliplr(sensor_data_noisy);

% Run the time reversal reconstruction with input_args
p0_recon = kspaceFirstOrder2D(kgrid, medium, source_reversed, sensor);

% Plot the reconstructed initial pressure distribution
figure;
imagesc(kgrid.x_vec * 1e3, kgrid.y_vec * 1e3, p0_recon);
xlabel('x-position [mm]');
ylabel('y-position [mm]');
title('Reconstructed Initial Pressure Distribution');
colorbar;
axis image;

% Find the position of the maximum value in the reconstructed initial pressure
[max_val, max_idx] = max(p0_recon(:));
[max_y, max_x] = ind2sub(size(p0_recon), max_idx);  % Note the order of indices (y, x)

disp([max_y, max_x]);

% Convert grid indices to physical coordinates
% initial_source_position = [kgrid.x_vec(max_x), kgrid.y_vec(max_y)] * 1e3; % [mm]
% disp(['Estimated initial source position: (', num2str(initial_source_position(1)), ', ', num2str(initial_source_position(2)), ') mm']);
