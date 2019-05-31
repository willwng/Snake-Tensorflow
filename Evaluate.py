import keras
import pygame
import random
import numpy as np
from numpy import genfromtxt

#file_name = str(input("Enter Model: ")) + '.model'
#print("Read CSV from: ", file_name)
#fit_model = genfromtxt(file_name, delimiter=',')
fit_model = keras.models.load_model('FittedModel.model')

pygame.init()
FPS = 5

screen_width, screen_height = 640, 480
screen = pygame.display.set_mode((screen_width, screen_height), 0, 32)
surface = pygame.Surface(screen.get_size())
surface = surface.convert()
surface.fill((255, 255, 255))

grid_size = 20
grid_width = screen_width / grid_size
grid_height = screen_height / grid_size
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

screen.blit(surface, (0, 0))


def draw_box(surf, color, pos):
    r = pygame.Rect((pos[0], pos[1]), (grid_size, grid_size))
    pygame.draw.rect(surf, color, r)


class Snake(object):
    def __init__(self):
        self.lose()
        self.color = (0, 0, 0)

    def get_head_position(self):
        return self.positions[0]

    def lose(self):
        self.length = 3
        self.positions = [((screen_width / 2), (screen_height / 2))]
        self.direction = RIGHT

    def point(self, pt):
        if self.length > 1 and (pt[0] * -1, pt[1] * -1) == self.direction:
            return
        else:
            self.direction = pt

    def move(self):
        game_run = True
        cur = self.positions[0]
        x, y = self.direction
        # new = (((cur[0] + (x * grid_size)) % screen_width), (cur[1] + (y * grid_size)) % screen_height)

        new = (((cur[0] + (x * grid_size))), (cur[1] + (y * grid_size)))
        if cur[0] >= screen_width or cur[1] >= screen_height:
            self.lose()
            game_run = False

        if cur[0] <= 0 or cur[1] <= 0:
            game_run = False
            self.lose()
        if len(self.positions) > 2 and new in self.positions[2:]:
            game_run = False
            self.lose()
        else:
            self.positions.insert(0, new)
            if len(self.positions) > self.length:
                self.positions.pop()
        return game_run

    def draw(self, surf):
        for p in self.positions:
            draw_box(surf, self.color, p)


class Apple(object):
    def __init__(self):
        self.position = (0, 0)
        self.color = (255, 0, 0)
        self.randomize()

    def randomize(self):
        self.position = (random.randint(1, grid_width - 2) * grid_size, random.randint(1, grid_height - 2) * grid_size)

    def draw(self, surf):
        draw_box(surf, self.color, self.position)


def play_game():
    move = [0, 1, 0, 0]
    snake = Snake()
    score = snake.length
    apple = Apple()
    while True:
        body_left_1, body_left_2, body_left_3 = 0, 0, 0
        body_right_1, body_right_2, body_right_3 = 0, 0, 0
        body_up_1, body_up_2, body_up_3 = 0, 0, 0
        body_down_1, body_down_2, body_down_3 = 0, 0, 0
        for body in snake.positions:
            if body[0] == snake.get_head_position()[0]:
                if body[1] == snake.get_head_position()[1] - grid_size:
                    body_up_1 = 1
                elif body[1] == snake.get_head_position()[1] - grid_size * 2:
                    body_up_2 = 1
                elif body[1] == snake.get_head_position()[1] - grid_size * 3:
                    body_up_3 = 1
                elif body[1] == snake.get_head_position()[1] + grid_size:
                    body_down_1 = 1
                elif body[1] == snake.get_head_position()[1] + grid_size * 2:
                    body_down_2 = 1
                elif body[1] == snake.get_head_position()[1] + grid_size * 3:
                    body_down_3 = 1
            if body[1] == snake.get_head_position()[1]:
                if body[0] == snake.get_head_position()[0] - grid_size:
                    body_left_1 = 1
                elif body[0] == snake.get_head_position()[0] - grid_size * 2:
                    body_left_2 = 1
                elif body[0] == snake.get_head_position()[0] - grid_size * 3:
                    body_left_3 = 1
                elif body[0] == snake.get_head_position()[0] + grid_size:
                    body_right_1 = 1
                elif body[0] == snake.get_head_position()[0] + grid_size * 2:
                    body_right_2 = 1
                elif body[0] == snake.get_head_position()[0] + grid_size * 3:
                    body_right_3 = 1

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize()
        #              #
        #    DRAWING   #
        #              #
        surface.fill((255, 255, 255))
        snake.draw(surface)
        apple.draw(surface)
        screen.blit(surface, (0, 0))
        pygame.display.flip()
        pygame.display.update()
        pygame.time.Clock().tick(FPS)
        #              #
        #  OBSERVATION #
        #              #
        apple_x = (snake.get_head_position()[0] - apple.position[0]) / screen_width
        apple_y = (snake.get_head_position()[1] - apple.position[1]) / screen_height
        left_wall = (snake.get_head_position()[0]) / screen_width
        right_wall = (640 - snake.get_head_position()[0]) / screen_width
        top_wall = (snake.get_head_position()[1]) / screen_height
        bottom_wall = (480 - snake.get_head_position()[1]) / screen_height
        body_left = [body_left_1, body_left_2, body_left_3]
        body_right = [body_right_1, body_right_2, body_right_3]
        body_up = [body_up_1, body_up_2, body_up_3]
        body_down = [body_down_1, body_down_2, body_down_3]
        observation = [apple_x, apple_y, left_wall, right_wall, top_wall, bottom_wall]
        observation.extend(body_left)
        observation.extend(body_right)
        observation.extend(body_up)
        observation.extend(body_down)
        observation = np.array(observation)
        action = np.argmax(fit_model.predict(observation.reshape(-1, len(observation)))[0])
        print(observation, fit_model.predict(observation.reshape(-1, len(observation)))[0])
        if action == 0:
            snake.point(LEFT)
        elif action == 1:
            snake.point(RIGHT)
        elif action == 2:
            snake.point(UP)
        elif action == 3:
            snake.point(DOWN)
        game_running = snake.move()
        if not game_running:
            break


play_game()
