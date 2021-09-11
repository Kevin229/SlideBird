import pygame, sys, random
import config
from pygame.locals import *
from gif_image import GIFImage

pygame.init()
pygame.font.init()
pygame.mixer.init()
fps_clock = pygame.time.Clock()
display_surface = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
pygame.display.set_caption('Slide Bird')
bird_slow_img = GIFImage(config.BIRD_SLOW_IMG)
bird_normal_img = GIFImage(config.BIRD_NORMAL_IMG)
bird_fast_img = GIFImage(config.BIRD_FAST_IMG)
introduce_game_sound = pygame.mixer.Sound(config.INTRODUCE_GAME)
bird_flap_sound = pygame.mixer.Sound(config.BIRD_FLAP)
game_over_sound = pygame.mixer.Sound(config.GAME_OVER)


class SlideBird():
    def __init__(self):
        self.width = config.BIRD_WIDTH
        self.height = config.BIRD_HEIGHT
        self.x_pos = (config.WINDOW_WIDTH - self.width) / 2
        self.y_pos = (config.WINDOW_HEIGHT - self.height) / 2
        self.speed = 0
        self.surface = bird_normal_img

    def draw(self):
        # if self.speed <= config.SPEED_LOW_NORMAL:
        #     self.surface = bird_slow_img
        # elif config.SPEED_LOW_NORMAL < self.speed <= config.SPEED_NORMAL_FAST:
        #     self.surface = bird_fast_img
        # else:
        #     pass
        self.surface.render(display_surface, (int(self.x_pos), int(self.y_pos)))

    def update(self, up_press, down_press):
        self.y_pos += self.speed + 0.5 * config.GRAVITY_EFFECT
        self.speed += config.GRAVITY_EFFECT
        if up_press:
            self.speed = -2
        if down_press:
            self.speed = 2
            pass


class Obstacle():
    def __init__(self):
        self.width = config.OBSTACLE_WIDTH
        self.height = config.OBSTACLE_HEIGHT
        self.blank = config.OBSTACLE_BLANK
        self.distance = config.OBSTACLE_DISTANCE
        self.speed = config.OBSTACLE_SPEED
        self.surface_obstacle = pygame.image.load(config.OBSTACLE_IMG)
        self.surface_nest = pygame.image.load(config.OBSTACLE_NEST_IMG)
        self.ls = []
        self.nest_ls = []
        for i in range(int(config.OBSTACLE_NUMBER_SCREEN)):
            x_pos = config.WINDOW_WIDTH + i * self.distance
            y_pos = random.randrange(60, config.WINDOW_HEIGHT - self.blank - 60, 50)
            self.ls.append([x_pos, y_pos])
            self.nest_ls.append(bool(random.getrandbits(1)))

    def draw(self):
        for i in range(int(config.OBSTACLE_NUMBER_SCREEN)):
            display_surface.blit(self.surface_obstacle, (self.ls[i][0], self.ls[i][1] - self.height))
            if self.nest_ls[i]:
                display_surface.blit(self.surface_nest, (self.ls[i][0], self.ls[i][1] + self.blank))
            else:
                display_surface.blit(self.surface_obstacle, (self.ls[i][0], self.ls[i][1] + self.blank))

    def update(self):
        for i in range(int(config.OBSTACLE_NUMBER_SCREEN)):
            self.ls[i][0] -= self.speed
        if self.ls[0][0] < -self.width:
            self.ls.pop(0)
            self.nest_ls.pop(0)
            x = self.ls[1][0] + self.distance
            y = random.randrange(60, config.WINDOW_HEIGHT - self.blank - 60, 50)
            self.ls.append([x, y])
            self.nest_ls.append(bool(random.getrandbits(1)))


def detect_collision(rect1, rect2):
    if rect1[0] <= rect2[0] + rect2[2] \
            and rect2[0] <= rect1[0] + rect1[2] \
            and rect1[1] <= rect2[1] + rect2[3] \
            and rect2[1] <= rect1[1] + rect1[3]:
        return True
    return False


def is_game_over(bird, obstacle):
    for i in range(3):
        rect_bird = [bird.x_pos, bird.y_pos, bird.width, bird.height]
        rect_obstacle1 = [obstacle.ls[i][0], obstacle.ls[i][1] - obstacle.height, obstacle.width, obstacle.height]
        rect_obstacle2 = [obstacle.ls[i][0], obstacle.ls[i][1] + obstacle.blank, obstacle.width, obstacle.height]
        if detect_collision(rect_bird, rect_obstacle1)\
                or detect_collision(rect_bird, rect_obstacle2):
            return True

    if bird.y_pos + bird.height < 0 \
            or bird.y_pos + bird.height > config.WINDOW_HEIGHT:
        return True
    return False


