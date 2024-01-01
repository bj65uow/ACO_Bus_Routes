import networkx as nx
import random
import matplotlib.pyplot as plt


def ant_colony_optimization(
    graph, source, destination, num_ants, iterations, evaporation_rate, alpha=1, beta=1
):
    # Initialize pheromone levels
    pheromone_levels = {edge: 1.0 for edge in graph.edges()}

    # Best solution tracking
    best_solution = None
    best_distance = float("inf")

    i = 0
    for _ in range(iterations):
        ant_paths = []
        print("Iteration " + str(i))
        i += 1
        for ant in range(num_ants):
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

    # Visualize the final result
    visualize_result(graph, best_solution, pheromone_levels)

    return best_solution, best_distance


def visualize_result(graph, best_path, pheromone_levels):
    plt.figure(figsize=(10, 8))

    # Plot the graph
    pos = nx.spring_layout(graph)
    nx.draw(graph, pos, with_labels=True)

    # Highlight the best path
    edges = [(best_path[i], best_path[i + 1]) for i in range(len(best_path) - 1)]
    nx.draw_networkx_edges(graph, pos, edgelist=edges, edge_color="r", width=2)

    # Display edge weights
    edge_labels = {
        (
            edge[0],
            edge[1],
        ): f'{pheromone:.2f}\n{graph[edge[0]][edge[1]].get("weight", 1.0):.2f}'
        for edge, pheromone in pheromone_levels.items()
    }
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)

    # Save or show the plot
    plt.title("Ant Colony Optimization - Final Result")
    plt.show()


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


def calculate_probabilities(
    graph, current_node, destination, pheromone_levels, alpha, beta
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

        # Calculate the probability using the formula for ant movement
        probability = (pheromone**alpha) * ((1 / distance) ** beta)
        probabilities.append((neighbor, probability))

    # Normalize probabilities
    total_probability = sum(probability for _, probability in probabilities)
    normalized_probabilities = [
        (neighbor, probability / total_probability)
        for neighbor, probability in probabilities
    ]

    return normalized_probabilities


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
            edge = (
                min(ant_path[i], ant_path[i + 1]),
                max(ant_path[i], ant_path[i + 1]),
            )
            pheromone_levels[edge] += pheromone_deposit


# Example usage
G = nx.complete_graph(20)  # Replace with your graph
# Add random weights to the edges
for edge in G.edges():
    G[edge[0]][edge[1]]["weight"] = random.uniform(
        1, 100
    )  # Replace the range as needed

source_node = 0
destination_node = 19
num_ants = 20
iterations = 100
evaporation_rate = 0.1

best_path, best_distance = ant_colony_optimization(
    G, source_node, destination_node, num_ants, iterations, evaporation_rate
)
print(f"Best Path: {best_path}")
print(f"Best Distance: {best_distance}")