import requests
import os
from dotenv import load_dotenv
import pandas as pd
import json
import folium
import streamlit as st
from streamlit_folium import st_folium
import polyline

load_dotenv()
my_api_key = os.getenv('ONE_MAP_ACCESS_TOKEN')

bus_stops = pd.read_csv("data/bus_stops_full.csv")
bus_stop_coords = {row['BusStopCode']: (row['Latitude'], row['Longitude']) for _, row in bus_stops.iterrows()}
bus_stop_names = {row['BusStopCode']: row['RoadName'] for _, row in bus_stops.iterrows()}

bus_stop_options = [f"{code} - {bus_stop_names[code]}" for code in bus_stop_coords.keys()]
bus_stop_codes = list(bus_stop_coords.keys())

start_selection = st.selectbox("Select Start Bus Stop Code:", bus_stop_options)
end_selection = st.selectbox("Select End Bus Stop Code:", bus_stop_options)
start_code = int(start_selection.split(" - ")[0])
end_code = int(end_selection.split(" - ")[0])

# Get coordinates for bus stops 
start_coords = bus_stop_coords[start_code]
end_coords = bus_stop_coords[end_code]

# Function to get route information from OneMap API
def get_route_info(start, end):
    params = { 
        'start': start,
        'end': end,   
        'mode': 'TRANSIT',
        'routeType': 'pt',   # walk, drive, pt, cycle
        'date': '10-20-2024',   # date in MM-DD-YYYY format
        'time': '09:00:00',   # time in HH:MM:SS format
        'maxWalkDistance': 500,
        'numItineraries': 3
    }
    headers = {"Authorization": my_api_key}
    url = "https://www.onemap.gov.sg/api/public/routingsvc/route"
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        response_json = response.json()
        return response_json
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

# Fetch route data
route_data = None
if st.button("Get Routes"):
    start_lat_lon = f"{start_coords[0]},{start_coords[1]}"
    end_lat_lon = f"{end_coords[0]},{end_coords[1]}"
    route_data = get_route_info(start_lat_lon, end_lat_lon)
    
    if route_data and "plan" in route_data:
        # Store route data in session state so it persists across interactions
        st.session_state['route_data'] = route_data

if 'route_data' in st.session_state:
    route_data = st.session_state['route_data']
    itineraries = route_data['plan']['itineraries']

    itinerary_options = [
        f"Itinerary {i+1}: {it['duration'] // 60} min, {', '.join(set(leg['mode'] for leg in it['legs']))}"
        for i, it in enumerate(itineraries)
    ]

    # Let the user select an itinerary
    selected_itinerary_idx = st.selectbox("Select an Itinerary:", range(len(itinerary_options)), format_func=lambda i: itinerary_options[i])
    selected_itinerary = itineraries[selected_itinerary_idx]

    st.session_state['selected_itinerary'] = selected_itinerary

    # Show the total duration of the selected itinerary
    total_duration = selected_itinerary['duration'] // 60  # Convert from seconds to minutes
    st.write(f"Total Duration: {total_duration} minutes")

    # Initialize the map centered around the start location
    route_map = folium.Map(location=[start_coords[0], start_coords[1]], zoom_start=14)

    # Add OneMap basemap tile layer
    folium.TileLayer(tiles="https://www.onemap.gov.sg/maps/tiles/Grey/{z}/{x}/{y}.png", attr="OneMap", name="OneMap Basemap").add_to(route_map)

    for leg in selected_itinerary['legs']:
        leg_duration = leg['duration'] // 60
        start_name = leg['from']['name']
        end_name = leg['to']['name']
        
         # Set the polyline color based on the mode of transport
        if leg['mode'] == 'WALK':
            color = 'black'  # Orange for walking
            st.write(f"Walking from {start_name} to {end_name} - Duration: {leg_duration} min")
        elif leg['mode'] == 'BUS':
            color = 'blue'  # Blue for bus
            bus_service = leg['route']  # Bus service number
            st.write(f"Bus {bus_service} from {start_name} to {end_name} - Duration: {leg_duration} min")
        elif leg['mode'] == 'RAIL':
            color = 'green'  # Green for MRT (train)
            st.write(f"Train from {start_name} to {end_name} - Duration: {leg_duration} min")
        else:
            color = 'gray'


        if 'legGeometry' in leg:
            points = leg['legGeometry']['points']
            decoded_points = polyline.decode(points)  # Decode polyline
            
            # Add the decoded polyline to the map
            folium.PolyLine(decoded_points, color=color, weight=5).add_to(route_map)
            
        # Add markers for start and end points of the leg
        start_location = [leg['from']['lat'], leg['from']['lon']]
        end_location = [leg['to']['lat'], leg['to']['lon']]
        folium.CircleMarker(start_location, radius=5, color="gray", fill=True, tooltip=start_name).add_to(route_map)
        folium.CircleMarker(end_location, radius=5, color="gray", tooltip=end_name).add_to(route_map)

        # If there is intermediate stops in the response
        if 'intermediateStops' in leg and len(leg['intermediateStops']) > 0:
            for stop in leg['intermediateStops']:
                stop_name = stop['name']
                stop_location = [stop['lat'], stop['lon']]
                folium.CircleMarker(stop_location, radius=3, color="red", tooltip=stop_name, icon=folium.Icon(color='red')).add_to(route_map)

    folium.Marker(end_location, tooltip=end_name).add_to(route_map)

    # Display the updated map with the selected itinerary
    st_folium(route_map, width=700, height=500)