import tkinter as tk
from tkinter import simpledialog, messagebox
import math
import heapq

class Graph:
    def __init__(self):
        self.graph = {}
        self.nodes = {}  # Stores coordinates of nodes
        self.node_names = {}  # Maps node IDs to names
        self.node_loes = {}  # Maps node IDs to LOE
        self.node_counter = 0

    def add_node(self, name, x, y, loe):
        node_id = self.node_counter
        self.nodes[node_id] = (x, y)
        self.node_names[node_id] = name
        self.node_loes[node_id] = loe
        self.graph[node_id] = []
        self.node_counter += 1
        return node_id

    def add_edge(self, start, end):
        if start in self.graph and end in self.graph:
            self.graph[start].append(end)
            self.graph[end].append(start)  # Assuming undirected graph

    def get_edges(self):
        edges = []
        for node in self.graph:
            for neighbor in self.graph[node]:
                if (node, neighbor) and (neighbor, node) not in edges:  # Avoid duplicate edges
                    edges.append(f"({self.node_names[node]} - {self.node_loes[node]}, {self.node_names[neighbor]} - {self.node_loes[neighbor]})")
        return edges

    def dijkstra(self, start):
        distances = {node: float('infinity') for node in self.graph}
        distances[start] = 0
        predecessors = {node: None for node in self.graph}

        pq = [(0, start)]
        while pq:
            current_distance, current_node = heapq.heappop(pq)

            if current_distance > distances[current_node]:
                continue

            for neighbor in self.graph[current_node]:
                distance = current_distance + self.node_loes[neighbor]
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    predecessors[neighbor] = current_node
                    heapq.heappush(pq, (distance, neighbor))

        return distances, predecessors

    def get_path(self, predecessors, start, end):
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = predecessors[current]
        path.reverse()
        return path if path[0] == start else []  # Return empty if no path found

class GraphUI:
    def __init__(self, graph):
        self.graph = graph
        self.root = tk.Tk()
        self.root.title("Graph Builder")

        self.canvas = tk.Canvas(self.root, width=600, height=400, bg='white')
        self.canvas.pack(padx=10, pady=10)

        self.selected_node = None

        self.canvas.bind("<Button-1>", self.canvas_click)
        tk.Button(self.root, text="Finish and Show Edges", command=self.finish_graph).pack(padx=10, pady=10)

        tk.Button(self.root, text="Find Shortest Path from 'start' to 'finish'", command=self.find_shortest_path).pack(padx=10, pady=10)

    def find_shortest_path(self):
        # Find node IDs for 'start' and 'finish'
        start_id = finish_id = None
        for node_id, name in self.graph.node_names.items():
            if name == 'start':
                start_id = node_id
            elif name == 'finish':
                finish_id = node_id

        if start_id is None or finish_id is None:
            messagebox.showerror("Error", "Start or finish node not found.")
            return

        distances, predecessors = self.graph.dijkstra(start_id)

        if distances[finish_id] == float('infinity'):
            messagebox.showinfo("Result", "No path found from 'start' to 'finish'.")
            return

        path = self.graph.get_path(predecessors, start_id, finish_id)
        self.highlight_path(path)

    def canvas_click(self, event):
        clicked_node = self.find_node_at(event.x, event.y)
        if clicked_node is not None:
            if self.selected_node is None:
                self.selected_node = clicked_node
            else:
                self.graph.add_edge(self.selected_node, clicked_node)
                self.selected_node = None
                self.redraw_canvas()
        else:
            node_name = simpledialog.askstring("Node Name", "Enter node name:", parent=self.root)
            if node_name:
                loe = simpledialog.askstring("Level of Effort", "Enter LOE for this node:", parent=self.root)
                if loe and loe.isdigit():
                    node_id = self.graph.add_node(node_name, event.x, event.y, int(loe))
                    self.draw_node(event.x, event.y, node_id)

    def find_node_at(self, x, y):
        for node_id, (node_x, node_y) in self.graph.nodes.items():
            if math.sqrt((node_x - x) ** 2 + (node_y - y) ** 2) < 15:
                return node_id
        return None

    def draw_node(self, x, y, node_id):
        name = self.graph.node_names[node_id]
        loe = self.graph.node_loes[node_id]
        self.canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill="blue")
        self.canvas.create_text(x, y, text=f"{name}\n(LOE: {loe})")

    def redraw_canvas(self):
        self.canvas.delete("all")
        for node_id, (x, y) in self.graph.nodes.items():
            self.draw_node(x, y, node_id)
        for start, ends in self.graph.graph.items():
            start_x, start_y = self.graph.nodes[start]
            for end in ends:
                end_x, end_y = self.graph.nodes[end]
                self.canvas.create_line(start_x, start_y, end_x, end_y)

    def finish_graph(self):
        edges = self.graph.get_edges()
        print("Edges in the graph:", edges)
        messagebox.showinfo("Graph Edges", "\n".join(edges))

    def run(self):
        self.root.mainloop()

# Example usage
graph = Graph()
gui = GraphUI(graph)
gui.run()
