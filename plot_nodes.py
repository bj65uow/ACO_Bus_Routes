# Importing GIS libraries
import osmnx as ox
import geopandas as gpd

# Define map boundaries for Tauranga, New Zealand
tauranga_bounds = {
    'north': -37.6039,
    'east': 176.5125,
    'south': -37.8114,
    'west': 176.0593
}

# Census data is in ESPG:2193, these bounds are similar to the ones above
tauranga_bbox = (1869316.8619308192, 5810699.85703883, 1910089.458412611, 5832327.558897601) # Format: min x, min y, max x, max y

# Download OSM bus stop map features for Tauranga
bus_stop_features = ox.features_from_bbox(**tauranga_bounds, tags={'highway': 'bus_stop'})

# Read census data shapefile within the same boundaries
census_shapefile_path = 'data/statsnz-2018-census-electoral-population-meshblock-2020-SHP/2018-census-electoral-population-meshblock-2020.shp'
census_data = gpd.read_file(census_shapefile_path, bbox=tauranga_bbox)

# Convert the census data to standard coordinate reference system for later manipulation
census_data = census_data.to_crs(epsg=4326)

# Calculate the sum of the population in each census block, replacing empty values
census_data['sum_population'] = census_data['General_El'].replace(-999, 0) + census_data['Maori_Elec'].replace(-999, 0)

# Drop unnecessary columns from the bus stop and census dataframes
bus_stop_features.drop(columns=['highway', 'bus', 'network', 'network:wikidata', 'public_transport', 'shelter', 'bench', 'bin', 'lit', 'tactile_paving', 'local_ref', 'passenger_information_display', 'noname', 'covered', 'access', 'school_bus', 'capacity', 'not:network:wikidata'], inplace=True)
census_data.drop(columns=['MB2020_V2_', 'General_El', 'Maori_Elec', 'GED2020_V1', 'GED2020__1', 'GED2020__2', 'MED2020_V1', 'MED2020__1', 'MED2020__2', 'LAND_AREA_', 'AREA_SQ_KM', 'Shape_Leng'], inplace=True)

# Spatially join bus stop features with census data
joined_data = gpd.sjoin(bus_stop_features, census_data, how='left', predicate='within')

# Print the mean of the summed population in the joined data
print(joined_data['sum_population'].mean())

# Create an interactive map and save it as an HTML file
map_figure = joined_data.explore() # Requires folium, matplotlib, and mapclassify
map_figure.save('map.html') # Temporary: save to HTML to view, in future will be directly used
