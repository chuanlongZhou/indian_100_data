import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import box

def point_to_grid(geo_df, value_cols, box_size):
    """
    Convert point data to grid boxes, summing the values of multiple columns within each box.
    
    Parameters:
        geo_df (GeoDataFrame): GeoDataFrame containing point geometries.
        value_cols (list): List of column names to sum.
        box_size (float): Size of the grid box in the same unit as the CRS of geo_df.
        
    Returns:
        grid_df (GeoDataFrame): GeoDataFrame of grid boxes with summed values.
    """
    # Extract coordinates
    geo_df["x"] = geo_df.geometry.x
    geo_df["y"] = geo_df.geometry.y

    # Compute grid indices
    geo_df["grid_x"] = (geo_df["x"] // box_size).astype(int)
    geo_df["grid_y"] = (geo_df["y"] // box_size).astype(int)

    # Aggregate by grid cells, summing the specified value columns
    grid_agg = geo_df.groupby(["grid_x", "grid_y"])[value_cols].sum().reset_index()

    # Compute grid box geometries
    grid_agg["geometry"] = grid_agg.apply(lambda row: 
        box(
            row["grid_x"] * box_size, 
            row["grid_y"] * box_size,
            (row["grid_x"] + 1) * box_size, 
            (row["grid_y"] + 1) * box_size
        ), axis=1
    )

    # Convert to GeoDataFrame and remove grid_x, grid_y
    grid_df = gpd.GeoDataFrame(grid_agg.drop(columns=["grid_x", "grid_y"]), geometry="geometry", crs=geo_df.crs)

    return grid_df

# Example Usage
# Load point data
gdf = gpd.read_file("kiln_location.geojson")  # Replace with actual file path

# Total emission 
TOTAL_CO2 = 42.64  # million tonnes
TOTAL_PM25 = 23300  # tonnes
TOTAL_CO = 2750  # tones

# Total number of kilns
TOTAL_KILN = len(gdf)

# Assign emissions per kiln
gdf['CO2'] = TOTAL_CO2 / TOTAL_KILN
gdf['PM25'] = TOTAL_PM25 / TOTAL_KILN
gdf['CO'] = TOTAL_CO / TOTAL_KILN

# Remove points outside India
gdf = gdf[(gdf.geometry.x > 68.0) & (gdf.geometry.x < 97.0)]

# Convert to grid with box size (e.g., 0.1 degrees)
grid_gdf = point_to_grid(gdf, value_cols=['CO2', 'PM25', 'CO'], box_size=0.1)

grid_gdf['CO2'] = grid_gdf['CO2']*1000000 # to tonnes
grid_gdf['PM25'] = grid_gdf['PM25'] # already in tonnes
grid_gdf['CO'] = grid_gdf['CO'] # already in tonnes

# Save or visualize
grid_gdf.to_file("grid_output.geojson", driver="GeoJSON")
grid_gdf.plot()
