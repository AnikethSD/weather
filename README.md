# Weather Data Visualization

A repository for various weather and climate data visualization projects.

## Projects

### 1. India Rainfall Visualization (`/rain`)
An interactive web-based application to visualize historical annual precipitation data for India (1991 - 2023).

- **Features:** Interactive heatmap, year selector, state-wise focus with masking, and relative intensity scaling.
- **Data Source:** [IPED Mean Source Data](https://zenodo.org/records/15618220)
- **Tech Stack:** Python (xarray, pandas), Leaflet.js

For more details, see the [Rain Project README](rain/README.md).

## Setup

1. **Virtual Environment:**
   It is recommended to use a virtual environment.
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Dependencies:**
   Install the required Python packages.
   ```bash
   pip install -r rain/requirements.txt
   ```

## License
This project is licensed under the terms of the LICENSE file included in the root directory.
