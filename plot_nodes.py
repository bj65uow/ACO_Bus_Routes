# Importing GIS libraries
import osmnx as ox
import geopandas as gpd

# Download OSM bus stop map features for Tauranga
def download_bus_stop_features(bounds):
    bus_stop_features = ox.features_from_bbox(**bounds, tags={'highway': 'bus_stop'})
    bus_stop_features.drop(columns=['highway', 'bus', 'network', 'network:wikidata', 'public_transport', 'shelter', 'bench', 'bin', 'lit', 'tactile_paving', 'local_ref', 'passenger_information_display', 'noname', 'covered', 'access', 'school_bus', 'capacity', 'not:network:wikidata'], inplace=True)
    return bus_stop_features

# Read in population meshblock data,
# removing unnecessary data, and combining General and Māori electorate populations
def read_census_data(shapefile_path, bbox):
    census_data = gpd.read_file(shapefile_path, bbox=bbox)
    census_data = census_data.to_crs(epsg=4326) # Convert to standard coordinate reference system for easier manipulation
    census_data.drop(columns=['MB2020_V2_', 'GED2020_V1', 'GED2020__1', 'GED2020__2', 'MED2020_V1', 'MED2020__1', 'MED2020__2', 'LAND_AREA_', 'AREA_SQ_KM', 'Shape_Leng'], inplace=True)
    census_data['sum_population'] = census_data['General_El'].replace(-999, 0) + census_data['Maori_Elec'].replace(-999, 0)
    census_data.drop(columns=['General_El', 'Maori_Elec'], inplace=True)
    return census_data

# Spatially join population data to bus stops within meshblock
def process_data(bus_stop_features, census_data):
    joined_data = gpd.sjoin(bus_stop_features, census_data, how='left', predicate='within')
    return joined_data

def generate_map(joined_data):
    map_figure = joined_data.explore()  # Requires folium, matplotlib, and mapclassify
    return map_figure

def plot():
    # TODO: Remove hard coded values
    # Define map boundaries for Tauranga, New Zealand
    tauranga_bounds = {
        'north': -37.6039,
        'east': 176.5125,
        'south': -37.8114,
        'west': 176.0593
    }

    # Census data is in ESPG:2193, these bounds are similar to the ones above
    tauranga_bbox = (1869316.8619308192, 5810699.85703883, 1910089.458412611, 5832327.558897601)  # Format: min x, min y, max x, max y

    bus_stop_features = download_bus_stop_features(tauranga_bounds)

    # Read census data shapefile within the same boundaries
    census_shapefile_path = 'data/statsnz-2018-census-electoral-population-meshblock-2020-SHP/2018-census-electoral-population-meshblock-2020.shp'
    census_data = read_census_data(census_shapefile_path, tauranga_bbox)

    # Process and join data
    joined_data = process_data(bus_stop_features, census_data)

    # Calculate the mean of the summed population in the joined data
    # (may be used in future data)
    mean_pop = joined_data['sum_population'].mean()

    # Create an interactive map and save it as an HTML file
    return generate_map(joined_data)

if __name__ == "__main__":
    plot()
