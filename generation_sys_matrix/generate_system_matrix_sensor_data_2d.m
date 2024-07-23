clear

addpath('/Users/nontakornbunluesriruang/Downloads/k-wave-toolbox-version-1/k-Wave')

poolobj = gcp('nocreate');
if ~isempty(poolobj)
    delete(poolobj);
end
bool_parallel_computation = false;
if bool_parallel_computation == true
    parpool('local');
end

Nx = 160;
Ny = 120;
dx = 3e-5;
dy = 3e-5;
medium.sound_speed = 1500;
medium.density = 1000;
kgrid = makeGrid(Nx, dx, Ny, dy);
sensor.mask = zeros(Nx, Ny);
sensor.mask(1, 120) = 1;


input_args = {'PMLInside', false, ...
    'PMLSize', [0, 0], ...
    'PMLAlpha', 0, ...  % Disable PML by setting PMLAlpha to 0
    'Smooth', false, ...
    'PlotPML', false};  % Use GPU for faster computation

% false : if skip the generation of system matrix
num_xy_steps_pixel = 10;
bool_generate_system_matrix = true;
bool_save_system_matrix_k = true;
if bool_generate_system_matrix == true
    K = {};
    key_points = {};
    n_pixel = 0;
    for m = 1:num_xy_steps_pixel:Ny
        for n = 1:num_xy_steps_pixel:Nx
            fprintf('x: %d, y: %d\n', n, m);
            source.p0 = zeros(Nx, Ny); 
            source.p0(n, m) = 1;
            k_sensor_output = kspaceFirstOrder2D(kgrid, medium, source, sensor, input_args{:});
            disp(size(k_sensor_output));
            K = [K, k_sensor_output];
            key_points = [key_points, [n, m]];
        end
    end
    if bool_save_system_matrix_k == true
        save('system_matrix.mat', 'K', 'key_points');
    end
end
