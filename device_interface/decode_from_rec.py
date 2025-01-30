import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

# File path (update as needed)
# os.path.join(os.getcwd(), 'device_interface', 'extraction.0.drc')
file_path = os.path.join(os.getcwd(), 'device_interface', 'extraction.0.drc')
csv_output_path = os.path.join(os.getcwd(), 'device_interface', 'hantek_waveform.csv')

# Oscilloscope settings
volts_per_div = 500e-3  # 100mV per division
time_per_div = 50e-6  # 5 microseconds per division
adc_offset = 128  # Midpoint for signed conversion (assuming 8-bit unsigned)
adc_scale = volts_per_div / 128  # Approximate scale factor

# Read the binary file as 8-bit unsigned integer values
with open(file_path, "rb") as f:
    binary_data = f.read()

# Convert binary data to an array of ADC values (uint8)
adc_values_uint8 = np.frombuffer(binary_data, dtype=np.uint8)


# Convert ADC values to voltage
voltages = (adc_values_uint8 - adc_offset) * adc_scale

plt.plot(voltages)
plt.show()

# Generate time values based on the oscilloscope sampling interval
num_samples = len(voltages)
time_values = np.linspace(0, num_samples * time_per_div, num_samples)

# Create a DataFrame for easy saving and analysis
df = pd.DataFrame({"Time (s)": time_values, "Voltage (V)": voltages})

# Save to CSV file
df.to_csv(csv_output_path, index=False)

# Plot the extracted waveform (first 1000 samples for visualization)
plt.figure(figsize=(10, 4))
plt.plot(time_values[:1000], voltages[:1000], label="Extracted Waveform")
plt.title("Extracted Waveform from Hantek 6254BE")
plt.xlabel("Time (s)")
plt.ylabel("Voltage (V)")
plt.grid()
plt.legend()
plt.show()

# Output file path
print(f"Waveform data saved to: {csv_output_path}")
