import streamlit as st
import streamlit.components.v1 as components
import geopandas as gpd
from shapely.geometry import mapping
import json
import streamlit.components.v1 as components
from data_module import mrt_buffers

# Filter the GeoDataFrame to include only the TE line
te_buffer = mrt_buffers[mrt_buffers['GROUPED_LINE'] == 'TE']

# Convert the geometry of TE line to GeoJSON format
te_buffer_geojson = te_buffer.geometry.apply(mapping).to_json()

# Set Streamlit page configuration
st.set_page_config(page_title="TE Line Buffer Map", layout="wide")

# Title of the Streamlit app
st.title("TE Line Buffer Map with OneMap API")

# Read the HTML file
with open("te_line_buffer_map.html", "r") as f:
    map_html = f.read()

# Replace the placeholder with GeoJSON data
map_html = map_html.replace("<%= te_buffer_geojson %>", json.dumps(te_buffer_geojson))

# Embed the HTML file and the script in the Streamlit app
components.html(map_html, height=800, scrolling=True)
