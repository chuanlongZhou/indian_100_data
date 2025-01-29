#%%

import numpy as np
import pandas as pd
import geopandas as gpd
import os
from shapely.geometry import Point
from shapely.validation import make_valid
#%%

res = []

# Get the list of cities
city_files = os.listdir('city_grid_map')

index =0 
for city_file in city_files:
    # Read the GeoJSON file
    city_grid_map = gpd.read_file(f'city_grid_map/{city_file}')
    total_bounds = city_grid_map.total_bounds
    
    center_x = (total_bounds[0] + total_bounds[2]) / 2
    center_y = (total_bounds[1] + total_bounds[3]) / 2
    res.append({
        'city_name': city_file.split('.')[0],
        'center_x': center_x,
        'center_y': center_y,
        'population': np.random.randint(100000, 1000000),
    })
    index += 1
    
# Ensure the CRS is consistent
res_gdf = gpd.GeoDataFrame(
    res,
    geometry=gpd.points_from_xy([entry['center_x'] for entry in res],
                                [entry['center_y'] for entry in res])
)
res_gdf.crs = city_grid_map.crs
res_gdf = res_gdf.to_crs('EPSG:4326')
res_gdf = res_gdf.drop(columns=['center_x', 'center_y'])
res_gdf.to_file('city_center.geojson', driver='GeoJSON')


city_names = res_gdf['city_name'].values
# %%
I want to generate test dataset of CO2+PM2.5+NOx emissions from 5 sectors, traffic, building, power, industrial, and aviation from 100 Indian cities.  
The data set has two types of data
1. time series of a city total from the 5 sectors for 3 emission species (CSV files, one for Indian total, region total, and each city) 
2. monthly 500*500 resolution emission map from the 5 sectors for 3 emission species (geojson file for each city, the pixel is provided as polygon, values are features for each polygon)

I want to create an interactive web dashboard to visualize them using vue3, vuetify and vit