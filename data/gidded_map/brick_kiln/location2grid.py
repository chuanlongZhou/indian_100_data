import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import box

def point_to_grid(geo_df, value_col, box_size):
    """
    Convert point data to grid boxes, summing the values of points within each box.
    
    Parameters:
        geo_df (GeoDataFrame): GeoDataFrame containing point geometries.
        value_col (str): The column containing values to sum.
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

    # Aggregate by grid cells
    grid_agg = geo_df.groupby(["grid_x", "grid_y"])[value_col].sum().reset_index()

    # Compute grid box geometries
    grid_agg["geometry"] = grid_agg.apply(lambda row: 
        box(
            row["grid_x"] * box_size, 
            row["grid_y"] * box_size,
            (row["grid_x"] + 1) * box_size, 
            (row["grid_y"] + 1) * box_size
        ), axis=1
    )

    # Convert to GeoDataFrame
    grid_df = gpd.GeoDataFrame(grid_agg, geometry="geometry", crs=geo_df.crs)

    return grid_df

# Example Usage
# Load point data
gdf = gpd.read_file("kiln_location.geojson")  # Replace with actual file path
gdf['value'] = 1
# check lon, remove the point outside india
gdf = gdf[gdf['geometry'].x > 68.0]
gdf = gdf[gdf['geometry'].x < 97.0]

# Convert to grid with box size (e.g., 500 meters)
grid_gdf = point_to_grid(gdf, value_col="value", box_size=0.1)  # Replace with actual box size

# Save or visualize
grid_gdf.to_file("grid_output.geojson", driver="GeoJSON")
grid_gdf.plot()
