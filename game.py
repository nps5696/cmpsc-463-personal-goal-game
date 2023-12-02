import json
import uuid
import tkinter as tk
import numpy as np
from tkinter import simpledialog, messagebox, StringVar, filedialog
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from game_ui import run_game
import threading


graph_window = None
canvas = None
ax = None


class Task:
    def __init__(self, name, points, completed=False, dependencies=[]):
        self.id = str(uuid.uuid4())  # Generate a unique ID
        self.name = name
        self.points = points
        self.completed = False
        self.dependencies = dependencies


    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'points': self.points,
            'completed': self.completed,
            'dependencies': self.dependencies
        }

    @staticmethod
    def from_dict(data):
        task = Task(data['name'], data['points'], data['completed'], data['dependencies'])
        #task.id = data['id']
        #task.completed = data['completed']
        return task


class Goal:
    def __init__(self, name, reward):
        self.id = str(uuid.uuid4())  # Generate a unique ID
        self.name = name
        self.reward = reward
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def add_start_task(self):
        start_task = Task("Start", 0, [])
        self.tasks.append(start_task)
        print("Initial Start task has been added to the new Goal!")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'reward': self.reward,
            'tasks': [task.to_dict() for task in self.tasks]
        }

    @staticmethod
    def from_dict(data):
        goal = Goal(data['name'], data['reward'])
        goal.id = data['id']

        for task_data in data['tasks']:
            goal.add_task(Task.from_dict(task_data))
            # print("taks data: ", str(Task.from_dict(task_data).dependencies))
        return goal


def save_goal(goal, filename):
    with open(filename, 'w') as file:
        json.dump(goal.to_dict(), file, indent=4)


def load_goal(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
        return Goal.from_dict(data)


def save_goal_as(goal):
    if goal is None:
        messagebox.showinfo("No Goal", "No goal to save.")
        return

    filename = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON files", "*.json"), ("All Files", "*.*")],
        title="Save Goal As"
    )
    if filename:
        save_goal(goal, filename)


def load_goal_from():
    filename = filedialog.askopenfilename(
        filetypes=[("JSON files", "*.json"), ("All Files", "*.*")],
        title="Open Goal"
    )
    if filename:
        return load_goal(filename)


def build_graph(goal):
    # Create a directed graph using NetworkX
    graph = nx.DiGraph()

    # Add nodes based on tasks
    for task in goal.tasks:
        graph.add_node(task.id, name=task.name, points=task.points, completed=task.completed, dependencies=task.dependencies)
        print(task.id, task.name, task.points, task.completed, task.dependencies, "\n")

    # Add edges based on tasks and their dependencies
    for task in goal.tasks:
        # if task.dependencies:
        #     for dep_uuid in task.dependencies:
        #         dep_task = next((t for t in goal.tasks if t.id == dep_uuid), None)
        #         if dep_task:
        #             graph.add_edge(dep_task.id, task.id, weight=task.points, task_name=task.name)
        #             print("adding dependency to task:", task.id, dep_task.id, task.name, task.points)

        if task.dependencies:
            # edge_weight = task.points
            for dep in task.dependencies:
                graph.add_edge(task.id, dep, weight=task.points, task_name=task.name)
                print("adding dependency to task:", task.id, dep, task.name, task.points)
                # graph.add_edge(dep, task.id, weight=task.points, name=task.name)
                # print(graph.edges)

    # Print nodes with attributes
    print("Nodes total:", len(graph.nodes()))
    for node, data in graph.nodes(data=True):
        name = data.get('name', 'Unknown')
        print(f"{node} ({name})")

    return graph


def draw_graph(goal, ax, path):
    # Build the graph
    graph = build_graph(goal)

    print("graph.edges:", graph.edges())
    # Clear the axes for the new plot
    ax.clear()

    # Draw the graph
    print(graph.nodes())
    pos = nx.spring_layout(graph)
    nx.draw(graph, pos, with_labels=True, font_weight='bold', node_size=1000, node_color='skyblue')
    node_labels = nx.get_node_attributes(graph, 'name')
    nx.draw_networkx_labels(graph, pos, labels=node_labels)

    print("path:", path)
    if path:
        ax.clear()
        # Highlight the shortest path
        path_edges = list(zip(path, path[1:]))
        nx.draw_networkx_edges(graph, pos, edgelist=path_edges, edge_color='red', width=2, ax=ax)
        nx.draw_networkx_nodes(graph, pos, nodelist=path, node_color='lightgreen', node_size=2000, ax=ax)


def show_graph(goal, graph_window, path=None):
    # graph_window = tk.Toplevel()
    graph_window.title("Task Dependency Graph")

    # Create a frame for the graph
    frame = tk.Frame(graph_window)
    frame.pack(fill=tk.BOTH, expand=True)

    # Create a matplotlib figure
    fig, ax = plt.subplots(figsize=(6, 4))

    # Embed the graph in the Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(fill=tk.BOTH, expand=True)

    # Draw or redraw the graph
    draw_graph(goal, ax, path)
    canvas.draw()


