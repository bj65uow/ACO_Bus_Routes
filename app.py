from flask import Flask, render_template, request, jsonify
from plot_nodes import plot_stops, plot_census
from create_display import generate_map
import aco
import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_stops')
def generate_stops():
    global stops
    stops = plot_stops()
    
    # Create leaflet
    figure = generate_map(stops)

    map_html = figure.get_root()._repr_html_()
    return map_html

@app.route('/generate_routes')
def generate_routes():
    global stops
    print('Adding population data')
    graph = plot_census(stops)

    print('Adding edges')
    G = aco.create_graph_with_distances(graph)

    start_nodes = request.args.getlist('start_node')
    end_nodes = request.args.getlist('end_node')

    num_ants = 10
    iterations = 10
    evaporation_rate = 0.2

    # Initialize an array to store the best paths
    best_paths = []

    # Iterate through each route
    for start_value, end_value in zip(start_nodes, end_nodes):
        source_node = aco.find_node(G, start_value)
        destination_node = aco.find_node(G, end_value)

        if source_node and destination_node is not None:
            best_path, best_distance = aco.ant_colony_optimisation(
                G, source_node, destination_node, num_ants, iterations, evaporation_rate
            )

            # Append the best path to the array
            best_paths.append(best_path)

    # Get line output for each best path
    lines = [LineString(path) for path in best_paths]
    line_gdf = gpd.GeoDataFrame(geometry=lines)

    # Display line_gdf and origin graph together
    graph = pd.concat([graph, line_gdf])

    # Create leaflet
    figure = generate_map(graph)

    map_html = figure.get_root()._repr_html_()
    return map_html

if __name__ == "__main__":
    app.run(debug=True)