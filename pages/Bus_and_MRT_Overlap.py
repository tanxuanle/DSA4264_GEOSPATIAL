import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString
import folium
from folium import GeoJson
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import streamlit.components.v1 as components
import os


##### DATA HANDLING #####
mrt_stations = pd.read_csv("data/mrt_geocodes.csv")
bus_routes_combined = pd.read_csv("data/bus_routes_combined.csv")

bus_routes_combined['geometry'] = bus_routes_combined.apply(lambda x: Point((x.Longitude, x.Latitude)), axis=1)
bus_routes_combined = gpd.GeoDataFrame(bus_routes_combined, geometry='geometry', crs="EPSG:4326")

# Prepare Linestrings for all bus routes
routes = (
    bus_routes_combined.sort_values(by=['ServiceNo', 'Direction', 'StopSequence'])
    .groupby(['ServiceNo', 'Direction'])['geometry']
    .apply(lambda x: LineString(x.tolist()))
    .reset_index()
)
bus_routes_ls = gpd.GeoDataFrame(routes, geometry='geometry', crs="EPSG:4326")

# Prepare MRT lines as Linestrings
mrt_lines = {}
for line_code in mrt_stations['STN_NO'].str.extract(r'(\D+)', expand=False).unique():
    line_stations = mrt_stations[mrt_stations['STN_NO'].str.startswith(line_code)]
    line_stations = line_stations.assign(Station_Number=line_stations['STN_NO'].str.extract(r'(\d+)').astype(int))
    line_sorted = line_stations.sort_values(by='Station_Number').reset_index(drop=True)
    line_sorted['geometry'] = line_sorted.apply(lambda row: Point(row['Longitude'], row['Latitude']), axis=1)
    line_sorted = gpd.GeoDataFrame(line_sorted, geometry='geometry', crs="EPSG:4326")
    route_line = LineString(line_sorted['geometry'].tolist())
    mrt_lines[line_code] = gpd.GeoDataFrame({'Line': [line_code], 'geometry': [route_line]}, crs="EPSG:4326")


##### STREAMLIT UI #####

st.title("Bus and MRT Overlap Analysis")
st.sidebar.header("Selection Options")

# MRT Line Selection
selected_mrt_line_code = st.sidebar.selectbox("Select MRT Line", list(mrt_lines.keys()))

# Select and buffer 500m along the chosen MRT line
selected_mrt_line = mrt_lines[selected_mrt_line_code].to_crs(epsg=32648)
bus_routes_ls = bus_routes_ls.to_crs(epsg=32648)
selected_buffer = selected_mrt_line.buffer(500).union_all()

# Define overlap calculation function
def calculate_overlap(route):
    intersection = route.intersection(selected_buffer)
    overlap_length = intersection.length
    route_length = route.length
    overlap_percentage = (overlap_length / route_length) * 100 if route_length > 0 else 0
    return pd.Series({'Overlap Length': round(overlap_length), 'Overlap Percentage': round(overlap_percentage, 1)})

# Calculate overlaps
buffer_overlap_500 = bus_routes_ls.copy()
buffer_overlap_500[['Overlap Length', 'Overlap Percentage']] = buffer_overlap_500['geometry'].apply(calculate_overlap)
buffer_overlap_500 = buffer_overlap_500.sort_values(by='Overlap Percentage', ascending=False).head(5)      # Top 5

# Allow users to select specific bus services
selected_services = st.sidebar.multiselect(
    "Select Bus Services",
    options=bus_routes_ls['ServiceNo'].unique(),
    default=buffer_overlap_500['ServiceNo'].unique()
)

# Get the colormap and generate the necessary number of colors
color_palette = plt.colormaps.get_cmap('tab10')
colors = [color_palette(i) for i in range(len(selected_services))]
colors_dict = {service: colors[i] for i, service in enumerate(selected_services)}

# Convert back to EPSG:4326 for map plotting
bus_routes_ls = bus_routes_ls.to_crs("EPSG:4326")
selected_mrt_line = selected_mrt_line.to_crs("EPSG:4326")
buffer_overlap_500 = buffer_overlap_500.to_crs("EPSG:4326")

# Filter data for selected bus services
selected_data = buffer_overlap_500[buffer_overlap_500['ServiceNo'].isin(selected_services)].copy()
selected_data = gpd.GeoDataFrame(selected_data, geometry='geometry', crs="EPSG:4326")

st.write("Selected Bus Service Overlap Data")
st.write(selected_data[['ServiceNo', 'Direction', 'Overlap Length', 'Overlap Percentage']])

# Map Display
st.subheader("Map View")

# Function to create the map
def create_map(selected_mrt_line_code, selected_services):
    sgmap = folium.Map(location=[1.3521, 103.8198], zoom_start=12)

    # Add MRT line and buffer
    coords = [(lat, lon) for lon, lat in selected_mrt_line.iloc[0].geometry.coords]
    folium.PolyLine(
        locations=coords,
        color='brown',
        weight=5,
        opacity=0.8,
        tooltip=f"{selected_mrt_line_code} Line"
    ).add_to(sgmap)

    # Add buffer to map
    buffer_gdf = gpd.GeoDataFrame(geometry=[selected_buffer], crs="EPSG:32648").to_crs("EPSG:4326")
    folium.GeoJson(
        buffer_gdf,
        style_function=lambda x: {'fillColor': 'blue', 'color': 'blue', 'weight': 1, 'fillOpacity': 0.5}
    ).add_to(sgmap)

    # Plot selected bus routes with dynamically assigned colors
    for _, row in selected_data.iterrows():
        service_no = row['ServiceNo']

        # Get the color from colors_dict
        route_color_rgb = colors_dict[service_no]
        route_color = '#{:02x}{:02x}{:02x}'.format(int(route_color_rgb[0] * 255),
                                                int(route_color_rgb[1] * 255),
                                                int(route_color_rgb[2] * 255))

        coords = [(lat, lon) for lon, lat in row['geometry'].coords]
        folium.PolyLine(
            locations=coords,
            color=route_color,
            weight=5,
            opacity=0.8,
            tooltip=f"{service_no} - Direction {row['Direction']}"
        ).add_to(sgmap)
        
        # Add start and end markers for each route
        folium.Marker(location=coords[0], icon=folium.Icon(color='blue')).add_to(sgmap)
        folium.Marker(location=coords[-1], icon=folium.Icon(color='blue')).add_to(sgmap)

    # Save map to HTML file
    html_path = "map.html"
    sgmap.save(html_path)
    return html_path

# Update the map only when button is clicked
if st.sidebar.button("Update Map"):
    html_path = create_map(selected_mrt_line_code, selected_data)
    st.session_state['map_html_path'] = html_path  # Save path in session state

# Embed the saved HTML map if it exists
if 'map_html_path' in st.session_state and os.path.exists(st.session_state['map_html_path']):
    with open(st.session_state['map_html_path'], 'r', encoding='utf-8') as map_file:
        map_html = map_file.read()
    components.html(map_html, height=500, width=700)

