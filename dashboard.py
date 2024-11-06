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
mrt_stations = pd.read_csv("data/mrt_stations.csv")
bus_routes_combined = pd.read_csv("data/bus_routes_combined.csv")

# Drop bus services ending with alphabets from the DataFrame
bus_routes_combined = bus_routes_combined[~bus_routes_combined['ServiceNo'].str.contains(r'[A-Za-z]$', regex=True)]

# Kept the unfiltered version for analysis for alternative bus overlaps & passenger calc.
bus_routes_combined['geometry'] = bus_routes_combined.apply(lambda x: Point((x.Longitude, x.Latitude)), axis=1)
bus_routes_combined = gpd.GeoDataFrame(bus_routes_combined, geometry='geometry', crs="EPSG:4326")

# Prepare Linestrings for trunk services
routes = (
    bus_routes_combined.sort_values(by=['ServiceNo', 'Direction', 'StopSequence'])
    .groupby(['ServiceNo', 'Direction', 'Category'])['geometry']
    .apply(lambda x: LineString(x.tolist()))
    .reset_index()
)
bus_routes_ls = gpd.GeoDataFrame(routes, geometry='geometry', crs="EPSG:4326")

# Filter for trunk services only
trunk_routes_ls = bus_routes_ls[bus_routes_ls['Category'] == 'TRUNK'].copy()

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

st.subheader("Bus and MRT Overlap Analysis")
st.sidebar.header("Selection Options")

# MRT Line Selection
selected_mrt_lines = st.sidebar.multiselect("Select MRT Line", list(mrt_lines.keys()), default=["TE", "DT"])

# Define overlap calculation function
def calculate_overlap(route, buffer):
    intersection = route.intersection(buffer)
    overlap_length = intersection.length if not intersection.is_empty else 0
    route_length = route.length
    overlap_percentage = (overlap_length / route_length) * 100 if route_length > 0 else 0
    return round(overlap_length, 2), round(overlap_percentage, 2)


# Store results for each MRT Line
all_results = pd.DataFrame()

for line_code in selected_mrt_lines:
    selected_mrt_line = mrt_lines[line_code].to_crs("EPSG:32648")  # Project to UTM for accurate buffering
    mrt_buffer = selected_mrt_line.buffer(400).union_all()

    # Calculate overlaps for each bus route against this MRT line buffer
    buffer_overlap = trunk_routes_ls.to_crs("EPSG:32648").copy()
    
    buffer_overlap[['Overlap Length', 'Overlap Percentage']] = buffer_overlap['geometry'].apply(
        lambda route: pd.Series(calculate_overlap(route, mrt_buffer)))
    
    buffer_overlap['MRT Line'] = line_code
    
    # Append results to the all_results DataFrame
    all_results = pd.concat([all_results, buffer_overlap])

# Sort by highest overlap percentage and take the top 10 bus services overall
all_results = all_results.sort_values(by='Overlap Length', ascending=False)
all_results = all_results.drop_duplicates(subset=['ServiceNo']).head(10)

# Allow users to select specific bus services
selected_services = st.sidebar.multiselect(
    "Select Bus Services",
    options=bus_routes_ls['ServiceNo'].unique(),
    default=all_results['ServiceNo'].unique()
)

# Get the colormap and generate the necessary number of colors
color_palette = plt.colormaps.get_cmap('tab10')
colors = [color_palette(i) for i in range(len(selected_services))]
colors_dict = {service: colors[i] for i, service in enumerate(selected_services)}

# Convert back to EPSG:4326 for map plotting
all_results = all_results.to_crs("EPSG:4326")

# Filter data for selected bus services
selected_data = all_results[all_results['ServiceNo'].isin(selected_services)].copy()
selected_data = gpd.GeoDataFrame(selected_data, geometry='geometry', crs="EPSG:4326")


st.dataframe(selected_data[['MRT Line', 'ServiceNo', 'Direction', 'Overlap Length', 'Overlap Percentage']], height = 200, width=700)

# Map Display
st.write("Map View")

# Function to create the map
def create_map(selected_mrt_lines, selected_services):
    sgmap = folium.Map(location=[1.3521, 103.8198], zoom_start=12, tiles="CartoDB Positron")

    buffer_colors = {
        "DT": "blue", 
        "TE": "brown", 
        "CC": "yellow",
        "NS": "red", 
        "NE": "purple",
        "EW": "green"
    }

    # Plot each selected MRT line with its buffer on the map
    for line_code in selected_mrt_lines:
        mrt_line_data = mrt_lines[line_code].to_crs(epsg=32648)
        coords = [(lat, lon) for lon, lat in mrt_line_data.to_crs("EPSG:4326").iloc[0].geometry.coords]

        # Create a buffer around each MRT line and add it to the map
        buffer_polygon = mrt_line_data.buffer(400).union_all()  # Creates a single polygon
        buffer_gdf = gpd.GeoDataFrame(geometry=[buffer_polygon], crs="EPSG:32648").to_crs("EPSG:4326")
        
        # Set color for the buffer based on the MRT line
        buffer_color = buffer_colors.get(line_code, 'blue')  # Default color if line not in buffer_colors

        folium.GeoJson(
            buffer_gdf,
            style_function=lambda x, color=buffer_color: {
                'fillColor': color, 'color': color, 'weight': 1, 'fillOpacity': 0.4
            }
        ).add_to(sgmap)

        folium.PolyLine(
            locations=coords,
            color=buffer_color,
            weight=5,
            opacity=0.8,
            tooltip=f"{line_code} Line"
        ).add_to(sgmap)


    # Plot selected bus routes with dynamically assigned colors
    for _, row in selected_data.iterrows():
        service_no = row['ServiceNo']
        
        # Get the color from colors_dict
        route_color_rgb = colors_dict[service_no]
        route_color = '#{:02x}{:02x}{:02x}'.format(int(route_color_rgb[0] * 255),
                                                int(route_color_rgb[1] * 255),
                                                int(route_color_rgb[2] * 255))


        # Convert route coordinates to (lat, lon) format
        coords = [(lat, lon) for lon, lat in row['geometry'].coords]
        
        # Plot the bus route on the map
        folium.PolyLine(
            locations=coords,
            color=route_color,
            weight=5,
            opacity=0.8,
            tooltip=f"{service_no} - Direction {row['Direction']}"
        ).add_to(sgmap)
        
        # Add start and end markers for each route using CircleMarker for custom color
        folium.CircleMarker(
            location=coords[0],
            radius=6,  # Adjust size as needed
            color=route_color,
            fill=True,
            fill_color=route_color,
            fill_opacity=1
        ).add_to(sgmap)

        folium.CircleMarker(
            location=coords[-1],
            radius=6,  # Adjust size as needed
            color=route_color,
            fill=True,
            fill_color=route_color,
            fill_opacity=1
        ).add_to(sgmap)


    # Save map to HTML file
    html_path = "map.html"
    sgmap.save(html_path)
    return html_path

# Update the map only when button is clicked
if st.sidebar.button("Update Map"):
    html_path = create_map(selected_mrt_lines, selected_services)
    st.session_state['map_html_path'] = html_path  # Save path in session state

# Embed the saved HTML map if it exists
if 'map_html_path' in st.session_state and os.path.exists(st.session_state['map_html_path']):
    with open(st.session_state['map_html_path'], 'r', encoding='utf-8') as map_file:
        map_html = map_file.read()
    components.html(map_html, height=500, width=700)