def add_task(goals):
    # Function to add tasks via GUI
    task_name = simpledialog.askstring("Task Name", "Enter the task name:")
    if task_name:
        task_points = simpledialog.askinteger("Task Points", "Enter the points for this task:")
        if task_points is not None:

            # Create a dictionary to map task names to UUIDs
            task_name_to_uuid = {task.name: task.id for task in goals.tasks}

            # Open the task dependency window after entering task points
            def on_dependency_selected():
                task_prereq = task_var.get()
                if task_prereq != "Select Prerequisite Task":
                    print("task_name_to_uuid[task_prereq]:", task_name_to_uuid[task_prereq])
                    new_task = Task(task_name, task_points, False, [task_name_to_uuid[task_prereq]])
                    goals.add_task(new_task)
                    messagebox.showinfo("Task Added", f"Task '{task_name}' added successfully!")
                    task_window.destroy()
                else:
                    messagebox.showwarning("No Selection", "Please select a prerequisite task or cancel.")

            task_window = tk.Toplevel()
            task_window.title("Update Task Dependency")


            # Dropdown for selecting a task
            task_var = StringVar(task_window)
            task_var.set("Select Prerequisite Task")
            #task_menu = tk.OptionMenu(task_window, task_var, *["Select Prerequisite Task"] + [task.name for task in goals.tasks])
            task_menu = tk.OptionMenu(task_window, task_var, *["Select Prerequisite Task"] + list(task_name_to_uuid.keys()))

            task_menu.pack()

            # Button to confirm the selection
            confirm_button = tk.Button(task_window, text="Confirm", command=on_dependency_selected)
            confirm_button.pack()

def add_goal(goals):
    # Function to add goals via GUI
    goal_name = simpledialog.askstring("Goal Name", "Enter the goal name:")
    if goal_name:
        goal_reward = simpledialog.askstring("Goal Reward", "Enter the reward for this goal:")
        if goal_reward:
            new_goal = Goal(goal_name, goal_reward)
            new_goal.add_start_task()
            goals.append(new_goal)
            messagebox.showinfo("Goal Added", f"Goal '{goal_name}' added successfully!")


def update_goal(goals, tasks):
    print("goals:", [ goal.name for goal in goals ])
    #goal_tasks = [task for task in [ goal.tasks for goal in goals ]]
    print("tasks:", [[task.name for task in goal.tasks] for goal in goals])
    if not goals: #or not goals.tasks:
        messagebox.showinfo("Update Goal", "No goals or tasks to update.")
        return

    update_window = tk.Toplevel()
    update_window.title("Update Goal with Task")

    # Dropdown for selecting a goal
    goal_var = StringVar(update_window)
    goal_var.set("Select a Goal")
    goal_menu = tk.OptionMenu(update_window, goal_var, *[goal.name for goal in goals])
    goal_menu.pack()

    # Dropdown for selecting a task
    task_var = StringVar(update_window)
    task_var.set("Select a Task")
    task_menu = tk.OptionMenu(update_window, task_var, *[task.name for task in tasks])
    task_menu.pack()

    def associate_task():
        selected_goal = next((goal for goal in goals if goal.name == goal_var.get()), None)
        selected_task = next((task for task in tasks if task.name == task_var.get()), None)
        if selected_goal and selected_task:
            selected_goal.add_task(selected_task)
            messagebox.showinfo("Success", f"Task '{selected_task.name}' added to Goal '{selected_goal.name}'")
        else:
            messagebox.showerror("Error", "Invalid goal or task selected.")

    # Button to associate the selected task with the selected goal
    associate_button = tk.Button(update_window, text="Associate Task with Goal", command=associate_task)
    associate_button.pack()


def display_progress(goal):
    if goal is None:
        messagebox.showinfo("No Goal", "No goal has been set.")
        return

    progress_window = tk.Toplevel()
    progress_window.title("Progress for Goal: " + goal.name)

    total_points = sum(task.points for task in goal.tasks)
    completed_points = sum(task.points for task in goal.tasks if task.completed)
    progress_label = tk.Label(progress_window, text=f"Total Progress: {completed_points} / {total_points} points")
    progress_label.pack()

    for task in goal.tasks:
        status = "Completed" if task.completed else "Pending"
        task_label = tk.Label(progress_window, text=f"Task: {task.name}, Points: {task.points}, Status: {status}")
        task_label.pack()

def edit_task_dependency(goal):
    if goal is None or not goal.tasks:
        messagebox.showinfo("No Tasks", "There are no tasks to edit.")
        return

    def on_confirm():
        selected_task_name = task_var.get()
        selected_prereq_name = prereq_var.get()

        if selected_task_name == "Select Task" or selected_prereq_name == "Select Prerequisite Task":
            messagebox.showwarning("No Selection", "Please select a task and a prerequisite.")
            return

        selected_task = next((task for task in goal.tasks if task.name == selected_task_name), None)
        if selected_task:
            selected_task.dependencies.append(selected_prereq_name)
            messagebox.showinfo("Task Updated", f"Prerequisite '{selected_prereq_name}' added to Task '{selected_task_name}'")
            edit_window.destroy()

    edit_window = tk.Toplevel()
    edit_window.title("Edit Task Dependencies")

    task_var = tk.StringVar(edit_window)
    task_var.set("Select Task")
    task_menu = tk.OptionMenu(edit_window, task_var, *["Select Task"] + [task.name for task in goal.tasks])
    task_menu.pack()

    prereq_var = tk.StringVar(edit_window)
    prereq_var.set("Select Prerequisite Task")
    prereq_menu = tk.OptionMenu(edit_window, prereq_var, *["Select Prerequisite Task"] + [task.name for task in goal.tasks])
    prereq_menu.pack()

    confirm_button = tk.Button(edit_window, text="Confirm", command=on_confirm)
    confirm_button.pack()




