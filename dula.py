import pygame
import random
import randomQuiz

pygame.init()
screen = pygame.display.set_mode((800, 400))
pygame.display.set_caption("Dodge Quiz")
clock = pygame.time.Clock()
for_font = pygame.font.Font(None, 24)
title_font = pygame.font.Font(None, 48)

bg_image = pygame.image.load("FreeImageBG/nature_2/natOrig.png").convert()
bg_image = pygame.transform.scale(bg_image, (800, 400))

main_menu = ["1. Start Game", "2. Highest Score", "3. Help"]
choosing = 0
player = pygame.Rect(200, 200, 10, 35) # (x, y, width, height)

# 3 monsters staggered so they don't all arrive at once
monsters = [
    pygame.Rect(800,  random.randint(10, 375), 15, 15),
    pygame.Rect(1000, random.randint(10, 375), 15, 15),
    pygame.Rect(1200, random.randint(10, 375), 15, 15),
]

monster_speed = 4
score = 0

current_screen = "menu"
current_question = ""
current_answer = ""
player_input = ""
feedback = ""
feedback_timer = 0

# ----- Random Question Trigger -----
def trigger_question():
    """Pick a random question from randomQuiz and return (question, answer)."""
    idx = random.randint(0, len(randomQuiz.questions) - 1)
    return randomQuiz.questions[idx], randomQuiz.answers[idx]

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.KEYDOWN:

            # --- Menu controls ---
            if current_screen == "menu":
                if event.key == pygame.K_UP:
                    choosing = (choosing - 1) % len(main_menu)
                elif event.key == pygame.K_DOWN:
                    choosing = (choosing + 1) % len(main_menu)
                elif event.key == pygame.K_RETURN:
                    if choosing == 0:
                        current_screen = "game"
                    elif choosing == 1:
                        current_screen = "scores"
                    elif choosing == 2:
                        current_screen = "help"

            # --- Question screen controls ---
            elif current_screen == "question":
                if event.key == pygame.K_RETURN:
                    if player_input.strip():  # only proceed if answer is not blank
                        if player_input.strip().lower() == current_answer.strip().lower():
                            # Add a new monster on correct answer
                            offset = len(monsters) * 200
                            monsters.append(
                                pygame.Rect(800 + offset, random.randint(10, 375), 15, 15)
                            )
                            feedback = f"Correct! +1 Monster! ({len(monsters)} total)"
                        else:
                            feedback = f"Wrong! Answer: {current_answer}"
                        feedback_timer = 120  # 120 frames = ~2 seconds at 60fps
                        player_input = ""
                        current_screen = "feedback"  # go to dedicated feedback screen
                        # Respawn all monsters so player isn't immediately hit again
                        for i, m in enumerate(monsters):
                            m.x = 800 + i * 200
                            m.y = random.randint(10, 375)
                elif event.key == pygame.K_BACKSPACE:
                    player_input = player_input[:-1]
                else:
                    if event.unicode and event.unicode.isprintable():
                        player_input += event.unicode

            # --- Game / Scores / Help ---
            else:
                if event.key == pygame.K_ESCAPE:
                    current_screen = "menu"

    screen.blit(bg_image, (0, 0))

    if current_screen == "menu":
        title = title_font.render("Dodge Quiz", True, "cyan")
        screen.blit(title, (300, 20))

        for i, options in enumerate(main_menu):
            color = 'yellow' if i == choosing else 'white'
            display_menu = for_font.render(options, False, color)
            screen.blit(display_menu, (300, 100 + i * 40))

    elif current_screen == "game":
        pygame.draw.rect(screen, "white", player)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            player.move_ip(0, -8)# (x, y)
        if keys[pygame.K_DOWN]:
            player.move_ip(0, 8)

        if player.top < 0:
            player.top = 0
        if player.bottom > 400:
            player.bottom = 400

        hit_this_frame = False
        for m in monsters:
            pygame.draw.rect(screen, "red", m)
            m.move_ip(-monster_speed, 0)

            if m.right < 0:
                m.x = 800
                m.y = random.randint(10, 375)
                score += 1  # player successfully dodged this monster
                if score % 4 == 0:
                    monster_speed = min(monster_speed + 0.50, 16)

            # --- Collision: switch to question screen (only once per frame) ---
            if not hit_this_frame and player.colliderect(m):
                hit_this_frame = True
                current_question, current_answer = trigger_question()
                player_input = ""
                current_screen = "question"
                # Respawn all monsters so they don't collide again immediately
                for i, other in enumerate(monsters):
                    other.x = 800 + i * 200
                    other.y = random.randint(10, 375)

        # Show current speed
        speed_text = for_font.render(f"Speed: {monster_speed:.1f}", True, "orange")
        screen.blit(speed_text, (10, 10))

        # Show score
        score_text = for_font.render(f"Score: {score}", True, "orange")
        screen.blit(score_text, (10, 40))

        back = for_font.render("Press ESC to return to menu", True, "gray")
        screen.blit(back, (260, 375))

    # ===================== QUESTION =====================
    elif current_screen == "question":
        q_title = title_font.render("Question!", True, "yellow")
        screen.blit(q_title, (400 - q_title.get_width() // 2, 20))

        score_text = for_font.render(f"Score: {score}", True, "orange")
        screen.blit(score_text, (10, 40))

        # Word-wrap the question
        words = current_question.split()
        lines, line = [], ""
        for word in words:
            test = line + word + " "
            if for_font.size(test)[0] > 740:
                lines.append(line)
                line = word + " "
            else:
                line = test
        lines.append(line)

        for j, l in enumerate(lines):
            q_surf = for_font.render(l, True, "white")
            screen.blit(q_surf, (30, 100 + j * 28))

        # Input box
        pygame.draw.rect(screen, "white", (30, 220, 740, 35), 2)
        input_surf = for_font.render(player_input + "|", True, "cyan")
        screen.blit(input_surf, (38, 230))

        hint = for_font.render("Type your answer and press ENTER", True, "gray")
        screen.blit(hint, (400 - hint.get_width() // 2, 275))

        if not player_input.strip():
            warn = for_font.render("Please type an answer first!", True, "red")
            screen.blit(warn, (400 - warn.get_width() // 2, 305))

    # ===================== FEEDBACK =====================
    elif current_screen == "feedback":
        if feedback_timer > 0:
            feedback_timer -= 1
        else:
            current_screen = "game"  # auto-continue after timer runs out

        fb_color = "green" if feedback.startswith("Correct") else "red"
        fb_title = title_font.render(feedback, True, fb_color)
        screen.blit(fb_title, (400 - fb_title.get_width() // 2, 160))

        secs_left = max(1, (feedback_timer // 60) + 1)
        countdown = for_font.render(f"Returning to game in {secs_left}...", True, "gray")
        screen.blit(countdown, (400 - countdown.get_width() // 2, 230))

    # ===================== SCORES =====================
    elif current_screen == "scores":
        heading = title_font.render("High Scores", True, "orange")
        screen.blit(heading, (260, 80))
        hint = for_font.render("Scores content goes here...", True, "white")
        screen.blit(hint, (270, 160))
        back = for_font.render("Press ESC to return to menu", True, "gray")
        screen.blit(back, (260, 350))

    # ===================== HELP =====================
    elif current_screen == "help":
        heading = title_font.render("Help", True, "violet")
        screen.blit(heading, (340, 80))
        hint = for_font.render("Help content goes here...", True, "white")
        screen.blit(hint, (270, 160))
        back = for_font.render("Press ESC to return to menu", True, "gray")
        screen.blit(back, (260, 350))

    pygame.display.update()
    clock.tick(60)