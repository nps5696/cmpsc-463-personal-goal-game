import pygame
import math



# Main loop

def run_game(goals):

    def get_next_tasks(goals):
        for task in goals.tasks:
            if task.completed is not False:
                return task.name

    ####
    # Initialize Pygame
    pygame.init()
    pygame.mixer.init()

    # Set up the display
    width = 800
    hight = 600
    screen = pygame.display.set_mode((width, hight))

    # Setup sounds
    button_click_sound = pygame.mixer.Sound("sounds/click.mp3")
    game_sound = pygame.mixer.Sound("sounds/gameplay.wav")
    # Play background music
    pygame.mixer.music.load("sounds/gameplay.wav")
    pygame.mixer.music.play(-1)

    # Define colors
    WHITE = (255, 255, 255)
    BLUE = (0, 0, 255)
    RED = (255, 0, 0)

    # Create a font object
    font = pygame.font.Font(None, 36)

    # Circle properties for main button
    circle_center = (400, 300)
    circle_radius = 50

    # Popup options
    popup_options = ["Complete", "Back", "Finish"]
    popup_visible = False
    popups = []
    popup_animating = False
    animation_step = 0
    score = 0

    # Function to draw a circular button
    def draw_button():
        pygame.draw.circle(screen, BLUE, circle_center, circle_radius)
        text = font.render('Task:' + get_next_tasks(goals), True, WHITE)
        text_rect = text.get_rect(center=circle_center)
        screen.blit(text, text_rect)

    # Function to draw popup options
    def draw_popups():
        x, y = circle_center
        for i, option in enumerate(popup_options):
            offset = min(animation_step, 50)  # Change 100 to control the sliding distance
            rect = pygame.Rect(x + 60 + offset, y + (i * 35) - 35, 100, 30)
            pygame.draw.rect(screen, RED, rect)
            text = font.render(option, True, WHITE)
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)
            if animation_step == 0:
                popups.append(rect)

    # Check if a point is inside the circle
    def is_inside_circle(point):
        x, y = point
        distance = math.sqrt((x - circle_center[0]) ** 2 + (y - circle_center[1]) ** 2)
        return distance < circle_radius
    ####

    running = True
    draw_button()
    while running:

        current_time = pygame.time.get_ticks()

        ## Get current time in milliseconds
        #current_time = pygame.time.get_ticks() - start_time

        # Convert milliseconds to seconds
        seconds = current_time // 1000
        milliseconds = current_time % 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if is_inside_circle(event.pos):
                    button_click_sound.play()
                    popup_visible = not popup_visible
                    popup_animating = True
                    animation_step = 0
                    popups = []
                    if popup_visible:
                        draw_popups()
                elif popup_visible:
                    for rect in popups:
                        if rect.collidepoint(event.pos):
                            print(f"{popup_options[popups.index(rect)]} clicked!")

        # Render and display "GAME is ON" at the top center
        game_on_text = font.render("GAME is ON", True, (255, 0, 0))
        game_on_rect = game_on_text.get_rect(center=(width // 2, 30))
        screen.blit(game_on_text, game_on_rect)

        score_text = font.render(f"Score: {score}", True, (255, 255, 0))
        screen.blit(score_text, (10, 50))

        # Render and display current time with milliseconds below the score
        time_text = font.render(f"Time: {seconds} s {milliseconds} ms", True, (255, 255, 0))
        screen.blit(time_text, (10, 80))

        if popup_animating:
            screen.fill((0, 0, 0))  # Clear screen
            draw_button()
            draw_popups()
            animation_step += 5  # Change the speed of the animation
            if animation_step > 100:  # Stop the animation after a certain point
                popup_animating = False

        pygame.display.flip()

        pygame.time.Clock().tick(60)

pygame.quit()
