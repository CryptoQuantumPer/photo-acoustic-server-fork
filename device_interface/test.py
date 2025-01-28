# import matplotlib.pyplot as plt
# import numpy as np

# import matplotlib.animation as animation
# from matplotlib.lines import Line2D


# class Scope:
#     def __init__(self, ax, maxt=2, dt=0.02):
#         self.ax = ax
#         self.dt = dt
#         self.maxt = maxt
#         self.tdata = [0]
#         self.ydata = [0]
#         self.line = Line2D(self.tdata, self.ydata)
#         self.ax.add_line(self.line)
#         self.ax.set_ylim(-.1, 1.1)
#         self.ax.set_xlim(0, self.maxt)

#     def update(self, y):
#         lastt = self.tdata[-1]
#         if lastt >= self.tdata[0] + self.maxt:  # reset the arrays
#             self.tdata = [self.tdata[-1]]
#             self.ydata = [self.ydata[-1]]
#             self.ax.set_xlim(self.tdata[0], self.tdata[0] + self.maxt)
#             self.ax.figure.canvas.draw()

#         # This slightly more complex calculation avoids floating-point issues
#         # from just repeatedly adding `self.dt` to the previous value.
#         t = self.tdata[0] + len(self.tdata) * self.dt

#         self.tdata.append(t)
#         self.ydata.append(y)
#         self.line.set_data(self.tdata, self.ydata)
#         return self.line,


# def emitter(p=0.1):
#     """Return a random value in [0, 1) with probability p, else 0."""
#     while True:
#         v = np.random.rand()
#         if v > p:
#             yield 0.
#         else:
#             yield np.random.rand()


# # Fixing random state for reproducibility
# np.random.seed(19680801 // 10)


# fig, ax = plt.subplots()
# scope = Scope(ax)

# # pass a generator in "emitter" to produce data for the update func
# ani = animation.FuncAnimation(fig, scope.update, emitter,
#                               blit=True, save_count=100)

# plt.show()


# import numpy as np
# import matplotlib.pyplot as plt
# from scipy.io import loadmat, savemat
# import os

# index = 0

# loaded_data = loadmat(os.path.join(os.getcwd(), 'device_interface', 'data.mat'))
# loaded_data_ultrasound = loaded_data['ultrasound']
# loaded_data_signal = loaded_data['sig']



# loaded_data_ultrasound_avg_index = np.average(loaded_data_ultrasound[index])
# loaded_data_ultrasound_diff_avg_index = [i-loaded_data_ultrasound_avg_index for i in loaded_data_ultrasound[index]]

# loaded_data_ultrasound_diff_avg_index = loaded_data_ultrasound_diff_avg_index[20000:30000]




# plt.figure(figsize=(8, 4))
# heatmap_data = np.array([loaded_data_ultrasound_diff_avg_index])
# plt.imshow(heatmap_data, cmap="viridis", aspect="auto", extent=[0, len(loaded_data_ultrasound_diff_avg_index), 0, 1])
# plt.colorbar(label="Difference (intervals between peaks)")
# plt.xlabel("Peak Index")
# plt.ylabel("Heatmap Row")
# plt.title("Heatmap of Peak Differences")
# plt.show()



import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Initialize the list that will be updated every second
data_list = [2, 3, 5, 6]

# Create a figure and axis for plotting
fig, ax = plt.subplots()

# Initialize an empty line plot
x_data = list(range(len(data_list)))  # X-axis data (indexes of the list)
y_data = data_list                    # Y-axis data (values in the list)
line, = ax.plot(x_data, y_data, lw=2)

# Set up plot limits
ax.set_xlim(0, 10)  # X-axis range
ax.set_ylim(0, 10)  # Y-axis range

# Function to initialize the plot
def init():
    line.set_data([], [])
    return line,

# Function to update the plot with new data
def update(frame):
    global data_list
    # Simulating the addition of a new element to the list
    data_list.append(np.random.randint(1, 10))  # Replace this with your actual update logic

    # If the list grows too long, remove the oldest value (optional)
    if len(data_list) > 10:
        data_list.pop(0)
    
    # Update the X and Y data for the plot
    x_data = list(range(len(data_list)))  # Update the X-axis values (indexes)
    y_data = data_list                    # Update the Y-axis values (the list data)
    
    line.set_data(x_data, y_data)

    # Adjust x-axis limits dynamically if needed
    if x_data[-1] > ax.get_xlim()[1]:
        ax.set_xlim(0, x_data[-1] + 1)

    return line,

# Create the animation
ani = FuncAnimation(fig, update, frames=np.arange(0, 100), init_func=init, blit=True, interval=1000)

# Show the plot
plt.show()




