import pygame
import random
from math import sqrt
from card_objects import Card
from constants import *

class AnimatedCard(Card):
    def __init__(self, card, pos, vel):
        Card.__init__(self, card.textures, card.suit, card.value)
        self.revealed = True
        self.position = pos
        self.velocity = vel
        self.acceleration = 0.5

    def update(self, screen):
        self.velocity = (self.velocity[0], self.velocity[1] + self.acceleration)
        self.position = (self.position[0] + self.velocity[0], self.position[1] + self.velocity[1])
        if self.position[0] < -CARD_DIM[0] or self.position[0] > WIDTH:
            return 1
        if self.position[1] >= HEIGHT - CARD_DIM[1] and self.velocity[1] > 0:
            self.velocity = (self.velocity[0], -sqrt(self.velocity[1])*self.velocity[1]*0.15)
        self.draw(screen, self.position)
        return 0

class WinAnimator(object):
    def __init__(self, holders):
        self.holders = holders
        self.last_update = 0
        self.animated_card_piles = []
        self.update_freq = 10

        self.setup()

    def setup(self):
        for i in range(len(self.holders)):
            holder = self.holders[i]
            self.animated_card_piles.append([])
            for card in holder.cards:
                self.animated_card_piles[i].append(AnimatedCard(card, holder.position, (random.uniform(-5.0, -6.5), random.uniform(4.0, 8.0))))

    def update(self, screen):
        now = pygame.time.get_ticks()
        if now - self.last_update < self.update_freq:
            return
        self.last_update = now

        for ani_card_pile in self.animated_card_piles:
            if len(ani_card_pile) == 0:
                continue
            ext_code = ani_card_pile[-1].update(screen)
            if ext_code == 1:
                del ani_card_pile[-1]
