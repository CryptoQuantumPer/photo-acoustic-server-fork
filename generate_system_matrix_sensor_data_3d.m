clear
addpath('/Users/nontakornbunluesriruang/Downloads/k-wave-toolbox-version-1/k-Wave')

poolobj = gcp('nocreate');
if ~isempty(poolobj)
    delete(poolobj);
end
bool_parallel_computation = true;
if bool_parallel_computation == true
    parpool('local'); % comment if disable parallel computation
end

Nx = 64;
Ny = 64;
Nz = 32;
dx = 0.1e-3;
dy = 0.1e-3;
dz = 0.1e-3;
kgrid = kWaveGrid(Nx, dx, Ny, dy, Nz, dz);

medium.sound_speed = 1500 * ones(Nx, Ny, Nz);
medium.density = 1000 * ones(Nx, Ny, Nz);


function inside = inpolygon_custom(x, y, vertices_x, vertices_y)
    inside = inpolygon(x, y, vertices_x, vertices_y);
end


x_length = 50;
y_length = 50;
prism_z_length = 30;
sensor.mask = zeros(Nx, Ny, Nz);
sensor.mask(1, 50, 1) = 1;
vertices_x = [0, 50, 0];
vertices_y = [0, 0, 50];
for  z = 1:Nz
    for x = 1:Nx
        for y = 1:Ny
            if inpolygon_custom(x, y, vertices_x, vertices_y)
                medium.density(x, y, z) = 1500;
            end
        end
    end
end


% loop to genenerate system_matrix
input_args = {'PMLInside', false, ...
              'PMLSize', [0, 0], ...
              'PMLAlpha', 0, ...  % Disable PML by setting PMLAlpha to 0
              'Smooth', false, ...
              'PlotPML', false,};


bool_generate_system_matrix = true;
bool_save_system_matrix_k = true;



if bool_generate_system_matrix
    K = cell(x_length * prism_z_length, 1);  % Preallocate cell array
    
    % Use parallel for loop to speed up the computation
    parfor idx = 1:(x_length * prism_z_length)
        [x, z] = ind2sub([x_length, prism_z_length], idx);
        source.p0 = zeros(Nx, Ny, Nz);
        source.p0(x, 1, z) = 1;
        sensor_data_sys_matrix = kspaceFirstOrder3D(kgrid, medium, source, sensor, input_args{:});
        K{idx} = gather(sensor_data_sys_matrix);  % Gather results from GPU to CPU
    end

    if bool_save_system_matrix_k
        save('system_matrix.mat', 'K');
        disp("Successfully saved system_matrix data")
    end
end



% if bool_generate_system_matrix == true
%     if bool_parallel_computation == true
%         for x = 1: x_length
%             for z = 1:prism_z_length
%                 source.p0 = zeros(Nx, Ny, Nz);
%                 source.p0(x, 1, z) = 1;
%                 sensor_data_sys_matrix = kspaceFirstOrder3D(kgrid, medium, source, sensor, input_args{:});
%             end
%         end    
%         if bool_save_system_matrix_k == true
%             save('system_matrix.mat', 'K');
%         end
%     else
%         for x = 1: x_length
%             for z = 1:prism_z_length
%                 source.p0 = zeros(Nx, Ny, Nz);
%                 source.p0(x, 1, z) = 10;
%                 sensor_data_sys_matrix = kspaceFirstOrder3D(kgrid, medium, source, sensor, input_args{:});
%                 plot(sensor_data_sys_matrix);
%                 xlabel('Time Index');
%                 ylabel('Pressure');
%                 title('Simulated Noisy Sensor Data');
%             end
%         end   
%         if bool_save_system_matrix_k == true
%             save('system_matrix.mat', 'K');
%         end 
%     end
% end







% source.p0 = zeros(Nx, Ny, Nz);

% for z = min(vertices_z):max(vertices_z)
%     for y = min(vertices_y):max(vertices_y)
%         for x = min(vertices_x):max(vertices_x)
%             if inpolygon(x, y, vertices_x, vertices_y)
%                 source.p0(x, y, z) = 1;
%             end
%         end
%     end
% end

% sensor_x = round(Nx / 2);
% sensor_y = round(Ny / 2);
% sensor_z = max(vertices_z);
% sensor.mask = zeros(Nx, Ny, Nz);
% sensor.mask(sensor_x, sensor_y, sensor_z) = 1;

sensor.record = {'p', 'p_final'};
input_args = {'PMLSize', 10, 'PMLAlpha', 2, 'DataCast', 'single'};
sensor_data = kspaceFirstOrder3D(kgrid, medium, source, sensor, input_args{:});

p = sensor_data.p_final;
figure;
isosurface(p, 0.5);
axis equal;
xlabel('x');
ylabel('y');
zlabel('z');
title('Pressure Distribution of the Triangular Prism');

