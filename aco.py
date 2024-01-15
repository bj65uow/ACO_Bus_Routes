import networkx as nx
import random

from itertools import combinations
import osmnx as ox
from shapely.geometry import Point

def ant_colony_optimisation(
    graph, source, destination, num_ants, iterations, evaporation_rate, alpha=1, beta=1
):
    # Initialise pheromone levels
    pheromone_levels = {edge: 1.0 for edge in graph.edges()}

    # Best solution tracking
    best_solution = None
    best_distance = float("inf")

    i = 0
    for _ in range(iterations):
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

    while current_node != destination:
        # Calculate probabilities for selecting the next node
        probabilities = calculate_probabilities(
            graph, current_node, destination, pheromone_levels, alpha, beta
        )

        # Choose the next node based on probabilities
        next_node = choose_next_node(graph, current_node, probabilities)

        # Move to the next node
        current_node = next_node
        path.append(current_node)

    return path

# TODO: Make probabilities match original paper
def calculate_probabilities(
    graph, current_node, destination, pheromone_levels, alpha, beta, gamma = 0
):
    neighbors = list(graph.neighbors(current_node))
    probabilities = []

    # Calculate probabilities for each neighbor
    for neighbor in neighbors:
        pheromone = pheromone_levels.get(
            (current_node, neighbor),
            pheromone_levels.get((neighbor, current_node), 1.0),
        )
        distance = graph[current_node][neighbor].get(
            "weight", 1.0
        )  # Assuming weighted graph

        # Add the "population" attribute to the calculation
        population = graph.nodes[neighbor].get("sum_population", 60)
        normalised_pop = (population - 6)/(150-6)

        # Calculate the probability using the formula for ant movement
        probability = (pheromone**alpha) * ((1 / distance) ** beta) * (normalised_pop ** gamma)
        probabilities.append((neighbor, probability))

    # Normalize probabilities
    total_probability = sum(probability for _, probability in probabilities)
    normalised_probabilities = [
        (neighbor, probability / total_probability)
        for neighbor, probability in probabilities
    ]

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
    # Create a NetworkX graph and add nodes
    G = nx.Graph()
    for index, row in bus_stops.iterrows():
        G.add_node(row['ref'])

    nan_nodes = []
    for node in G.nodes():
        try:
            int(node)
        except ValueError:
            nan_nodes.append(node)
    G.remove_nodes_from(nan_nodes)

    # Add node attributes
    pos_dict = {row['ref']: (row['geometry'].x, row['geometry'].y, row['sum_population']) for index, row in bus_stops.iterrows()}
    nx.set_node_attributes(G, pos_dict, 'pos')

    # Add edges with distances
    for (node1, data1), (node2, data2) in combinations(G.nodes(data=True), 2):
        distance = (
            ((data1['pos'][0] - data2['pos'][0])**2 + (data1['pos'][1] - data2['pos'][1])**2)**0.5
        )
        G.add_edge(node1, node2, weight=distance)

    return G


def find_node(graph, target_node):
    # min_distance = float('inf')
    # closest_node = None

    # for node, data in graph.nodes(data=True):
    #     node_coordinates = data['pos']
    #     distance = ((node_coordinates[0] - target_coordinates[0])**2 + (node_coordinates[1] - target_coordinates[1])**2)**0.5

    #     if distance < min_distance:
    #         min_distance = distance
    #         closest_node = node

    # return closest_node
    if target_node in graph.nodes:
        return target_node
    else:
        print(target_node + "not found")

# # Example usage
# source_coordinates = (176.167548, -37.682783)  # Replace with your source coordinates
# destination_coordinates = (176.283595, -37.703196)  # Replace with your destination coordinates

# source_node = find_closest_node(G, source_coordinates)
# destination_node = find_closest_node(G, destination_coordinates)

# print(f"Closest Source Node: {source_node}")
# print(f"Closest Destination Node: {destination_node}")


# num_ants = 10
# iterations = 10
# evaporation_rate = 0.2

# best_path, best_distance = ant_colony_optimisation(
#     G, source_node, destination_node, num_ants, iterations, evaporation_rate
# )
# # print(f"Best Path: {best_path}")
# print(f"Best Distance: {best_distance}")