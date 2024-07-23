import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

# Define the original signal points
x_original = np.array([0, 2, 4, 6, 8, 10])
y_original = np.array([1, 1.5, 2, 2.5, 3, 3.5])

# Create a linear interpolator
linear_interpolator = interp1d(x_original, y_original, kind='linear')

# Define the x values where we want to interpolate
x_values = np.linspace(0, 10, num=100)

# Interpolate the y values
y_values = linear_interpolator(x_values)

# Plot the results
plt.plot(x_original, y_original, 'ro')  # Original points
plt.plot(x_values, y_values, 'b-')  # Interpolated values
plt.xlabel('x')
plt.ylabel('y')
plt.title('Signal Interpolation with 5 Points')
plt.show()