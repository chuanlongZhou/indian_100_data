import geopandas as gpd
import json
import os
import pandas as pd

from shapely.ops import unary_union

# Create a single geometry from all geometries in the GeoDataFrame

# Paths to directories and files
geojson_directory = r"city_grid_map"
province_region_file = r"city_mapping.json"
output_directory = ""

# Load the province and region mapping
with open(province_region_file, "r") as file:
    city_province_region = json.load(file)

# Ensure output directory exists
os.makedirs(output_directory, exist_ok=True)

# Initialize lists to store all GeoDataFrames for merging
city_center_list = []
bounding_box_list = []
crs = 'EPSG:4326'
# Process each GeoJSON file
for filename in os.listdir(geojson_directory):
    # Load the GeoJSON file
    filepath = os.path.join(geojson_directory, filename)
    gdf = gpd.read_file(filepath)
    gdf = gdf.to_crs(crs)
    
    # Extract city name from the filename (adjust parsing as needed)
    city_name = filename.split(".")[0]
    
    # Get province and region
    province = city_province_region.get(city_name, {}).get("province", "Unknown")
    region = city_province_region.get(city_name, {}).get("region", "Unknown")
    if province == "Unknown" or region == "Unknown":
        print(f"Could not find province and region for {city_name}")
    unified_geometry = unary_union(gdf.geometry)
    
    # Create GeoDataFrames for city center and bounding box
    city_center_gdf = gpd.GeoDataFrame({
        "city_name": [city_name],
        "province": [province],
        "region": [region],
        "geometry": [unified_geometry.centroid]
    }, geometry="geometry", crs=gdf.crs)
    
    bounding_box_gdf = gpd.GeoDataFrame({
        "city_name": [city_name],
        "province": [province],
        "region": [region],
        "geometry": [unified_geometry.envelope]
    }, geometry="geometry", crs=gdf.crs)
    
    # Add to lists for merging
    city_center_list.append(city_center_gdf)
    bounding_box_list.append(bounding_box_gdf)

print(len(bounding_box_list))
print(len(city_center_list))
# Merge all city centers and bounding boxes
merged_city_centers = gpd.GeoDataFrame(pd.concat(city_center_list, ignore_index=True), crs=city_center_list[0].crs)
merged_bounding_boxes = gpd.GeoDataFrame(pd.concat(bounding_box_list, ignore_index=True), crs=bounding_box_list[0].crs)

# Save the merged GeoJSON files
city_center_filepath = os.path.join(output_directory, "city_center.geojson")
bounding_box_filepath = os.path.join(output_directory, "city_box.geojson")

merged_city_centers.to_file(city_center_filepath, driver="GeoJSON")
merged_bounding_boxes.to_file(bounding_box_filepath, driver="GeoJSON")

print(f"Merged and saved all city centers to: {city_center_filepath}")
print(f"Merged and saved all bounding boxes to: {bounding_box_filepath}")

# visualize the polygon, grid and the city center
import matplotlib.pyplot as plt
grid_path = r'city_grid_map'
output_directory = r'fig'
for city in merged_city_centers['city_name']:
    city_gdf = merged_city_centers[merged_city_centers['city_name'] == city]
    bounding_box_gdf = merged_bounding_boxes[merged_bounding_boxes['city_name'] == city]
    grid_gdf = gpd.read_file(os.path.join(grid_path, f"{city}.geojson"))
    shape_df = gpd.read_file(r'city\Urban Local Boundary\{city}.geojson'.format(city=city))
    grid_gdf = grid_gdf.to_crs(city_gdf.crs)
    shape_df = shape_df.to_crs(city_gdf.crs)
    grid_gdf.to_file(os.path.join(grid_path, f"{city}.geojson"), driver='GeoJSON')
    # Plot the city
    fig, ax = plt.subplots(figsize=(12, 12), dpi=200)
    bounding_box_gdf.boundary.plot(ax=ax, color='grey', linewidth=1)
    grid_gdf.boundary.plot(ax=ax, color='blue', linewidth=1, alpha=0.5)
    shape_df.plot(ax=ax, color='green', linewidth=1, alpha=0.5)
    city_gdf.plot(ax=ax, color='red', alpha=1)
    ax.set_title(city)
    
    plt.savefig(os.path.join(output_directory, f"{city}.png"))
    plt.close()
    