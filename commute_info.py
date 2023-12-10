# Importing GIS libraries
import geopandas as gpd

# Define map boundaries for Tauranga, New Zealand
tauranga_bounds = {
    "north": -37.6039,
    "east": 176.5125,
    "south": -37.8114,
    "west": 176.0593,
}

# Census data is in ESPG:2193, these bounds are similar to the ones above
tauranga_bbox = (
    1869316.8619308192,
    5810699.85703883,
    1910089.458412611,
    5832327.558897601,
)  # Format: min x, min y, max x, max y

# Load the geographical data from a shapefile and convert it to WGS84 coordinate reference system
statistical_area_data = gpd.read_file(
    "data/statsnz-statistical-area-2-2018-generalised-SHP/statistical-area-2-2018-generalised.shp",
    bbox=tauranga_bbox,
)
statistical_area_data = statistical_area_data.to_crs(4326)

# Extract unique statistical areas
statistical_areas = statistical_area_data["SA22018__1"].unique().tolist() # Statistical area 2 place name column

# Load census data and filter based on statistical areas
census_data = gpd.read_file(
    "data/statsnz-2018-census-main-means-of-travel-to-work-by-statistical-area-CSV/2018-census-main-means-of-travel-to-work-by-statistical-area.csv"
)
census_data = census_data[
    census_data["SA2_name_usual_residence_address"].isin(statistical_areas) # Is SA2 place name
]

# Drop unnecessary columns from the census data
census_data_filtered = census_data.drop(
    columns=[
        "SA2_code_usual_residence_address",
        "SA2_usual_residence_easting",
        "SA2_usual_residence_northing",
        "SA2_code_workplace_address",
        "SA2_workplace_easting",
        "SA2_workplace_northing",
        "Work_at_home",
        "Drive_a_private_car_truck_or_van",
        "Drive_a_company_car_truck_or_van",
        "Passenger_in_a_car_truck_van_or_company_bus",
        "Public_bus",
        "Train",
        "Bicycle",
        "Walk_or_jog",
        "Ferry",
        "Other",
        "geometry",
    ]
)

# Display the filtered census data
print("All commutes:")
print(census_data_filtered)

# Calculate and display arrival counts for each statistical area
arrival_counts = [["Area", "Arrivals"]]
for area in statistical_areas:
    count = sum(
        (census_data[census_data["SA2_name_workplace_address"] == area])["Total"] # Is SA2 place name
    )
    arrival_counts.append([area, str(count)])

# Print number of people arriving in each area
print(arrival_counts)

print("Number of statistical areas:", len(statistical_areas))
