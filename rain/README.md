# India Rainfall Visualization Project

This project provides an interactive heatmap visualization of annual precipitation data for India across multiple decades. It leverages climate data to provide insights into rainfall patterns at both national and state levels.

## Features

- **Interactive Heatmap:** Visualizes precipitation intensity across the Indian subcontinent using a vibrant color gradient.
- **Dynamic Year Filtering:** Seamlessly navigate through annual data from 1991 to 2023 using a dropdown selector or quick-navigation arrows.
- **State-Wise Focus:** Search for any Indian state to automatically zoom in and mask out other regions, allowing for dedicated regional analysis.
- **Relative Scaling:** Rainfall intensity is normalized per year to highlight relative patterns and ensure consistent visualization across both dry and wet years.
- **Clean UI:** Includes a light-themed interface with an informative legend and title overlays.

## Tech Stack

- **Data Processing:** Python ([xarray](https://docs.xarray.dev/), [pandas](https://pandas.pydata.org/), [numpy](https://numpy.org/))
- **Visualization:** [Leaflet.js](https://leafletjs.com/) with [Leaflet.heat](https://github.com/Leaflet/Leaflet.heat)
- **Basemaps:** [CartoDB Positron](https://carto.com/basemaps/)
- **Regional Data:** GeoJSON boundaries for Indian States

## Directory Structure

- `IPED_Mean_Source_Data/`: Contains the raw NetCDF data files for each year.
- `site/`: The output directory for generated JSON data and the interactive HTML map.
- `generate_map.py`: The main processing script that converts raw data into web-ready formats.

## Getting Started

1. **Process the Data:**
   Run the main script to generate the required JSON datasets and the interactive HTML map:
   ```bash
   python3 rain/generate_map.py
   ```

2. **Launch the Server:**
   Start a local HTTP server to view the interactive map:
   ```bash
   python3 -m http.server 8000
   ```

3. **View the Map:**
   Open your browser and navigate to:
   `http://localhost:8000/rain/site/map.html`

## Data Source
The precipitation data is derived from the **IPED Mean** dataset, covering historical rainfall records for India. Available at: [https://zenodo.org/records/15618220](https://zenodo.org/records/15618220)
