Nx = 160;
Ny = 120;

binary_image = imread('vascular.png');
binary_image = imbinarize(binary_image);
binary_image = imresize(binary_image, [Nx, Ny]);  % Resize the image to match the grid

% sensor position at 120, 1
sensor.mask = zeros(Nx, Ny);
sensor.mask(120, 1) = 1;

% create A system matrix
K = {};
for m = 1:Nx
    for n = 1:Ny
        source.mask = binary_image(Nx, Ny);
        % simluate the behavior
        % k_sensor_output = kspaceFirstOrder2D()
        K = [K, k_sensor_output];
    end
end


disp(binary_image(120,1));