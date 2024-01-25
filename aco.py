import networkx as nx
import random

from itertools import combinations
import osmnx as ox
from shapely.geometry import Point

import signal

stop_flag = False

def handle_interrupt(signum, frame):
    global stop_flag
    print('\nFinishing iteration')
    stop_flag = True

# Register the custom handler for Ctrl+C
signal.signal(signal.SIGINT, handle_interrupt)

def ant_colony_optimisation(
    graph, source, destination, num_ants, iterations, evaporation_rate, alpha=1, beta=5
):
    # Initialise pheromone levels
    pheromone_levels = {edge: 1.0 for edge in graph.edges()}

    # Best solution tracking
    best_solution = None
    best_distance = float("inf")

    i = 0
    global stop_flag
    for _ in range(iterations):
        # Allow early finish
        if stop_flag:
            break

        ant_paths = []
        # print("Iteration " + str(i))
        i += 1
        j = 1
        for ant in range(num_ants): 
            print('Iteration ' + str(i) + ', ant ' + str(j) + '  ', end='\r')
            j += 1
            # Ant movement
            ant_path = ant_move(
                graph, source, destination, pheromone_levels, alpha, beta
            )
            ant_paths.append((ant_path, calculate_path_distance(graph, ant_path)))

        # Pheromone update
        update_pheromone(graph, pheromone_levels, ant_paths, evaporation_rate)

        # Update best solution
        for path, distance in ant_paths:
            if distance < best_distance:
                best_solution = path
                best_distance = distance

    # Convert node labels to Shapely Point objects
    best_path_points = [Point(graph.nodes[node]['pos']) for node in best_solution]

    # Visualise the final result
    # visualise_result(graph, best_solution, pheromone_levels)

    return best_path_points, best_distance


# Ant movement
def ant_move(graph, source, destination, pheromone_levels, alpha, beta):
    current_node = source
    path = [current_node]
    visited_nodes = set()

    while current_node != destination:
        # Calculate probabilities for selecting the next node
        probabilities = calculate_probabilities(
            graph, current_node, destination, pheromone_levels, alpha, beta, visited_nodes
        )

        # Choose the next node based on probabilities
        next_node = choose_next_node(graph, current_node, probabilities)

        # Move to the next node
        current_node = next_node
        path.append(current_node)
        visited_nodes.add(current_node)

    return path

def calculate_probabilities(graph, current_node, destination, pheromone_levels, alpha, beta, visited_nodes, gamma=1, delta=0.2):
    neighbors = list(graph.neighbors(current_node))
    unvisited_neighbors = [neighbor for neighbor in neighbors if neighbor not in visited_nodes]
    probabilities = []

    # If there are unvisited neighbors, calculate probabilities for them
    if unvisited_neighbors:
        # Calculate probabilities for each unvisited neighbor
        for neighbor in unvisited_neighbors:
            pheromone = pheromone_levels.get(
                (current_node, neighbor),
                pheromone_levels.get((neighbor, current_node), 1.0),
            )

            distance_to_neighbour = graph[current_node][neighbor].get("weight", 1.0)

            population = graph.nodes[neighbor].get("sum_population", 60)
            normalised_pop = (population - 6) / (150 - 6)

            distance_to_origin = graph.nodes[current_node]['distance_to_origin']

            # Calculate the probability using the formula for ant movement
            probability = (pheromone**alpha) * ((1 / distance_to_neighbour) ** beta) * (normalised_pop ** gamma) * ((1 / distance_to_origin) ** delta)
            probabilities.append((neighbor, probability))

        # Normalize probabilities
        total_probability = sum(probability for _, probability in probabilities)
        if total_probability != 0:
            normalised_probabilities = [
                (neighbor, probability / total_probability)
                for neighbor, probability in probabilities
            ]
        else:
            # If total_probability is zero, assign equal probabilities to all neighbors
            equal_probability = 1.0 / len(unvisited_neighbors)
            normalised_probabilities = [(neighbor, equal_probability) for neighbor in unvisited_neighbors]
    else:
        # If all neighbors are visited, assign zero probability to all of them
        normalised_probabilities = [(neighbor, 0) for neighbor in neighbors]

    return normalised_probabilities



