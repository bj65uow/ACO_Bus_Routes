from shapely.geometry import Point, LineString
points = []

# Set graph, and endpoints
def set_start(start_point, end_point, current_graph):
    points.append(start_point)
    global graph
    graph = current_graph
    global end
    end = end_point

# Generate line
def run():
    i = 0
    while end not in points: # Can create limit to finish early by ANDing i < #
        i += 1
        print(str(i))
        near_points = select_nearby(points[-1])
        points.append(select_next(near_points))
    return LineString(points)

# Select the nearest 5 nodes to the current
def select_nearby(current_point):
    global graph

    # Calculate distance to all points
    graph['distance'] = graph['geometry'].distance(current_point)

    # Remove existing points
    graph = graph[~graph['geometry'].isin(points)]

    # Select nearest 5
    graph = graph.sort_values(by='distance')
    return graph.head(5)

# ACO decide which node next
def select_next(current_graph):
    # ant decisions here TODO: pheromones, randomness, weighting by population
    # current_graph = current_graph.sort_values(by='sum_population')
    # return current_graph.geometry.iloc[0]
    global end
    current_graph['distance'] = current_graph['geometry'].distance(end)
    current_graph = current_graph.sort_values(by='distance')
    return current_graph.geometry.iloc[0]