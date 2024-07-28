clear
addpath('/Users/nontakornbunluesriruang/Downloads/k-wave-toolbox-version-1/k-Wave')

% Set up the computational grid
Nx = 100;  % number of grid points in the x direction
Ny = 100;  % number of grid points in the y direction
Nz = 100;  % number of grid points in the z direction
dx = 0.5e-3;  % grid point spacing in the x direction [m]
dy = 0.5e-3;  % grid point spacing in the y direction [m]
dz = 0.5e-3;  % grid point spacing in the z direction [m]
kgrid = kWaveGrid(Nx, dx, Ny, dy, Nz, dz);

% Define the medium properties
medium.sound_speed = 1500 * ones(Nx, Ny, Nz);  % sound speed [m/s]
medium.density = 1000 * ones(Nx, Ny, Nz);      % density [kg/m^3]

% Create the source mask for the triangular prism
source.p0 = zeros(Nx, Ny, Nz);

% Define the vertices of the triangular prism (in grid points)
vertices_x = [25, 75, 25];
vertices_y = [25, 25, 75];
vertices_z = [25, 25, 75];

% Plot the initial shape of the triangular prism
figure;
fill3(vertices_x, vertices_y, vertices_z, 'r', 'FaceAlpha', 0.5);
axis equal;
xlabel('x [grid points]');
ylabel('y [grid points]');
zlabel('z [grid points]');
title('Initial Shape of the Triangular Prism');
grid on;

% Fill the triangular prism
for z = min(vertices_z):max(vertices_z)
    for y = min(vertices_y):max(vertices_y)
        for x = min(vertices_x):max(vertices_x)
            if inpolygon(x, y, vertices_x, vertices_y)
                source.p0(x, y, z) = 1;
            end
        end
    end
end

% Define the sensor at a single point at (0, 0) and the top part of the triangle
sensor_x = round(Nx / 2);  % center of the grid in x
sensor_y = round(Ny / 2);  % center of the grid in y
sensor_z = max(vertices_z);  % top part of the triangle
sensor.mask = zeros(Nx, Ny, Nz);
sensor.mask(sensor_x, sensor_y, sensor_z) = 1;

% Run the simulation
sensor.record = {'p', 'p_final'}; % record the pressure and final pressure

input_args = {'PMLSize', 10, 'PMLAlpha', 2, 'DataCast', 'single'};
sensor_data = kspaceFirstOrder3D(kgrid, medium, source, sensor, input_args{:});

% Visualize the pressure distribution
p = sensor_data.p_final;
figure;
isosurface(p, 0.5);
axis equal;
xlabel('x [mm]');
ylabel('y [mm]');
zlabel('z [mm]');
title('Pressure Distribution of the Triangular Prism');

% Plot the triangular prism outline
hold on;
plot3(vertices_x, vertices_y, vertices_z, 'k', 'LineWidth', 2);
fill3(vertices_x, vertices_y, vertices_z, 'r', 'FaceAlpha', 0.3);
hold off;

% Plot the sensor data
figure;
plot(sensor_data.p);
xlabel('Time [s]');
ylabel('Pressure [Pa]');
title('Sensor Data at (0, 0, top part of triangle)');
grid on;