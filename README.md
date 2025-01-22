
# Traffic Light Simulation in Urban Networks

This repository contains two Python scripts (`tl1.py` and `tl2.py`) that simulate traffic flow in urban networks using OpenStreetMap (OSM) data and visualizations with Pygame and Matplotlib. These scripts analyze traffic density and demonstrate the impact of traffic lights on urban traffic management.

---

## Scripts Overview

### `tl1.py`

**Purpose**: Simulates a traffic network with agents (vehicles) navigating a city without traffic lights and evaluates traffic density. Traffic lights are later dynamically added to high-density areas, and the improvement in traffic efficiency is measured.

#### Key Features:
- Fetches road network data using OSMnx for a specified radius around a central location.
- Dynamically adds traffic lights to nodes with high traffic density based on initial simulation results.
- Compares traffic flow efficiency with and without traffic lights.
- Visualizes the road network, agents, and traffic lights in real-time using Pygame.

---

### `tl2.py`

**Purpose**: Simulates traffic in a selected area with and without traffic lights using animation and visualizes the impact of traffic lights over time.

#### Key Features:
- Utilizes Matplotlib for creating animations to showcase vehicle movements and traffic density dynamically.
- Introduces agents (vehicles) with different speeds and behaviors depending on the presence of traffic lights.
- Adds traffic lights at the busiest nodes based on node degrees.
- Compares total traffic density over time with traffic lights versus without traffic lights.

---

## Dependencies

Both scripts require the following Python libraries:

- `osmnx`
- `networkx`
- `matplotlib`
- `pygame`

Install the dependencies using the following command:

```bash
pip install osmnx networkx matplotlib pygame
```

---

## Usage

1. **Run `tl1.py`**:
   ```bash
   python tl1.py
   ```
   - This script uses Pygame to visualize the simulation in real-time.
   - Results include a comparison of traffic density before and after adding traffic lights.

2. **Run `tl2.py`**:
   ```bash
   python tl2.py
   ```
   - This script uses Matplotlib to animate traffic movements and displays a graph comparing traffic density over time.

---

## Results

- **`tl1.py`**: Provides real-time simulation and traffic density improvement calculations with traffic lights.
- **`tl2.py`**: Animates traffic flows and visualizes traffic density trends, highlighting the effectiveness of traffic lights.

---

## Future Work

- Extend simulations to support multiple traffic signal states (e.g., yellow light).
- Optimize agent behaviors using reinforcement learning for better traffic management.
- Simulate real-world scenarios like accidents or roadblocks.

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

## Contributions

Feel free to open issues or submit pull requests for improvements and new features!
