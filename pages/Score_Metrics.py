import streamlit as st
import folium
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString
import os
from dotenv import load_dotenv

load_dotenv()
my_api_key = os.getenv('ONE_MAP_ACCESS_TOKEN')

##### DATA HANDLING #####
# Load data
mrt_stations = pd.read_csv("data/mrt_stations.csv")
bus_routes_combined = pd.read_csv("data/bus_routes_combined.csv")

# Drop bus services ending with alphabets from the DataFrame
bus_routes_combined = bus_routes_combined[~bus_routes_combined['ServiceNo'].str.contains(r'[A-Za-z]$', regex=True)]

# Convert to GeoDataFrame
bus_routes_combined['geometry'] = bus_routes_combined.apply(lambda x: Point((x.Longitude, x.Latitude)), axis=1)
bus_routes_combined = gpd.GeoDataFrame(bus_routes_combined, geometry='geometry', crs="EPSG:4326")

mrt_stations['geometry'] = mrt_stations.apply(lambda x: Point((x.Longitude, x.Latitude)), axis=1)
mrt_stations = gpd.GeoDataFrame(mrt_stations, geometry='geometry', crs="EPSG:4326")

# Filter top 10 bus services
top_10_bus_services = ["36", "67", "23", "170", "961", "63", "65", "184", "401", "5"]
top_10_bus_services = sorted(top_10_bus_services)

filtered_df = bus_routes_combined[bus_routes_combined['ServiceNo'].isin(top_10_bus_services)]
filtered_bus_routes = gpd.GeoDataFrame(filtered_df, geometry=filtered_df['geometry'], crs="EPSG:4326")

# Linestrings for all bus services
routes = (
    bus_routes_combined.sort_values(by=['ServiceNo', 'Direction', 'StopSequence'])
    .groupby(['ServiceNo', 'Direction'])['geometry']
    .apply(lambda x: LineString(x.tolist()) if len(x) > 1 else None)
    .dropna()  # Remove entries where LineString could not be created
    .reset_index()
)

# Create GeoDataFrame with valid LineStrings
bus_routes_ls = gpd.GeoDataFrame(routes, geometry='geometry', crs="EPSG:4326")

# Constants
buffer_distance_meters = 400 
overlap_threshold = 30 

warm_tones = [
    "#e41a1c",  # Bright Red
    "#ff7f00",  # Orange
    "#fdae61",  # Soft Orange
    "#d95f0e",  # Deep Orange
    "#e31a1c",  # Rich Red
    "#f46d43",  # Coral
    "#fee08b",  # Light Yellow
    "#fdb863",  # Warm Peach
    "#a6761d",  # Earthy Brown
    "#d73027",  # Dark Red
]

# Count function for bus stops within MRT buffer
def count_bus_stops_within_buffer(bus_routes_combined, mrt_stations, buffer_distance=400):
    results = []
    mrt_stations = mrt_stations.to_crs(epsg=32648)
    mrt_stations['geometry'] = mrt_stations.geometry.buffer(buffer_distance)

    unique_routes_directions = bus_routes_combined[['ServiceNo', 'Direction']].drop_duplicates()
    for _, row in unique_routes_directions.iterrows():
        route, direction = row['ServiceNo'], row['Direction']
        bus_stops = bus_routes_combined[
            (bus_routes_combined['ServiceNo'] == route) &
            (bus_routes_combined['Direction'] == direction)
        ]
        bus_stops_gdf = gpd.GeoDataFrame(bus_stops, geometry=bus_stops['geometry'], crs="EPSG:4326").to_crs(epsg=32648)
        bus_stops_gdf['within_mrt_buffer'] = bus_stops_gdf.geometry.apply(
            lambda bus_stop: any(mrt_buffer.intersects(bus_stop) for mrt_buffer in mrt_stations.geometry)
        )
        total_bus_stops = len(bus_stops_gdf)
        count_within_buffer = bus_stops_gdf['within_mrt_buffer'].sum()
        percentage_within_buffer = (count_within_buffer / total_bus_stops * 100) if total_bus_stops > 0 else 0
        results.append({'Route': route, 'Direction': direction, 'Bus Stops Within Buffer': count_within_buffer})
    return pd.DataFrame(results)