# def dijkstras_min_points_path(goal):
#
#
# # Example usage
# # Assuming 'goal' is an instance of Goal with tasks having 'name' and 'points' attributes
# path = dijkstras_min_points_path(goal)
# print("Path from Start to Finish with minimum points:", path)


def find_case_insensitive_node(G, node_name):
    for node in G.nodes:
        if node.lower() == node_name.lower():
            return node
    return None

def calculate_path(goal, graph_window):

    #print("Data:", [task.name for task in goal.tasks])
    if goal is None or not goal.tasks:
        messagebox.showinfo("No Data", "There are no goals or tasks.")
        return
    # Dijkstra's algorithm to find the optimal path
    G = nx.DiGraph()

    # Add nodes and edges with points as weights
    for task in goal.tasks:
        print("Adding task:", task.name)
        G.add_node(task.name)
        if task.dependencies:
            for dep in task.dependencies:
                # print(f"adding neighbor node {dep} to our current {task.name}, edge weight is {task.points}")
                # use the points as the weight for the edge
                G.add_edge(dep, task.name, weight=task.points)

    #print("Print G graph:", nx.write_adjlist(G, "graph.adjlist"))

    print(G.nodes())
    start_node = find_case_insensitive_node(G, "Start")
    finish_node = find_case_insensitive_node(G, "Finish")

    # ###
    # G = nx.DiGraph()
    #
    # # Add nodes and edges based on tasks and their dependencies
    # for task in goal.tasks:
    #     G.add_node(task.name)
    #     if task.dependencies:
    #         for dep in task.dependencies:
    #             G.add_edge(dep, task.name)
    # ###

    # Check if "Start" and "Finish" nodes exist
    if start_node is not None and finish_node is not None:
        path = nx.shortest_path(G, source=start_node, target=finish_node, weight='weight')
        path_weight = sum(G[path[i]][path[i + 1]]['weight'] for i in range(len(path) - 1))

        print("Shortest path:", path, "weight:", path_weight)
        show_graph(goal, graph_window, path)
        return path
    else:
        raise ValueError("Start or Finish node not present in the graph")


def main():
    # Main application window
    root = tk.Tk()
    root.title("Personal Achievement as a Game")
    root.geometry("1024x786")
    button_frame = tk.Frame(root)
    button_frame.pack(side=tk.RIGHT, fill=tk.Y)
    button_width = 20
    #goal = Goal()
    goals = []
    #tasks = []

    label = tk.Label(root, text="")
    label.pack()

    def display_string():
        # Update the label's text when the button is clicked
        label.config(text="Hello There!")

    def start_game_and_close_root(root, goals):
        if len(goals) == 0:
            messagebox.showinfo("No Goal", "Goal has not been set. Please create or load goal.")
            return
        root.destroy()  # Close the Tkinter window
        run_game(goals[-1])  # Start the Pygame game

    # Add buttons and bind them to their respective functions
    tk.Button(button_frame, text="Add Goal", command=lambda: add_goal(goals), width=button_width).pack()
    tk.Button(button_frame, text="Add Task", command=lambda: add_task(goals[-1] if goals else None), width=button_width).pack()
    tk.Button(button_frame, text="Show Progress", command=lambda: display_progress(goals[-1] if goals else None), width=button_width).pack()
    tk.Button(button_frame, text="Calculate Path", command=lambda: calculate_path(goals[-1] if goals else None, root), width=button_width).pack()
    # tk.Button(button_frame, text="Update Goal", command=lambda: update_goal(goals), width=button_width).pack()
    tk.Button(button_frame, text="Show Tasks Graph", command=lambda: show_graph(goals[-1] if goals else None, root), width=button_width).pack()
    # Add Save and Load buttons
    tk.Button(button_frame, text="Save Goal", command=lambda: save_goal_as(goals[-1] if goals else None), width=button_width).pack()
    tk.Button(button_frame, text="Load Goal", command=lambda: goals.append(load_goal_from()), width=button_width).pack()
    tk.Button(button_frame, text="Click to display string", command=display_string, width=button_width).pack()
    tk.Button(button_frame, text="Edit Task Dependency", command=lambda: edit_task_dependency(goals[-1] if goals else None), width=button_width).pack()
    tk.Button(button_frame, text="Play Game", command=lambda: start_game_and_close_root(root, goals), width=button_width).pack()


    root.mainloop()


if __name__ == "__main__":
    main()