class Score():
    def __init__(self):
        self.score = 0
        self.addScore = True

    def draw(self):
        font = pygame.font.SysFont('consolas', 40)
        score_suface = font.render(str(self.score), True, (0, 0, 0))
        text_size = score_suface.get_size()
        display_surface.blit(score_suface, (int((config.WINDOW_WIDTH - text_size[0]) / 2), 100))

    def update(self, bird, columns):
        collision = False
        for i in range(3):
            rect_column = [columns.ls[i][0] + columns.width, columns.ls[i][1], 1, columns.blank]
            rect_bird = [bird.x_pos, bird.y_pos, bird.width, bird.height]
            if detect_collision(rect_bird, rect_column):
                collision = True
                break
        if collision:
            if self.addScore:
                self.score += 1
            self.addScore = False
        else:
            self.addScore = True


def game_start(bird):
    bird.__init__()
    font = pygame.font.SysFont('consolas', 60)
    heading_suface = font.render('SLIDE BIRD', True, (255, 0, 0))
    heading_size = heading_suface.get_size()

    font = pygame.font.SysFont('consolas', 20)
    comment_suface = font.render('Click to start', True, (0, 0, 0))
    comment_size = comment_suface.get_size()

    if pygame.mixer.Channel(0).get_busy():
        pygame.mixer.Channel(0).stop()
    if pygame.mixer.Channel(1).get_busy():
        pygame.mixer.Channel(1).stop()
    if pygame.mixer.Channel(2).get_busy():
        pygame.mixer.Channel(2).stop()
    pygame.mixer.Channel(0).play(introduce_game_sound, -1)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                return

        display_surface.fill(config.BACK_GROUND_COLOR)
        bird.draw()
        display_surface.blit(heading_suface, (int((config.WINDOW_WIDTH - heading_size[0]) / 2), 100))
        display_surface.blit(comment_suface, (int((config.WINDOW_WIDTH - comment_size[0]) / 2), 500))

        pygame.display.update()
        fps_clock.tick(config.FPS)


def game_play(bird, obstacles, score):
    bird.__init__()
    bird.speed = config.VELOCITY_DELTA
    obstacles.__init__()
    score.__init__()
    up_press = False
    down_press = False

    if pygame.mixer.Channel(0).get_busy():
        pygame.mixer.Channel(0).stop()
    if pygame.mixer.Channel(1).get_busy():
        pygame.mixer.Channel(1).stop()
    if pygame.mixer.Channel(2).get_busy():
        pygame.mixer.Channel(2).stop()
    pygame.mixer.Channel(1).play(bird_flap_sound, -1)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_w:
                    up_press = True
                if event.key == K_s:
                    down_press = True

        display_surface.fill(config.BACK_GROUND_COLOR)
        obstacles.draw()
        obstacles.update()

        bird.draw()
        bird.update(up_press, down_press)
        up_press = False
        down_press = False
        score.draw()
        score.update(bird, obstacles)

        if is_game_over(bird, obstacles):
            return

        pygame.display.update()
        fps_clock.tick(config.FPS)


def game_over(bird, obstacles, score):
    font = pygame.font.SysFont('consolas', 60)
    heading_suface = font.render('GAME OVER', True, (255, 0, 0))
    heading_size = heading_suface.get_size()

    font = pygame.font.SysFont('consolas', 20)
    comment_suface = font.render('Press "space" to replay', True, (0, 0, 0))
    comment_size = comment_suface.get_size()

    font = pygame.font.SysFont('consolas', 30)
    score_suface = font.render('Score: ' + str(score.score), True, (0, 0, 0))
    score_size = score_suface.get_size()

    if pygame.mixer.Channel(0).get_busy():
        pygame.mixer.Channel(0).stop()
    if pygame.mixer.Channel(1).get_busy():
        pygame.mixer.Channel(1).stop()
    if pygame.mixer.Channel(2).get_busy():
        pygame.mixer.Channel(2).stop()
    pygame.mixer.Channel(2).play(game_over_sound, -1)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYUP:
                if event.key == K_SPACE:
                    return

        display_surface.fill(config.BACK_GROUND_COLOR)
        obstacles.draw()
        bird.draw()
        display_surface.blit(heading_suface, (int((config.WINDOW_WIDTH - heading_size[0]) / 2), 100))
        display_surface.blit(comment_suface, (int((config.WINDOW_WIDTH - comment_size[0]) / 2), 500))
        display_surface.blit(score_suface, (int((config.WINDOW_WIDTH - score_size[0]) / 2), 160))

        pygame.display.update()
        fps_clock.tick(config.FPS)


def main():
    bird = SlideBird()
    obstacles = Obstacle()
    score = Score()
    while True:
        game_start(bird)
        game_play(bird, obstacles, score)
        game_over(bird, obstacles, score)
    pass


if __name__ == '__main__':
    main()