# Count function for alternative services overlap
def count_services_with_overlap(shortlisted_services, bus_routes_ls, threshold):
    overlap_results = []
    for _, shortlisted_row in shortlisted_services.iterrows():
        service_no = shortlisted_row['ServiceNo']
        shortlisted_geom = bus_routes_ls.loc[bus_routes_ls['ServiceNo'] == service_no, 'geometry'].values[0]
        shortlisted_length = shortlisted_geom.length
        overlap_count = 0
        overlapping_services = []

        for _, existing_route in bus_routes_ls.iterrows():
            existing_service_no = existing_route['ServiceNo']
            existing_geom = existing_route['geometry']
            if service_no == existing_service_no:
                continue
            intersection = shortlisted_geom.intersection(existing_geom)
            intersection_length = intersection.length if intersection.is_valid else 0
            overlap_percentage = (intersection_length / shortlisted_length) * 100 if shortlisted_length > 0 else 0
            if overlap_percentage >= threshold:
                overlap_count += 1
                overlapping_services.append(existing_service_no)
        overlap_results.append({'ServiceNo': service_no, 'Overlap Count': overlap_count,  'Overlapping Services': overlapping_services})
    return pd.DataFrame(overlap_results)


########## Streamlit App Interface #########

st.sidebar.header("Options")

# Toggle Selection
view_option = st.sidebar.radio("Select Map View", ["Bus Stops Near MRT Stations", "Alternative Route Overlap"])

# Dropdowns for selecting bus service
selected_service = st.sidebar.selectbox("Select Bus Service", options=top_10_bus_services)
directions = filtered_bus_routes[filtered_bus_routes['ServiceNo'] == selected_service]['Direction'].unique()
selected_direction = st.sidebar.selectbox("Select Direction", options=directions)

# Load appropriate data and create map based on selection
if view_option == "Bus Stops Near MRT Stations":
    st.subheader(f"**Bus Stops Near MRT Stations - Route {selected_service} (Direction {selected_direction})**")

    bus_stops_gdf = filtered_bus_routes[
        (filtered_bus_routes['ServiceNo'] == selected_service) &
        (filtered_bus_routes['Direction'] == selected_direction)
    ].to_crs(epsg=32648)

    # Buffer MRT stations and check which bus stops are within buffer
    mrt_stations_buffered = mrt_stations.to_crs(epsg=32648)
    mrt_stations_buffered['geometry'] = mrt_stations_buffered['geometry'].buffer(buffer_distance_meters)
    bus_stops_gdf['within_mrt_buffer'] = bus_stops_gdf.geometry.apply(
        lambda stop: any(stop.within(buffer) for buffer in mrt_stations_buffered.geometry)
    )
    bus_stops_gdf = bus_stops_gdf.to_crs("EPSG:4326")

    # Calculate summary for bus stops near MRT
    total_stops = len(bus_stops_gdf)
    stops_within_buffer = bus_stops_gdf['within_mrt_buffer'].sum()
    percentage_within_buffer = (stops_within_buffer / total_stops * 100) if total_stops > 0 else 0

    # Display text summary
    st.write(f"**Number of bus stops within 400m of MRT:**   {stops_within_buffer} / {total_stops} ({percentage_within_buffer:.2f}%)")

    # Create map
    m = folium.Map(location=[1.3521, 103.8198], zoom_start=12)
    folium.TileLayer(tiles="https://www.onemap.gov.sg/maps/tiles/Grey/{z}/{x}/{y}.png", attr="OneMap", name="OneMap Basemap").add_to(m)

    # Add bus route line to the map
    route_coords = [(point.y, point.x) for point in bus_stops_gdf.geometry]
    folium.PolyLine(route_coords, color="blue", weight=5, opacity=0.6, tooltip=f"Bus Route {selected_service} ").add_to(m)

    # Plot bus stops with CircleMarkers and highlight those within MRT buffer with folium Markers
    for _, stop in bus_stops_gdf.iterrows():
        location = (stop.geometry.y, stop.geometry.x)
        bus_stop_info = f"Bus Stop Code: {stop['BusStopCode']}<br>Description: {stop['Description']}"
        
        if stop['within_mrt_buffer']:
            circle_marker = folium.CircleMarker(
                location=location,
                radius=5,
                color="red",
                fill=True,
                fill_color="red",
                fill_opacity=0.8,
                tooltip=bus_stop_info
            ).add_to(m)
            
        else:
            folium.CircleMarker(
                location=location,
                radius=5,
                color="blue",
                fill=True,
                fill_color="blue",
                fill_opacity=0.8,
                tooltip=bus_stop_info
            ).add_to(m)

    # Save map to HTML and display
    map_html = m._repr_html_()
    st.components.v1.html(map_html, width=1000, height=800)


