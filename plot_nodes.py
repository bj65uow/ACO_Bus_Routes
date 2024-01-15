# Importing GIS libraries
import osmnx as ox
import geopandas as gpd
from requests import Request
from owslib.wfs import WebFeatureService


# Download OSM bus stop map features for Tauranga
def download_bus_stop_features(bounds):
    bus_stop_features = ox.features_from_bbox(
        **bounds, tags={"highway": "bus_stop"}
    )  # Retrieve all bus stops
    bus_stop_features.drop(
        columns=[
            "highway",
            "bus",
            "network",
            "network:wikidata",
            "public_transport",
            "shelter",
            "bench",
            "bin",
            "lit",
            "tactile_paving",
            "local_ref",
            "passenger_information_display",
            "noname",
            "covered",
            "access",
            "school_bus",
            "capacity",
            "not:network:wikidata",
        ],
        inplace=True,
    )  # Many empty fields

    # Bus stops taken from BOPRC API, OSM is similar enough and can be applied to anywhere
    # bus_stop_features = gpd.read_file('https://gis.boprc.govt.nz/server2/rest/services/BayOfPlentyMaps/Community/MapServer/3/query?where=1%3D1&outFields=BusStopName,BusStopID,ZoneID,StopLatitude,StopLongitude&outSR=4326&f=json') # They scrape from Google Maps?
    # bus_stop_features = bus_stop_features[bus_stop_features['ZoneID'].isin('BOP00_1A', 'BOP00_2A', 'BOP00_2B')] # Tauranga Urban, Te Puke, Katikati/Ōmokoroa/Bethlehem
    return bus_stop_features


# Read in population meshblock data,
# removing unnecessary data, and combining General and Māori electorate populations
def read_census_data(bbox):
    # URL for WFS backend
    url = "https://datafinder.stats.govt.nz/services;key=1f0a305f72954361a9b5a7aa6750f2db/wfs"

    # Initialize
    wfs = WebFeatureService(url=url)

    # Fetch the census population layer
    layer_name = "layer-104578"

    # Specify the parameters for fetching the data
    params = dict(
        service="WFS",
        version="2.0.0",
        request="GetFeature",
        typeName=layer_name,
        outputFormat="json",
        SRSName="EPSG:4326",
        BBOX=f'{bbox["west"]},{bbox["south"]},{bbox["east"]},{bbox["north"]},EPSG:4326',
    )  # Bounds, minX, minY, maxX, maxY
    # Parse the URL with parameters
    wfs_request_url = Request("GET", url, params=params).prepare().url

    # Read data from URL
    census_data = gpd.read_file(wfs_request_url)

    # Now retreived from API
    # census_data = gpd.read_file(shapefile_path, bbox=bbox)
    # census_data = census_data.to_crs(epsg=4326)  # Convert to standard coordinate reference system for easier manipulation

    # Remove unneeded data
    census_data = census_data[
        ["General_Electoral_Population", "Maori_Electoral_Population", "geometry"]
    ]

    census_data["sum_population"] = census_data["General_Electoral_Population"].replace(
        -999, 0
    ) + census_data["Maori_Electoral_Population"].replace(
        -999, 0
    )  # 'General_Electorial_Population' (General_El in shape file) = population count on general roll column, 'Maori_Electorial_Population' (Maori_Elec in shape file) = population count on Māori roll column
    census_data.drop(
        columns=["General_Electoral_Population", "Maori_Electoral_Population"],
        inplace=True,
    )
    return census_data


# Spatially join population data to bus stops within meshblock
def process_data(bus_stop_features, census_data):
    joined_data = gpd.sjoin(
        bus_stop_features, census_data, how="left", predicate="within"
    )
    return joined_data


# Create geodataframe with bus stops/population data
def plot_stops():
    # TODO: Remove hard coded values
    # Define map boundaries for Tauranga, New Zealand
    tauranga_bounds = {
        "north": -37.6039,
        "east": 176.5125,
        "south": -37.8114,
        "west": 176.0593,
    }

    bus_stop_features = download_bus_stop_features(tauranga_bounds)

    return bus_stop_features

def plot_census(stops):
    # TODO: Remove hard coded values
    # Define map boundaries for Tauranga, New Zealand
    tauranga_bounds = {
        "north": -37.6039,
        "east": 176.5125,
        "south": -37.8114,
        "west": 176.0593,
    }

    # Read census data shapefile within the same boundaries
    census_data = read_census_data(tauranga_bounds)

    # Process and join data
    joined_data = process_data(stops, census_data)

    # Calculate the mean of the summed population in the joined data
    # (may be used in future data)
    #mean_pop = joined_data["sum_population"].mean()

    # Create an interactive map and save it as an HTML file
    return joined_data



# if __name__ == "__main__":
#     from create_display import generate_map

#     figure = generate_map(plot())
