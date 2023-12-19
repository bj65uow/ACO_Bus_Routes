from shapely.geometry import Point, LineString
import geopandas as gpd
import pandas as pd
import time
line_points = []
removed_points = []

# Set graph, and endpoints
def set_start(start_point, end_point, current_graph):
    line_points.append(start_point)
    global graph
    graph = current_graph.reset_index(drop=True)
    global end
    end = end_point

# Generate line
def run():
    i = 0
    while end not in line_points: # Can create limit to finish early by ANDing i < #
        i += 1
        print(str(i))
        near_points = select_nearby(line_points[-1])
        print(len(near_points))
        line_points.append(select_next(near_points))
    return LineString(line_points)

# Select the nearest 5 nodes to the current
def select_nearby(current_point):
    global graph
    global end
    global line_points
    graph = graph[graph['geometry'] != current_point].reset_index(drop=True)

    i = 1
    bus_stops_sindex = graph.sindex
    nearby_graph = graph.iloc[bus_stops_sindex.nearest(current_point)[1]]
    while i <= 4:
        i += 1
        bus_stops_sindex = graph.sindex
        nearest_point = graph.iloc[bus_stops_sindex.nearest(current_point)[1]]
        if(nearest_point.geometry.iloc[0] == end):
            line_points.append(end)
            break
        pd.concat([nearby_graph, nearest_point])
        graph = graph[graph['geometry'] != nearest_point['geometry'].iloc[0]].reset_index(drop=True)

    # Calculate distance to all points
    nearby_graph['distance'] = nearby_graph['geometry'].distance(current_point)

    # Select nearest 5
    nearby_graph = nearby_graph.sort_values(by='distance')
    return nearby_graph.head(5)

# ACO decide which node next
def select_next(current_graph):
    # ant decisions here TODO: pheromones, randomness, weighting by population
    # current_graph = current_graph.sort_values(by='sum_population')
    # return current_graph.geometry.iloc[0]
    global end
    current_graph['distance'] = current_graph['geometry'].distance(end)
    current_graph = current_graph.sort_values(by='distance')
    return current_graph.geometry.iloc[0]