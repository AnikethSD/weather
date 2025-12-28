import xarray as xr
import pandas as pd
import numpy as np
import json
import glob
import os

def generate_interactive_map():
    # 1. Find all files
    files = sorted(glob.glob('rain/IPED_Mean_Source_Data/IPED_mean_*.nc'))
    years = []
    
    file_year_map = {}

    for f in files:
        year = f.split('_')[-1].split('.')[0]
        years.append(year)
        file_year_map[year] = f
    
    # 2. Process each file
    print("Generating JSON data for each year (Relative Normalization)...")
    for year in years:
        f = file_year_map[year]
        try:
            ds = xr.open_dataset(f)
            mean_ds = ds.pcp.mean(dim='time')
            df = mean_ds.to_dataframe().reset_index()
            df = df.dropna(subset=['pcp'])
            
            # Calculate local max for relative scaling
            local_max = df['pcp'].quantile(0.98)
            
            # Normalize
            df['intensity'] = df['pcp'] / local_max
            df['intensity'] = df['intensity'].clip(upper=1.0)
            
            # [lat, lon, intensity]
            data_points = df[['lat', 'lon', 'intensity']].values.tolist()
            
            out_file = f'rain/site/heatmap_data_{year}.json'
            with open(out_file, 'w') as jf:
                json.dump(data_points, jf)
            
            print(f"Saved {out_file}")
            ds.close()
        except Exception as e:
            print(f"Error processing {year}: {e}")

    # 3. Generate HTML
    # We pass the list of years to the HTML to populate the dropdown
    years_json = json.dumps(years)

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>India Rain Heatmap</title>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet.heat/0.2.0/leaflet-heat.js"></script>
        
        <style>
            html, body {{
                height: 100%;
                margin: 0;
                font-family: Arial, sans-serif;
            }}
            #map {{
                width: 100%;
                height: 100%;
                background: white;
            }}
            .info {{
                padding: 6px 8px;
                font: 14px/16px Arial, Helvetica, sans-serif;
                background: rgba(255,255,255,0.9);
                box-shadow: 0 0 15px rgba(0,0,0,0.2);
                border-radius: 5px;
                border: 1px solid #ccc;
            }}
            .info h4 {{
                margin: 0 0 5px;
                color: #333;
            }}
            .legend {{
                line-height: 18px;
                color: #333;
            }}
            .legend i {{
                width: 18px;
                height: 18px;
                float: left;
                margin-right: 8px;
                opacity: 0.8;
            }}
            .search-control {{
                background: white;
                padding: 10px;
                border-radius: 5px;
                box-shadow: 0 0 15px rgba(0,0,0,0.2);
                border: 1px solid #ccc;
                margin-bottom: 10px;
            }}
            .search-control input, .search-control select {{
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 3px;
                font-size: 14px;
            }}
            .search-control input {{
                width: 200px;
            }}
            .year-control {{
                display: flex;
                align-items: center;
                gap: 5px;
            }}
            .year-btn {{
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 5px 10px;
                cursor: pointer;
                font-size: 14px;
            }}
            .year-btn:hover {{
                background-color: #e0e0e0;
            }}
            .controls-container {{
                background: white;
                padding: 10px;
                border-radius: 5px;
                box-shadow: 0 0 15px rgba(0,0,0,0.2);
                border: 1px solid #ccc;
            }}
            .reset-btn {{
                margin-top: 5px;
                width: 100%;
                padding: 5px;
                background-color: #f8d7da;
                border: 1px solid #f5c6cb;
                color: #721c24;
                border-radius: 3px;
                cursor: pointer;
                font-size: 13px;
            }}
            .reset-btn:hover {{
                background-color: #f1b0b7;
            }}
        </style>
    </head>
    <body>
        <div id="map"></div>
        <script>
            var map = L.map('map').setView([22.0, 78.0], 5);

            // Light Basemap (Positron)
            L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
                subdomains: 'abcd',
                maxZoom: 20
            }}).addTo(map);

            var geoJsonLayer;
            var maskLayer;
            var statesData = {{}}; // Store layer by state name
            var allFeatures = [];

            // Combined Controls (Search + Year)
            var controls = L.control({{position: 'topleft'}});
            controls.onAdd = function(map) {{
                var div = L.DomUtil.create('div', 'controls-container');
                
                // Search
                var searchDiv = document.createElement('div');
                searchDiv.style.marginBottom = '10px';
                searchDiv.innerHTML = '<input type="text" id="stateSearch" list="stateList" placeholder="Search State..."><datalist id="stateList"></datalist>';
                div.appendChild(searchDiv);

                // Year Filter
                var yearDiv = document.createElement('div');
                yearDiv.className = 'year-control';
                
                var prevBtn = '<button id="prevYear" class="year-btn">&lt;</button>';
                var nextBtn = '<button id="nextYear" class="year-btn">&gt;</button>';
                
                var yearSelect = '<select id="yearSelect">';
                var years = {years_json};
                years.forEach(function(y) {{
                    yearSelect += '<option value="' + y + '">' + y + '</option>';
                }});
                yearSelect += '</select>';
                
                yearDiv.innerHTML = '<strong>Year: </strong>' + prevBtn + yearSelect + nextBtn;
                div.appendChild(yearDiv);

                // Reset Button
                var resetBtn = document.createElement('button');
                resetBtn.className = 'reset-btn';
                resetBtn.innerText = 'Reset to India';
                resetBtn.id = 'resetView';
                div.appendChild(resetBtn);

                L.DomEvent.disableClickPropagation(div);
                return div;
            }};
            controls.addTo(map);

            // Helper to swap [lon, lat] to [lat, lon]
            function swapCoords(coords) {{
                if (typeof coords[0] === 'number') {{
                    return [coords[1], coords[0]];
                }}
                return coords.map(swapCoords);
            }}

            function applyMask(features) {{
                if (maskLayer) {{
                    map.removeLayer(maskLayer);
                }}

                var worldPolygon = [
                    [90, -180],
                    [90, 180],
                    [-90, 180],
                    [-90, -180]
                ];

                var maskHoles = [];
                features.forEach(function(feature) {{
                    var coords = feature.geometry.coordinates;
                    var type = feature.geometry.type;
                    if (type === 'Polygon') {{
                        maskHoles.push(swapCoords(coords[0]));
                    }} else if (type === 'MultiPolygon') {{
                        for (var i = 0; i < coords.length; i++) {{
                            maskHoles.push(swapCoords(coords[i][0]));
                        }}
                    }}
                }});

                maskLayer = L.polygon([worldPolygon].concat(maskHoles), {{
                    color: 'transparent',
                    fillColor: '#ffffff',
                    fillOpacity: 1.0, 
                    stroke: false
                }}).addTo(map);
            }}

            // Load GeoJSON and Populate Search
            fetch('https://raw.githubusercontent.com/geohacker/india/master/state/india_telengana.geojson')
                .then(res => res.json())
                .then(data => {{
                    var datalist = document.getElementById('stateList');
                    allFeatures = data.features;

                    geoJsonLayer = L.geoJSON(data, {{
                        onEachFeature: function(feature, layer) {{
                            var name = feature.properties.NAME_1 || feature.properties.name; 
                            if (name) {{
                                statesData[name] = layer;
                                var option = document.createElement('option');
                                option.value = name;
                                datalist.appendChild(option);
                            }}
                        }}
                    }});

                    // Apply initial mask for all of India
                    applyMask(allFeatures);
                }})
                .catch(err => console.error("Error loading GeoJSON:", err));

            // Setup Event Listeners
            setTimeout(function() {{
                // Search Event
                document.getElementById('stateSearch').addEventListener('change', function(e) {{
                    var state = e.target.value;
                    if (statesData[state]) {{
                        focusState(state);
                    }}
                }});

                // Reset Event
                document.getElementById('resetView').addEventListener('click', function() {{
                    applyMask(allFeatures);
                    map.setView([22.0, 78.0], 5);
                    document.getElementById('stateSearch').value = '';
                }});

                // Year Event
                var yearSelect = document.getElementById('yearSelect');
                yearSelect.addEventListener('change', function(e) {{
                    var year = e.target.value;
                    loadHeatmap(year);
                }});

                // Prev/Next Buttons
                document.getElementById('prevYear').addEventListener('click', function() {{
                    if (yearSelect.selectedIndex > 0) {{
                        yearSelect.selectedIndex--;
                        loadHeatmap(yearSelect.value);
                    }}
                }});

                document.getElementById('nextYear').addEventListener('click', function() {{
                    if (yearSelect.selectedIndex < yearSelect.options.length - 1) {{
                        yearSelect.selectedIndex++;
                        loadHeatmap(yearSelect.value);
                    }}
                }});

            }}, 500);

            function focusState(stateName) {{
                var layer = statesData[stateName];
                if (!layer) return;

                // 1. Zoom to State
                map.fitBounds(layer.getBounds());

                // 2. Create Mask for single state
                applyMask([layer.toGeoJSON()]);
            }}

            // Title Control
            var title = L.control({{position: 'topright'}});
            title.onAdd = function (map) {{
                var div = L.DomUtil.create('div', 'info');
                div.innerHTML = '<h4 id="mapTitle">Average Annual Rainfall</h4><p>Data Source: IPED Mean Source Data</p>';
                return div;
            }};
            title.addTo(map);

            // Legend Control
            var legend = L.control({{position: 'bottomright'}});
            legend.onAdd = function (map) {{
                var div = L.DomUtil.create('div', 'info legend');
                var grades = ['Low', 'Medium', 'High'];
                var colors = ['blue', 'lime', 'red']; 
                
                div.innerHTML += '<strong>Intensity</strong><br>';
                for (var i = 0; i < grades.length; i++) {{
                    div.innerHTML +=
                        '<i style="background:' + colors[i] + '"></i> ' +
                        grades[i] + '<br>';
                }}
                return div;
            }};
            legend.addTo(map);

            // Heatmap Layer Handling
            var currentHeatLayer = null;

            function loadHeatmap(year) {{
                // Update Title
                document.getElementById('mapTitle').innerText = 'Average Annual Rainfall (' + year + ')';

                var file = 'heatmap_data_' + year + '.json';
                console.log("Loading " + file);
                
                fetch(file)
                    .then(response => response.json())
                    .then(addressPoints => {{
                        if (currentHeatLayer) {{
                            map.removeLayer(currentHeatLayer);
                        }}
                        
                        currentHeatLayer = L.heatLayer(addressPoints, {{
                            radius: 12,
                            blur: 20,
                            maxZoom: 10,
                            max: 1.0,
                            gradient: {{0.0: 'blue', 0.25: 'cyan', 0.5: 'lime', 0.75: 'yellow', 1.0: 'red'}} 
                        }});
                        
                        currentHeatLayer.addTo(map);
                    }})
                    .catch(error => console.error('Error loading heatmap data:', error));
            }}

            // Initial Load
            loadHeatmap('{years[0]}');

        </script>
    </body>
    </html>
    """
    
    with open('rain/site/map.html', 'w') as f:
        f.write(html_content)
    
    print("Interactive map generated: rain/site/map.html")

if __name__ == "__main__":
    generate_interactive_map()