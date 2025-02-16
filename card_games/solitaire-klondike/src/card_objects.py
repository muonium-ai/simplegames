import random
import pygame
from constants import *

class Card(object):
    def __init__(self, textures, suit, val):
        self.textures = textures
        self.card_tex      = textures[0]
        self.card_back_tex = textures[1]
        self.suit_tex      = textures[2]
        self.val_tex       = textures[3]
        self.suit = suit
        self.value = val
        self.revealed = False

        # Positions to draw card elements at
        self.top_xy = (5, 5)
        self.bottom_xy = (5, CARD_DIM[1] - CARD_SMALL_ITEM_SIZE[1] - 5)
        self.top_spacing_x = CARD_DIM[0] - 30

    def draw(self, screen, pos):
        if self.revealed:
            screen.blit(self.card_tex, pos)
            screen.blit(self.val_tex, (pos[0] + self.top_xy[0], pos[1] + self.top_xy[1]))
            screen.blit(self.suit_tex, (pos[0] + self.top_xy[0] + self.top_spacing_x, pos[1] + self.top_xy[1]))
            screen.blit(self.suit_tex, (pos[0] + self.bottom_xy[0], pos[1] + self.bottom_xy[1]))
            screen.blit(self.val_tex, (pos[0] + self.bottom_xy[0] + self.top_spacing_x, pos[1] + self.bottom_xy[1]))
        else:
            screen.blit(self.card_back_tex, pos)

    def __str__(self):
        return "%d %s" % (self.value, self.suit.lower().capitalize())

class Deck(object):
    def __init__(self, pos, deal_holder, br_holders, tr_holders, textures, easy_mode, autowin=False):
        self.position = pos
        self.deal_holder = deal_holder
        self.br_holders = br_holders
        self.tr_holders = tr_holders
        self.easy_mode = easy_mode
        self.autowin = autowin
        self.card_tex = textures["card_tex"]
        self.card_back_tex = textures["card_back_tex"]
        self.empty_texture = textures["empty_tex"]
        self.suit_textures = textures["suit_textures"]
        self.black_value_textures = textures["black_value_textures"]
        self.red_value_textures = textures["red_value_textures"]
        self.texture = textures["deck_tex"]

        self.cards = []

        self.shuffleCards()
        self.dealCards()

    def clicked(self):
        card_count = 3
        if self.easy_mode:
            card_count = 1
        if len(self.cards) > 0:
            for i in range(min(len(self.cards), card_count)):
                self.cards[i].revealed = True
                self.deal_holder.addCard(self.cards[i])
            self.cards = self.cards[min(len(self.cards), card_count):]
        else:
            for i in range(len(self.deal_holder.cards)):
                self.cards.append(self.deal_holder.cards[i])
            self.deal_holder.cards = []

    def shuffleCards(self):
        new_deck = []
        val = 1
        suit_counter = 0
        for i in range(52):
            suit = CARD_SUITS[suit_counter]
            if suit_counter < 2:
                val_tex = self.red_value_textures[val]
            else:
                val_tex = self.black_value_textures[val]
            new_deck.append(Card([self.card_tex, self.card_back_tex, self.suit_textures[suit], val_tex], suit, val))
            suit_counter += 1
            if suit_counter > 3:
                suit_counter = 0
                val += 1
        if self.autowin:
            self.cards = new_deck
            return
        self.cards = []
        while len(new_deck) > 0:
            rand_idx = random.randint(0, len(new_deck)-1)
            self.cards.append(new_deck[rand_idx])
            del new_deck[rand_idx]

    def dealCards(self):
        if self.autowin:
            counter = 0
            for card in self.cards:
                card.revealed = True
                self.tr_holders[counter].addCard(card)
                counter += 1
                if counter > 3:
                    counter = 0
            return

        for i in range(-1, 6):
            for j in range(6, i, -1):
                self.br_holders[j].addCard(self.cards[-1])
                self.cards = self.cards[:-1]
        for card_holder in self.br_holders:
            card_holder.cards[-1].revealed = True

    def inBounds(self, mouse_pos):
        return mouse_pos[0] > self.position[0] and mouse_pos[0] < self.position[0] + CARD_DIM[0] \
               and mouse_pos[1] > self.position[1] and mouse_pos[1] < self.position[1] + CARD_DIM[1] \

    def draw(self, screen):
        if len(self.cards) > 0:
            screen.blit(self.texture, self.position)
        else:
            screen.blit(self.empty_texture, self.position)


class CardHolder(object):
    def __init__(self, pos, empty_tex, easy_mode=False):
        self.position = pos
        self.empty_tex = empty_tex
        self.easy_mode = easy_mode
        self.cards = []
        self.offset = (0,0)

    def addCard(self, card, player_action=False, contact_point=None):
        if not player_action:
            self.cards.append(card)
            return
        if contact_point == None:
            sys.exit("in addCard: If player action; contact_point arg must be not None")
        last_card_top_pos = self.position[1] + self.offset[1]*(len(self.cards)-1)
        if contact_point[1] > last_card_top_pos and contact_point[1] < last_card_top_pos+CARD_DIM[1]:
            if self.checkSuitAndVal(self.cards, card, lastCard=True):
                return self
        return None

    def checkSuitAndVal(self, card1, card2):
        sys.exit("The base class version of this function should not be used.")

    def isValidParentCard(self, idx):
        prev_card = self.cards[idx]
        for i in range(idx+1, len(self.cards)):
            if not self.checkSuitAndVal(prev_card, self.cards[i]):
                return False
            prev_card = self.cards[i]
        return True

    def transferCards(self, targetHolder, idx=0):
        while len(self.cards) > idx:
            targetHolder.addCard(self.cards[idx])
            del self.cards[idx]

    def drawCards(self, screen):
        if len(self.cards) == 0:
            screen.blit(self.empty_tex, self.position)
            return
        for i in range(len(self.cards)):
            self.cards[i].draw(screen, (self.position[0] + self.offset[0]*i, self.position[1] + self.offset[1]*i))