def choose_next_node(graph, current_node, probabilities):
    # Choose the next node based on probabilities
    selected_node = None
    random_value = random.uniform(0, 1)
    cumulative_probability = 0

    for neighbor, probability in probabilities:
        cumulative_probability += probability
        if random_value <= cumulative_probability:
            selected_node = neighbor
            break
    
    # If selected_node is still None, choose a random neighbor
    if selected_node is None and probabilities:
        selected_node = random.choice(probabilities)[0]

    return selected_node


def calculate_path_distance(graph, path):
    # Calculate the total distance of a path in the graph
    total_distance = 0

    # Iterate over the nodes in the path
    for i in range(len(path) - 1):
        current_node = path[i]
        next_node = path[i + 1]

        # Assuming the graph is weighted, get the edge weight
        edge_weight = graph[current_node][next_node].get("weight", 1.0)

        # Accumulate the distance
        total_distance += edge_weight

    return total_distance


def update_pheromone(graph, pheromone_levels, ant_paths, evaporation_rate, Q=1.0):
    # Evaporation: Update pheromone levels on all edges
    for edge in graph.edges():
        pheromone_levels[edge] *= 1 - evaporation_rate

    # Deposit pheromone on the edges of the best path found by each ant
    for ant_path, path_distance in ant_paths:
        pheromone_deposit = (
            Q / path_distance
        )  # Q is a constant representing the pheromone deposit
        for i in range(len(ant_path) - 1):
            try:
                edge = (
                    min(ant_path[i], ant_path[i + 1]),
                    max(ant_path[i], ant_path[i + 1]),
                )
                pheromone_levels[edge] += pheromone_deposit
            except KeyError:
                edge = (
                    max(ant_path[i], ant_path[i + 1]),
                    min(ant_path[i], ant_path[i + 1]),
                )
                pheromone_levels[edge]

def create_graph_with_distances(bus_stops):
    G = nx.Graph()

    for index, row in bus_stops.iterrows():
        G.add_node(row['ref'], pos=(row['geometry'].x, row['geometry'].y, row['sum_population']))

    nan_nodes = []
    for node in G.nodes():
        try:
            int(node)
        except ValueError:
            nan_nodes.append(node)
    G.remove_nodes_from(nan_nodes)

    # Add edges with distances and calculate the distance from the origin to each node
    for (node1, data1), (node2, data2) in combinations(G.nodes(data=True), 2):
        distance = ((data1['pos'][0] - data2['pos'][0]) ** 2 + (data1['pos'][1] - data2['pos'][1]) ** 2) ** 0.5
        G.add_edge(node1, node2, weight=distance)

    return G

def calc_origin_dist(G, origin):
    # Calculate the distance from the origin to each node
    for node in G.nodes():
        distance_to_origin = ((G.nodes[node]['pos'][0] - G.nodes[origin]['pos'][0]) ** 2 + (G.nodes[node]['pos'][1] - G.nodes[origin]['pos'][1]) ** 2) ** 0.5
        G.nodes[node]['distance_to_origin'] = distance_to_origin

    G.nodes[origin]['distance_to_origin'] = 1

    return G


# stops = plot_area()

# G = plot_census(stops)

# G = nx.Graph(G)

# # Example usage
# source_coordinates = (176.167548, -37.682783)  # Replace with your source coordinates
# destination_coordinates = (176.283595, -37.703196)  # Replace with your destination coordinates 176.3324474, -37.7205095

# source_node = find_node(G, source_coordinates)
# destination_node = find_node(G, destination_coordinates)

# print(f"Closest Source Node: {source_node}")
# print(f"Closest Destination Node: {destination_node}")


# num_ants = 20
# iterations = 15
# evaporation_rate = 0.2

# best_path, best_distance = ant_colony_optimisation(
#     G, source_node, destination_node, num_ants, iterations, evaporation_rate
# )
# # print(f"Best Path: {best_path}")
# print(f"Best Distance: {best_distance}")