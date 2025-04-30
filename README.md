# Driving Data Visualization Tool

This project provides a real-time animation tool to visualize driving data, focusing on throttle, brake, and vehicle acceleration dynamics. The tool reads a CSV log of vehicle sensor data, processes it, and creates a high-resolution animated video that displays key driver input and motion cues over time.

## Features

- **Real-Time Animation** of:
  - Throttle percentage over time
  - Brake pressure over time
  - Polar plot of lateral and longitudinal acceleration
- **Blank Placeholder** for future use (e.g., speed and RPM)
- **Custom Layout** for clean and compact visualizations
- **Automatic Trimming**: Begins 3 seconds before first throttle input
- **Regular Time Interpolation** for smooth animations
- **MP4 Video Output** with adjustable frame rate and layout

## Example Output

- Pop-up matplotlib window for interactive debugging
- `.mp4` video file saved to `video/` directory

## File Structure

```
.
├── data/
│   └── 2025-04-27_15-18-18.csv       # Example input CSV file
├── video/
│   └── 2025-04-27_15-18-18.mp4       # Output video file (auto-generated)
├── visualize.py                      # Main animation script
└── README.md                         # Project documentation
```

## Requirements

- Python 3.8+
- `matplotlib`
- `pandas`
- `numpy`

Install dependencies with:

```bash
pip install matplotlib pandas numpy
```

## Usage

1. Place your driving data CSV in the `data/` directory. The file must include the following columns:
   - `Time`
   - `Normalized accelerator pedal angle`
   - `Current brake pressure`
   - `Vehicle lateral acceleration`
   - `Vehicle longitudinal acceleration`

2. Run the script:

```bash
python visualize.py
```

3. The script will:
   - Clip the data starting 3 seconds before first throttle input
   - Normalize brake pressure
   - Interpolate data to a 20 FPS timeline
   - Display a live animation window
   - Save an `.mp4` file to the `video/` folder

## Notes

- The current layout is designed for 4 plots in a compact 12x2 inch window.
- The speed and RPM panel is reserved for future implementation.
- The polar plot shows lateral (left-right) and longitudinal (forward-backward) acceleration in a compass-style orientation:
  - 0°: Forward
  - 90°: Left
  - 180°: Backward
  - 270°: Right

## License

MIT License
