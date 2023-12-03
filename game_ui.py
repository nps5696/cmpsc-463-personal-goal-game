import math
import sys
import pygame


# Main loop

def run_game(goals):

    def get_next_tasks(task_name='', score=0):
        # get start task
        if task_name == '':
            for task in goals.tasks:
                if task.completed is not False:
                    return task.name
        else:
            print("task_name received:", task_name)
            next_tasks = []
            for task in goals.tasks:
                print("Checking task for matching, name:", task.name, "with received task name:", task_name)
                # set completed to true
                if task.name == task_name:
                    print("Found the task, name:", task.name, "marking as completed, now:", task.completed)
                    task.completed = True
                    print("Current score:", score)
                    score += task.points
                    print("New score:", score)
                    print("now completed:", task.completed)
                # find next taxt using task name within their dependencies
                print("Verifying task:", task.name, "which has dependencies:", task.dependencies)


                if task_name in task.dependencies:
                    print("********* Found task which has:", task_name, "as prereq, adding new task name:", task.name)
                    #if task.dependencies:
                    next_tasks.append(task.name)
            return next_tasks, score

    ####
    # Initialize Pygame
    pygame.init()
    pygame.mixer.init()

    # Set up the display
    width = 800
    hight = 600
    screen = pygame.display.set_mode((width, hight))
    global music_playing
    music_playing = True

    # Setup sounds
    button_click_sound = pygame.mixer.Sound("sounds/click.mp3")

    # Play background music
    pygame.mixer.music.load("sounds/gameplay_2.mp3")
    pygame.mixer.music.play(-1)

    def toggle_music():
        global music_playing
        if music_playing:
            pygame.mixer.music.stop()
        else:
            pygame.mixer.music.play(-1)
        music_playing = not music_playing

    # Define colors
    WHITE = (255, 255, 255)
    BLUE = (0, 0, 255)
    RED = (255, 0, 0)

    # Create a font object
    font = pygame.font.Font(None, 20)
    heading_font = pygame.font.Font(None, 40)
    font = pygame.font.Font(None, 20)

    # Circle properties for main button
    #circle_center = [400, 300]
    #circle_centers = [[350, 350], [400, 350], [450, 350]]
    circle_radius = 50

    # Popup options
    popup_options = ["Complete", "Back", "Finish"]
    popup_visible = False
    popups = []
    popup_animating = False
    animation_step = 0
    score = 0

    # Function to draw a circular button
    def draw_button(name='', circle_center=()):
        print(circle_center)
        pygame.draw.circle(screen, BLUE, circle_center, circle_radius)
        text = font.render('Task:' + name, True, WHITE)
        text_rect = text.get_rect(center=circle_center)
        screen.blit(text, text_rect)

    def draw_buttons(tasks):
        #print(circle_center)
        circle_centers = []
        for i, task in enumerate(tasks):
            circle_center = [int(400 - 120 * (i+1)), 450]
            pygame.draw.circle(screen, BLUE, circle_center, circle_radius)
            text = font.render(task, True, WHITE)
            text_rect = text.get_rect(center=circle_center)
            screen.blit(text, text_rect)
            circle_centers.append(circle_center)

        return circle_centers

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
    def is_inside_circle(point, circle_centers):
        x, y = point
        within = False
        circle = []
        for circle_center in circle_centers:
            print("x,y", x, y)
            distance = math.sqrt((x - circle_center[0]) ** 2 + (y - circle_center[1]) ** 2)
            print("circle_center, circle_radius, distance", circle_center, circle_radius, distance)
            if distance < circle_radius:
                within = True
                circle = circle_center

        print("within, circle", within, circle)
        return within, circle

    def show_game_over(score, time_taken):
        game_over_window = pygame.display.set_mode((400, 200))
        pygame.display.set_caption("Game Over")

        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        time_text = font.render(f"Time Taken: {time_taken} seconds", True, (255, 255, 255))

        game_over_window.blit(score_text, (50, 50))
        game_over_window.blit(time_text, (50, 100))

        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.time.Clock().tick(60)

    def draw_blinking_text(screen, font, text, color, position, blink_interval):
        current_time = pygame.time.get_ticks()

        if current_time % (2 * blink_interval) < blink_interval:
            # Draw the text only during the first half of the blink interval
            text_surface = font.render(text, True, color)
            screen.blit(text_surface, position)

    ####

    running = True
    next_tasks = ["Start"]
    if not next_tasks:
        next_tasks = "Start"
    circle_centers = draw_buttons(next_tasks)
    while running:

        # Clear the screen
        screen.fill((0, 0, 0))  # Fill with a background color (adjust as needed)

        circle_centers = draw_buttons(next_tasks)
        current_time = pygame.time.get_ticks()

        # Render and display blinking text
        draw_blinking_text(screen, heading_font, "Goal: " + goals.name, (255, 255, 0), (10, 110),
                           blink_interval=500)  # Adjust blink_interval as needed

        # Render and display "GAME is ON" at the top center
        game_on_text = heading_font.render("GAME is ON", True, (255, 0, 0))
        game_on_rect = game_on_text.get_rect(center=(width // 2, 30))
        screen.blit(game_on_text, game_on_rect)


        # Convert milliseconds to seconds
        seconds = current_time // 1000
        milliseconds = current_time % 1000


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:

                # Check if the mouse click is on the music toggle button 600, 20, 120, 50
                if 600 <= event.pos[0] <= 720 and 20 <= event.pos[1] <= 70:
                    button_click_sound.play()
                    toggle_music()

                within , circle_center = is_inside_circle(event.pos, circle_centers)
                if within:
                    button_click_sound.play()


                    # Retrieve the name of the clicked button based on the circle_center
                    clicked_button_name = next_tasks[circle_centers.index(circle_center)]
                    print("Clicked button:", clicked_button_name)

                    print("hey there! Current task is", [ i for i in next_tasks])
                    #name='Start'

                    if clicked_button_name:
                        if clicked_button_name == 'Finish' or clicked_button_name == 'finish':
                            running = False
                        else:
                            next_tasks, score = get_next_tasks(clicked_button_name, score)
                    else:
                        next_tasks, score = get_next_tasks(next_tasks)
                    print("next_tasks", next_tasks)
                    if next_tasks:
                        for i, next_task in enumerate(next_tasks):
                            print("i:", i)


                            circle_centers = draw_buttons(next_tasks)

                elif popup_visible:
                    for rect in popups:
                        if rect.collidepoint(event.pos):
                            print(f"{popup_options[popups.index(rect)]} clicked!")


        # Render and display the music toggle button
        pygame.draw.rect(screen, (0, 255, 0), (600, 20, 120, 50))  # Green rectangle as the button
        button_text = font.render("Music ON/OFF", True, (255, 255, 255))
        screen.blit(button_text, (610, 25))

        score_text = heading_font.render(f"Score: {score}", True, (255, 255, 0))
        screen.blit(score_text, (10, 50))

        # Render and display current time with milliseconds below the score
        time_text = heading_font.render(f"Time: {seconds} s", False, (255, 255, 0))
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

    # show window with scores and time
    pygame.mixer.music.stop()

    show_game_over(score, seconds)

pygame.quit()
