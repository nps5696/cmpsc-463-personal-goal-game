import pygame
import math

# Initialize Pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((800, 600))

# Colors and Fonts
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
font = pygame.font.Font(None, 36)

# Graph Data
nodes = []
edges = []
selected_node = None
popup_menu = None
level = 1

# Node Radius and Popup Menu Properties
NODE_RADIUS = 10
POPUP_WIDTH = 100
POPUP_HEIGHT = 30
POPUP_OPTIONS = ["Add Node", "Option 2", "Option 3"]

# Define Node Class
class Node:
    def __init__(self, position, level):
        self.position = position
        self.level = level

    def draw(self):
        color = RED if self == selected_node else BLUE
        pygame.draw.circle(screen, color, self.position, NODE_RADIUS)
        text = font.render(str(self.level), True, BLUE)
        screen.blit(text, (self.position[0] + 15, self.position[1] - 10))

    def is_clicked(self, pos):
        distance = math.sqrt((self.position[0] - pos[0]) ** 2 + (self.position[1] - pos[1]) ** 2)
        return distance < NODE_RADIUS

# Popup Menu Class
class PopupMenu:
    def __init__(self, position):
        self.position = position
        self.options = POPUP_OPTIONS
        self.rects = [pygame.Rect(position[0], position[1] + i * POPUP_HEIGHT, POPUP_WIDTH, POPUP_HEIGHT) for i in range(len(self.options))]

    def draw(self):
        for i, rect in enumerate(self.rects):
            pygame.draw.rect(screen, RED, rect)
            text = font.render(self.options[i], True, WHITE)
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)

    def get_clicked_option(self, pos):
        for i, rect in enumerate(self.rects):
            if rect.collidepoint(pos):
                return self.options[i]
        return None


# Function to draw nodes and edges
def draw_graph():
    for edge in edges:
        pygame.draw.line(screen, BLACK, edge[0].position, edge[1].position, 2)
    for node in nodes:
        node.draw()


# Main game loop
running = True
level = 1
while running:
    screen.fill(WHITE)
    draw_graph()

    if popup_menu:
        popup_menu.draw()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if clicking on an existing node
            clicked_node = None
            for node in nodes:
                if node.is_clicked(event.pos):
                    clicked_node = node
                    break

            if clicked_node:
                if clicked_node == selected_node:
                    selected_node = None
                else:
                    selected_node = clicked_node
            else:
                # Add new node
                new_node = Node(event.pos, level)
                nodes.append(new_node)
                if selected_node:
                    edges.append((selected_node, new_node)) #!!!!
                selected_node = new_node
                level += 1

    pygame.display.flip()

pygame.quit()
