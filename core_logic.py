####
# Nikolay Sizov
# nps5696@psu.edu
# Dijkstra's heap
####

import heapq

class Graph:

    def __init__(self):
        self.graph = {}

    def add_edges(self, graph_items):
        for node in graph_items:

            # if node doesn't exist create one as dict of lists
            if node[0] != '' and node[1] != '':

                if node[0] not in self.graph:
                    self.graph[node[0]] = []

                if node[1] not in self.graph:
                    self.graph[node[1]] = []

            # # attach nodes make a directioinal edge
            self.graph[node[0]].append((node[1], node[2]))
    def get_node_neighbors(self, node):
        if self.graph[node]:
            return self.graph[node]
        else:
            #print("Neighbor nodes not found!")
            return ''


    def print_graph(self):
        # dump all list items
        for key, value in self.graph.items():
            #print("Node:", key, "connects to:", [i for i in value])
            # more efficient?
            print("Node:", key, "connects to:", str(value))

    def dijkstra(self, start_node):
        # heap based dijkstra
        # Creates a dictionary to hold the distances
        distances = {key: float('inf') for key, value in self.graph.items()}
        distances[start_node] = 0

        previous_vertices = {key: None for key, value in self.graph.items()}

        # Creates a priority queue to store the vertices to visit next, ordered by their tentative distances
        priority_queue = [(0, start_node)]

        while len(priority_queue) > 0:

            curr_distance, curr_vertex = heapq.heappop(priority_queue)
            #print("curr_vertex: ", curr_vertex)

            # # find neighbors
            curr_neighbors = self.get_node_neighbors(curr_vertex)

            for neighbor, weight in curr_neighbors:
                distance = curr_distance + weight

                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    # Stores the distance of the city and the neighbor nodes of the city
                    heapq.heappush(priority_queue, (distance, neighbor))

        return distances

G = Graph()

graph_items = [
    ['A', 'B', 215],
    ['A', 'C', 105],
    ['A', 'D', 307],
    ['B', 'E', 94],
    ['B', 'F', 188],
    ['B', 'A', 215],
    ['E', 'F', 102],
    ['E', 'H', 142],
    ['F', 'H', 38],
    ['D', 'N', 201],
]

G.add_edges(graph_items)
#G.print_graph()

print("shortest paths: ", G.dijkstra('A'))