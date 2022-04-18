import sys
import pygame as pg
from pygame.math import Vector2
from enum import Enum, auto
import random

SCREEN_W, SCREEN_H = 800, 600
BACKGROUND_COLOR = pg.Color(50, 50, 50)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
PLAYER_SIZE = SCREEN_W * 0.2


class GameState(Enum):
    idle = auto()
    running = auto()


class Entity:
    def __init__(self, left, top, width, height, direction: Vector2 = Vector2(0, 0), speed=10):
        self.rect = pg.Rect(left, top, width, height)
        self.speed = speed
        self.direction = direction

    def update(self):
        raise NotImplementedError

    def move(self):
        if self.direction.length() > 1:
            self.direction = self.direction.normalize()
        self.rect.center += self.direction * self.speed

    def is_collide_with(self, rect: pg.Rect):
        return self.rect.colliderect(rect)

    def _lock_in_screen_bound(self):
        self.rect.top = max(self.rect.top, 0)
        self.rect.bottom = min(self.rect.bottom, SCREEN_H)


class Player(Entity):
    def update(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_UP]:
            self.direction.y = -1
        elif keys[pg.K_DOWN]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        self.move()
        self._lock_in_screen_bound()


class Enemy(Entity):
    def update(self, entity: Entity):
        target_pos = entity.rect
        self.direction.y = (target_pos.y - self.rect.centery) / self.speed
        self.move()
        self._lock_in_screen_bound()


class Ball(Entity):
    def update(self):
        self.move()
        if self.rect.y <= 0:
            self.rect.y = abs(self.rect.y)
            self.direction.y *= -1
        elif self.rect.y >= SCREEN_H:
            self.rect.y -= (self.rect.y - SCREEN_H)
            self.direction.y *= -1

    def reflect_if_collide(self, entity: Entity):
        if self.is_collide_with(entity.rect):
            if self.rect.x != entity.rect.x:
                self.rect.x -= self.direction.x * self.speed
                self.direction.x *= -1
                return True
        return False


class Game:
    def __init__(self):
        self.window = pg.display.set_mode((SCREEN_W, SCREEN_H))
        self.clock = pg.time.Clock()
        self.state = GameState.idle

    def initialize(self):
        a = random.choice((-1, 1))
        b = random.choice((-1, 1))
        self.ball = Ball(SCREEN_W / 2, SCREEN_H / 2, 20, 20, direction=Vector2(a, b), speed=10)
        self.player = Player(10, SCREEN_H / 2 - PLAYER_SIZE / 2, 10, PLAYER_SIZE)
        self.enemy = Enemy(SCREEN_W - 20, SCREEN_H / 2 - PLAYER_SIZE / 2, 10, PLAYER_SIZE)

    def render(self):
        self.window.fill(BACKGROUND_COLOR)    # clear
        pg.draw.rect(self.window, WHITE, self.player)
        pg.draw.rect(self.window, WHITE, self.enemy)
        pg.draw.ellipse(self.window, WHITE, self.ball)

        debug(f'Ball[dir {self.ball.direction}, pos {self.ball.rect.center}]', YELLOW)

        pg.display.update()

        self.clock.tick(60)
        pg.display.set_caption(f"{self.clock.get_fps()} FPS")

    def input(self):
        for event in pg.event.get():
            if self.state == GameState.idle:
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        self.run()
            elif self.state == GameState.running:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.idle()

    def run(self):
        self.state = GameState.running
        while self.state == GameState.running:
            self.input()

            # update
            self.player.update()
            self.ball.update()
            self.ball.reflect_if_collide(self.player)
            self.ball.reflect_if_collide(self.enemy)
            self.enemy.update(self.ball)

            self.render()

            if self.ball.rect.x < self.player.rect.x:
                self.idle()

    def idle(self):
        self.initialize()
        self.state = GameState.idle
        while self.state == GameState.idle:
            self.input()
            self.render()


def main():
    pg.init()
    game = Game()
    game.idle()


def debug(text: str, color=(0, 0, 0), x=10, y=10):
    font = pg.font.Font(None, 22)
    debug_text = font.render(text, True, color)
    surface = pg.display.get_surface()
    surface.blit(debug_text, (x, y))


if __name__ == '__main__':
    main()
