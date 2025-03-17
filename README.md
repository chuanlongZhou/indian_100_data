# indian_100_data
 visualization data for the Indian 100 website


How to update data:
1. The city grid is under: indian_100_data/data/city/city_grid
   For each gird, you have indexes with f"{cityName}_{gridIndex}", eg: "index": "Agartala_0", this is used for matching the rows in CSV files in data/summary_grid and data/gidded_data
2. CSV files under: data/summary_grid
   Total Emission from this grid -> annual mean of the total emission from this grid 
3.  CSV files under: data/gidded_data
   Daily Emission from this grid -> Daily Emission from this grid 
4.  CSV files under: data/summary_time_series
   Daily total emission for a city - > sum of the city grids under: data/gidded_data