class BottomRowHolder(CardHolder):
    def __init__(self, pos, empty_tex, easy_mode):
        CardHolder.__init__(self, pos, empty_tex, easy_mode)
        self.offset = BOTTOMROWHOLDER_OFFSET

    def grabCard(self, mouse_pos, mouse_holder):
        for i in range(len(self.cards)):
            card_pos = (self.position[0], self.position[1] + self.offset[1]*i)
            if i == len(self.cards)-1:
                height = CARD_DIM[1]
            else:
                height = CARD_HOLDER_VER_OFFSET
            if mouse_pos[1] > card_pos[1] and mouse_pos[1] < card_pos[1]+height and self.cards[i].revealed:
                # check if card is valid parent
                if self.isValidParentCard(i):
                    self.transferCards(mouse_holder, i)
                    mouse_holder.mouse_relative_position = (card_pos[0] - mouse_pos[0], card_pos[1] - mouse_pos[1])
                    mouse_holder.last_holder = self
                return

    def checkSuitAndVal(self, card1, card2, lastCard=False):
        if lastCard:
            if len(card1) == 0:
                return True
            card1 = card1[-1]
        # check color of suit
        if not self.easy_mode:
            if card1.suit in CARD_SUITS[:2] and card2.suit in CARD_SUITS[:2]:
                return False
            if card1.suit in CARD_SUITS[2:4] and card2.suit in CARD_SUITS[2:4]:
                return False
        # check value
        if card1.value != card2.value+1:
            return False
        return True

class TopRightHolder(CardHolder):
    def __init__(self, pos, empty_tex):
        CardHolder.__init__(self, pos, empty_tex)
        self.offset = TOPRIGHTHOLDER_OFFSET

    def grabCard(self, mouse_pos, mouse_holder):
        if len(self.cards) <= 0:
            return
        if mouse_pos[1] > self.position[1] and mouse_pos[1] < self.position[1] + CARD_DIM[1]:
            mouse_holder.addCard(self.cards[-1])
            mouse_holder.mouse_relative_position = (self.position[0] - mouse_pos[0], self.position[1] - mouse_pos[1])
            mouse_holder.last_holder = self
            del self.cards[-1]

    def checkSuitAndVal(self, card1, card2, lastCard=False):
        if lastCard:
            if len(card1) == 0:
                if card2.value == 1:
                    return True
                else:
                    return False
            card1 = card1[-1]
        # check color of suit
        if card1.suit != card2.suit:
            return False
        # check value
        if card1.value != card2.value-1:
            return False
        return True

class TopLeftHolder(CardHolder):
    def __init__(self, pos, empty_tex):
        CardHolder.__init__(self, pos, empty_tex)
        self.offset = TOPLEFTHOLDER_OFFSET

    def grabCard(self, mouse_pos, mouse_holder):
        if len(self.cards) <= 0:
            return
        cards_displayed = min(len(self.cards), 3)
        card_pos = (self.position[0] + self.offset[0]*(cards_displayed-1), self.position[1])
        if mouse_pos[0] > card_pos[0] and mouse_pos[0] < card_pos[0] + CARD_DIM[0]:
            mouse_holder.addCard(self.cards[-1])
            mouse_holder.mouse_relative_position = (card_pos[0] - mouse_pos[0], card_pos[1] - mouse_pos[1])
            mouse_holder.last_holder = self
            del self.cards[-1]

    def drawCards(self, screen, one_held):
        if len(self.cards) == 0:
            screen.blit(self.empty_tex, self.position)
            return
        if one_held:
            start_idx = min(len(self.cards), 2)
        else:
            start_idx = min(len(self.cards), 3)
        count = 0
        for card in self.cards[-start_idx:]:
            card.draw(screen, (self.position[0] + self.offset[0]*count, self.position[1] + self.offset[1]*count))
            count += 1

class MouseHolder(CardHolder):
    def __init__(self):
        CardHolder.__init__(self, (0,0), None)

        self.mouse_relative_position = (0,0)
        self.last_holder = None
        self.offset = MOUSEHOLDER_OFFSET

    def drawCards(self, screen, position=None):
        position = (self.mouse_relative_position[0] + position[0], self.mouse_relative_position[1] + position[1])
        if len(self.cards) == 0:
            if self.empty_tex: # if not mouse holder
                screen.blit(self.empty_tex, position)
            return
        for i in range(len(self.cards)):
            self.cards[i].draw(screen, (position[0] + self.offset[0]*i, position[1] + self.offset[1]*i))

    def addCard(self, card):
        self.cards.append(card)