import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.gridspec import GridSpec
from pathlib import Path

# --- Step 1: Load and Prepare the Data ---

# Load the data from the CSV file
# Ensure this CSV file is in the same directory as the script
csv_path = Path('data')/('2025-09-20_14-14-10.csv')
data = pd.read_csv(csv_path)

# Clip the data to start 3 seconds before the first non-zero throttle
first_nonzero_idx = data['Normalized accelerator pedal angle'].to_numpy().nonzero()[0][0]
first_nonzero_time = data['Time'].iloc[first_nonzero_idx]
clip_start_time = first_nonzero_time - 3
data = data[data['Time'] >= clip_start_time].reset_index(drop=True)

# Normalize brake pressure to a percentage
max_brake_pressure = data['Current brake pressure'].max()
data['Normalized brake pressure'] = data['Current brake pressure'] / max_brake_pressure * 100

# Interpolate the data to a regular time series (0.04s interval for smooth animation)
regular_time = np.arange(data['Time'].min(), data['Time'].max(), 0.04)
data_interpolated = pd.DataFrame({'Time': regular_time})

# Interpolate all necessary vehicle variables
data_interpolated['Throttle'] = np.interp(regular_time, data['Time'], data['Normalized accelerator pedal angle'])
data_interpolated['Brake'] = np.interp(regular_time, data['Time'], data['Normalized brake pressure'])
data_interpolated['Lat Acc'] = np.interp(regular_time, data['Time'], data['Vehicle lateral acceleration'])
data_interpolated['Long Acc'] = np.interp(regular_time, data['Time'], data['Vehicle longitudinal acceleration'])
data_interpolated['Vehicle Speed'] = np.interp(regular_time, data['Time'], data['Vehicle speed'])
data_interpolated['Engine Speed'] = np.interp(regular_time, data['Time'], data['Engine speed'])


# --- Step 2: Set up the Plots ---

# Create the figure and a grid for the layout
fig = plt.figure(figsize=(16, 2), dpi=100)
gs = GridSpec(1, 4, figure=fig, width_ratios=[1, 1, 1, 0.4])

# Create the four subplots
ax1 = fig.add_subplot(gs[0, 0])  # Speed and RPM
ax2 = fig.add_subplot(gs[0, 1])  # Throttle
ax3 = fig.add_subplot(gs[0, 2])  # Brake
ax4 = fig.add_subplot(gs[0, 3], polar=True)  # G-force

# Configure the Speed and RPM plot (ax1)
ax1.set_ylabel('Speed/RPM')
ax1.set_ylim(0, data_interpolated['Vehicle Speed'].max() * 1.1) # Dynamic ylim
ax1.tick_params(axis='y')
ax1.grid(True, linestyle='--', alpha=0.3)
ax1.set_xticks([]) # Hide x-axis ticks for a cleaner look

# Create a second y-axis on ax1 for the Engine Speed
ax1b = ax1.twinx()
# ax1b.set_ylabel('Engine RPM')
ax1b.set_ylim(0, data_interpolated['Engine Speed'].max() * 1.1) # Dynamic ylim
ax1b.tick_params(axis='y')

# Configure the Throttle plot (ax2)
ax2.set_ylabel('Throttle %')
ax2.set_ylim(0, 110)
ax2.grid(True, linestyle='--', alpha=0.3)

# Configure the Brake plot (ax3)
ax3.set_ylabel('Brake %')
ax3.set_ylim(0, 110)
ax3.grid(True, linestyle='--', alpha=0.3)

# Configure the polar G-force plot (ax4)
ax4.set_ylim(0, 15) # Set radius to 1.5g (assuming units are m/s^2, ~1.5g)
ax4.set_yticklabels([])
ax4.set_theta_zero_location('N') # Zero degrees (forward accel) at the top
ax4.set_theta_direction(1)

# --- Step 3: Create Animation Elements ---

# Create empty line objects for all time-series plots
speed_line, = ax1.plot([], [], 'blue', lw=2)
rpm_line, = ax1b.plot([], [], 'orange', lw=2)
throttle_line, = ax2.plot([], [], 'green', lw=2)
brake_line, = ax3.plot([], [], 'red', lw=2)
acc_dot, = ax4.plot([], [], 'ro') # The moving dot for the g-force plot

# Define the rolling time window for the plots
window_size_seconds = 10
frame_interval = 40  # 40ms between frames corresponds to 25 FPS

# --- Step 4: Define Animation Functions ---

# Initialization function: sets the initial state for the animation
def init():
    speed_line.set_data([], [])
    rpm_line.set_data([], [])
    throttle_line.set_data([], [])
    brake_line.set_data([], [])
    acc_dot.set_data([], [])
    return speed_line, rpm_line, throttle_line, brake_line, acc_dot

# Animation function: this is called for each frame
def animate(i):
    # Determine the current time window
    time_current = data_interpolated['Time'].iloc[i]
    time_window_start = time_current - window_size_seconds
    mask = (data_interpolated['Time'] >= time_window_start) & (data_interpolated['Time'] <= time_current)

    # Update Speed and RPM plot
    ax1.set_xlim(time_window_start, time_current)
    speed_line.set_data(data_interpolated['Time'][mask], data_interpolated['Vehicle Speed'][mask])
    rpm_line.set_data(data_interpolated['Time'][mask], data_interpolated['Engine Speed'][mask])

    # Update throttle plot
    ax2.set_xlim(time_window_start, time_current)
    throttle_line.set_data(data_interpolated['Time'][mask], data_interpolated['Throttle'][mask])

    # Update brake plot
    ax3.set_xlim(time_window_start, time_current)
    brake_line.set_data(data_interpolated['Time'][mask], data_interpolated['Brake'][mask])

    # Update polar G-force plot
    lat_acc = data_interpolated['Lat Acc'].iloc[i]
    long_acc = data_interpolated['Long Acc'].iloc[i]
    r = np.hypot(lat_acc, long_acc)
    theta = np.arctan2(lat_acc, long_acc)
    acc_dot.set_data([theta], [r])

    return speed_line, rpm_line, throttle_line, brake_line, acc_dot

# --- Step 5: Create and Save the Animation ---

# Create the animation object
ani = animation.FuncAnimation(
    fig, animate, frames=len(data_interpolated), init_func=init,
    interval=frame_interval, blit=True, repeat=False
)

# Set up the output path
output_path = Path('video') / (Path(csv_path).stem + '.mp4')
output_path.parent.mkdir(parents=True, exist_ok=True)

print("Creating video... (this may take a while)")

# Adjust layout to prevent labels from overlapping
fig.subplots_adjust(wspace=0.5, hspace=0.1)

# Save the animation as an MP4 file
writer = animation.FFMpegWriter(fps=1 / (frame_interval / 1000.0), bitrate=1800)
ani.save(str(output_path), writer=writer)

print(f"Video saved successfully as '{output_path}'")

# Use plt.show() if you want to see the animation pop up in a window
# plt.tight_layout()
# plt.show()