from flask import Flask, render_template, request, jsonify
from plot_nodes import plot_stops, plot_census_stops, plot_census_intersections, plot_area, find_node, get_node, get_coords
from create_display import generate_map, generate_map_colour
import aco
import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString
import networkx as nx

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_stops')
def generate_stops():
    global stops
    stops = plot_stops()
    
    # Create leaflet
    colours = (['#ABABAB'] * len(stops.index))
    figure = generate_map_colour(stops, colours)

    map_html = figure.get_root()._repr_html_()
    return map_html

@app.route('/generate_routes')
def generate_routes():
    start_nodes = request.args.getlist('start_node')
    end_nodes = request.args.getlist('end_node')

    num_ants = request.args.get('num_ants', type=int)
    iterations = request.args.get('num_iterations', type=int)
    evaporation_rate = 0.2

    mode = request.args.get('mode')

    global stops

    # Initialize an array to store the best paths
    best_paths = []


    if (mode == 'bus_stops'):
        print('Adding population data')
        graph = plot_census_stops(stops)

        print('Adding edges')
        G = aco.create_graph_with_distances(graph)
    elif (mode == 'intersections'):
        print('Plotting roads (before population)')
        roads = plot_area()

        print('Adding population data')
        graph = plot_census_intersections(roads)

        print('Adding edges')
        G = nx.Graph(graph)
    else:
        print('ERROR: No mode')

    # Iterate through each route
    for start_value, end_value in zip(start_nodes, end_nodes):
        if(mode == 'bus_stops'):
            source_node = get_node(G, start_value)
            destination_node = get_node(G, end_value)
        elif(mode == 'intersections'):
            start = get_coords(stops, start_value)
            end = get_coords(stops, end_value)

            source_node = find_node(G, start)
            destination_node = find_node(G, end)

        if source_node and destination_node is not None:
            G = aco.calc_origin_dist(G, source_node)
            
            best_path, best_distance = aco.ant_colony_optimisation(
                G, source_node, destination_node, num_ants, iterations, evaporation_rate
            )

            # Append the best path to the array
            best_paths.append(best_path)

    # Get line output for each best path
    lines = [LineString(path) for path in best_paths]
    line_gdf = gpd.GeoDataFrame(geometry=lines)

    # Display line_gdf and origin graph together
    map = pd.concat([stops, line_gdf])

    # Create leaflet
    colours = (['#ABABAB'] * len(stops.index)) + (['blue', 'red', 'green'][:len(line_gdf.index)])
    figure = generate_map_colour(map, colours)

    map_html = figure.get_root()._repr_html_()
    return map_html

if __name__ == "__main__":
    app.run(debug=True)