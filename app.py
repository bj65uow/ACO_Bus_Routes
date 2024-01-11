from flask import Flask, render_template
from plot_nodes import plot
from create_display import generate_map
import aco
import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate')
def generate():
    graph = plot()

    # TODO: Update generate_line to use new algorithm
    # Hardcoded route start/end points
    start_point = (graph[graph['ref'] == '2401'])['geometry'].iloc[0]
    end_point = (graph[graph['ref'] == '2169'])['geometry'].iloc[0]
    source_coordinates = (176.167548, -37.682783)  # Replace with your source coordinates
    destination_coordinates = (176.331999, -37.720432)  # Replace with your destination coordinates

    G = aco.create_graph_with_distances(graph)

    source_node = aco.find_closest_node(G, source_coordinates)
    destination_node = aco.find_closest_node(G, destination_coordinates)

    print(f"Closest Source Node: {source_node}")
    print(f"Closest Destination Node: {destination_node}")


    num_ants = 10
    iterations = 10
    evaporation_rate = 0.2

    best_path, best_distance = aco.ant_colony_optimisation(
        G, source_node, destination_node, num_ants, iterations, evaporation_rate
    )

    # Get line output
    lines = [LineString(best_path)]
    gdf = gpd.GeoDataFrame(geometry=lines)
    graph = pd.concat([graph, gdf])

    # Create leaflet
    figure = generate_map(graph)

    map_html = figure.get_root()._repr_html_()
    return map_html

if __name__ == "__main__":
    app.run(debug=True)