elif view_option == "Alternative Route Overlap":
    st.subheader(f"**Alternative Route Overlap -- {selected_service} (Direction {selected_direction})**")
    shortlisted_services = filtered_bus_routes[filtered_bus_routes['ServiceNo'] == selected_service][['ServiceNo']].drop_duplicates()
    overlap_count_df = count_services_with_overlap(shortlisted_services, bus_routes_ls, threshold=overlap_threshold)

    # Display text summary for overlap results
    overlap_count = overlap_count_df['Overlap Count'].sum()
    overlapping_services = overlap_count_df['Overlapping Services'].explode().unique()
    
    # Only display the overlapping services if there are any
    if overlap_count > 0:
        overlapping_services_text = ", ".join(str(service) for service in overlapping_services)
        st.write(f"**Number of Overlapping Bus Services (at least 30%):** {overlap_count}")
        st.write(f"**Overlapping Services:** {overlapping_services_text}")
    else:
        st.write("**No overlapping bus services found.**")

    # Create base map
    m = folium.Map(location=[1.3521, 103.8198], zoom_start=12, tiles='CartoDB Positron')
    folium.TileLayer(tiles="https://www.onemap.gov.sg/maps/tiles/Grey/{z}/{x}/{y}.png", attr="OneMap", name="OneMap Basemap").add_to(m)
    
    selected_route = bus_routes_combined[(bus_routes_combined['ServiceNo'] == selected_service) & (bus_routes_combined['Direction'] == selected_direction)]
    selected_route_coords = [(point.y, point.x) for point in selected_route.geometry]
    folium.PolyLine(selected_route_coords, color="blue", weight=8, opacity=0.8, tooltip=f"Selected Route {selected_service}").add_to(m)

    # Plot each overlapping route distinctly
    for idx, (_, row) in enumerate(overlap_count_df.iterrows()):
        service_no = row['ServiceNo']
        overlap_count = row['Overlap Count']
        overlapping_services = row['Overlapping Services']
        
        # Only display routes with overlap
        if overlap_count > 0:
            for overlap_idx, overlap_service in enumerate(overlapping_services):
                overlap_route = bus_routes_combined[(bus_routes_combined['ServiceNo'] == overlap_service) & (bus_routes_combined['Direction'] == selected_direction)]
                overlap_route_coords = [(point.y, point.x) for point in overlap_route.geometry]
                shades = warm_tones[overlap_idx % len(warm_tones)]
                folium.PolyLine(overlap_route_coords, color=shades, weight=6, opacity=0.5, tooltip=f"Overlap Route {overlap_service}").add_to(m)
                

    # Save map to HTML and display
    map_html = m._repr_html_()
    st.components.v1.html(map_html, width=1000, height=800)