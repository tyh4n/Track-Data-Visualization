import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.gridspec import GridSpec
from pathlib import Path

# Load the data
csv_path = Path('data') / ('2025-04-27_15-18-18.csv')
data = pd.read_csv(csv_path)

# Clip the data to start 3 seconds before the first non-zero throttle
first_nonzero_idx = data['Normalized accelerator pedal angle'].to_numpy().nonzero()[0][0]
first_nonzero_time = data['Time'].iloc[first_nonzero_idx]
clip_start_time = first_nonzero_time - 3
data = data[data['Time'] >= clip_start_time].reset_index(drop=True)

# Normalize brake pressure
max_brake_pressure = data['Current brake pressure'].max()
data['Normalized brake pressure'] = data['Current brake pressure'] / max_brake_pressure * 100

# Interpolate the data to a regular time series (0.1s interval)
regular_time = np.arange(data['Time'].min(), data['Time'].max(), 0.04)  # 0.05s regular time
data_interpolated = pd.DataFrame({'Time': regular_time})

# Interpolate throttle, brake pressure, and other variables to regular time
data_interpolated['Throttle'] = np.interp(regular_time, data['Time'], data['Normalized accelerator pedal angle'])
data_interpolated['Brake'] = np.interp(regular_time, data['Time'], data['Normalized brake pressure'])
data_interpolated['Lat Acc'] = np.interp(regular_time, data['Time'], data['Vehicle lateral acceleration'])
data_interpolated['Long Acc'] = np.interp(regular_time, data['Time'], data['Vehicle longitudinal acceleration'])

# Create figure with new size and layout
fig = plt.figure(figsize=(16, 2), dpi=100)
gs = GridSpec(1, 4, figure=fig, width_ratios=[1, 1, 1, 0.4])

# Create subplots
ax1 = fig.add_subplot(gs[0, 0])  # Speed and RPM placeholder (blank for future use)
ax2 = fig.add_subplot(gs[0, 1])  # Throttle plot (time series)
ax3 = fig.add_subplot(gs[0, 2])  # Brake plot (time series)
ax4 = fig.add_subplot(gs[0, 3], polar=True)  # Polar acceleration plot

# Set up plots
ax1.set_ylabel('Speed, RPM')
ax1.set_ylim(0, 110)
ax1.set_yticks([0, 50, 100])
ax1.set_xticks([])  # Remove x ticks
ax1.grid(True, linestyle='--', alpha=0.3)

ax2.set_ylabel('Throttle%')
ax2.set_ylim(0, 110)
ax2.grid(True, linestyle='--', alpha=0.3)

ax3.set_ylabel('Brake%')
ax3.set_ylim(0, 110)
ax3.grid(True, linestyle='--', alpha=0.3)

ax4.set_ylim(0, 15)  # Acceleration magnitude up to 15 m/s
ax4.set_yticklabels([])  # Remove polar plot labels
ax4.set_theta_zero_location('N')  # Set zero degree to the top (North)
ax4.set_theta_direction(1)  # Counterclockwise direction

# Create lines for throttle and brake (time series)
throttle_line, = ax2.plot([], [], 'g-', lw=2)
brake_line, = ax3.plot([], [], 'r-', lw=2)

# Create a moving dot in polar plot
acc_dot, = ax4.plot([], [], 'ro')

# Initialize animation
window_size_seconds = 10  # rolling window of 10s

# Set real-time playback
frame_interval = 100  # Set a fixed frame interval for real-time animation (100 ms per frame)

# Function to initialize the plot
def init():
    throttle_line.set_data([], [])
    brake_line.set_data([], [])
    acc_dot.set_data([], [])
    return throttle_line, brake_line, acc_dot

# Animation function
def animate(i):
    if i == 0:
        return init()

    # Time handling for the interpolated data
    time_current = data_interpolated['Time'].iloc[i]
    time_window_start = time_current - 10  # current at 100% position

    # Filter window
    mask = (data_interpolated['Time'] >= time_window_start) & (data_interpolated['Time'] <= time_window_start + window_size_seconds)

    # Update throttle plot
    ax2.set_xlim(time_window_start, time_window_start + window_size_seconds)
    throttle_line.set_data(data_interpolated['Time'][mask], data_interpolated['Throttle'][mask])

    # Update brake plot
    ax3.set_xlim(time_window_start, time_window_start + window_size_seconds)
    brake_line.set_data(data_interpolated['Time'][mask], data_interpolated['Brake'][mask])

    # Update polar plot
    lat_acc = data_interpolated['Lat Acc'].iloc[i]
    long_acc = data_interpolated['Long Acc'].iloc[i]
    
    # Calculate polar coordinates
    r = np.hypot(lat_acc, long_acc)
    theta = np.arctan2(lat_acc, long_acc)
    
    acc_dot.set_data([theta], [r])

    return throttle_line, brake_line, acc_dot

# Create animation
ani = animation.FuncAnimation(
    fig, animate, frames=len(data_interpolated), init_func=init,
    interval=frame_interval, blit=False, repeat=False
)

# Save animation
output_path = Path('video') / (csv_path.stem + '.mp4')
output_path.parent.mkdir(parents=True, exist_ok=True)

print("Creating video... (this may take a while)")

# Adjust padding manually for video export (to prevent overlap)
fig.subplots_adjust(wspace=0.5, hspace=0.1)  # Adjust spacing between subplots

# Create video writer with custom FPS and bitrate
writer = animation.FFMpegWriter(fps=25, bitrate=1800)
ani.save(str(output_path), writer=writer)
print(f"Video saved as '{output_path}'")

# Use tight_layout for pop-up window
plt.tight_layout()
plt.show()
