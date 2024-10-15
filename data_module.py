# data_module.py
import geopandas as gpd

mrt_buffers = gpd.read_file("data/mrt_buffers.geojson") \