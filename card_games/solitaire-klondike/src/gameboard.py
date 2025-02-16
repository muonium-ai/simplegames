from card_objects import Card, Deck, BottomRowHolder, TopLeftHolder, TopRightHolder, MouseHolder
from constants import *
from win_animator import WinAnimator

class GameBoard(object):
    def __init__(self, textures, easy_mode, autowin):
        self.empty_holder_tex = textures["empty_tex"]
        self.easy_mode = easy_mode
        self.autowin = autowin
        self.deck_pos = (BOTTOMROW_XY[0], TOPROW_Y)

        self.mouse_pos = (0,0)
        # Holders
        self.br_card_holders = []   # Bottom row
        self.trr_card_holders = []  # Top right row
        self.tl_card_holder = None  # Top left holder
        # Holder ranges
        self.br_holder_hor_ranges = []
        self.tr_holder_hor_ranges = []
        self.mouse_holder = MouseHolder()
        # Initialize holders
        self.initializeHolders()
        # Create deck and deal cards
        self.deck = Deck(self.deck_pos, self.tl_card_holder, self.br_card_holders, self.trr_card_holders, textures, self.easy_mode, autowin)
        self.player_won = autowin
        self.drawn_once = False

        self.winAnimator = None

    def mouseClicked(self):
        if self.player_won:
            return
        # Bottom row
        if self.mouse_pos[1] > BOTTOMROW_XY[1]:
            for i in range(len(self.br_holder_hor_ranges)):
                if self.mouse_pos[0] > self.br_holder_hor_ranges[i][0] and self.mouse_pos[0] < self.br_holder_hor_ranges[i][1]:
                    self.br_card_holders[i].grabCard(self.mouse_pos, self.mouse_holder)
                    break
        # Top right row
        elif self.mouse_pos[0] > BOTTOMROW_XY[0] + 3*(CARD_SPACING + CARD_DIM[0]):
            for i in range(len(self.tr_holder_hor_ranges)):
                if self.mouse_pos[0] > self.tr_holder_hor_ranges[i][0] and self.mouse_pos[0] < self.tr_holder_hor_ranges[i][1]:
                    self.trr_card_holders[i].grabCard(self.mouse_pos, self.mouse_holder)
                    break
        else:
            if self.deck.inBounds(self.mouse_pos):
                self.deck.clicked()
            else:
                tl_holder_width = CARD_DIM[0] + min(2, len(self.tl_card_holder.cards))*TOPLEFTHOLDER_OFFSET[0]
                if self.mouse_pos[0] > self.tl_card_holder.position[0] and self.mouse_pos[0] < self.tl_card_holder.position[0] + tl_holder_width\
                   and self.mouse_pos[1] > TOPROW_Y and self.mouse_pos[1] < TOPROW_Y + CARD_DIM[1]:
                   self.tl_card_holder.grabCard(self.mouse_pos, self.mouse_holder)

    def mouseReleased(self):
        if self.player_won:
            return
        if len(self.mouse_holder.cards) == 0:
            return 0
        # Position to check if card intersects with holder
        bottom_card = self.mouse_holder.cards[0]
        card_contact_point = (self.mouse_pos[0] + self.mouse_holder.mouse_relative_position[0] + int(CARD_DIM[0]/2), \
                              self.mouse_pos[1] + self.mouse_holder.mouse_relative_position[1] + int(CARD_DIM[1]/2))
        new_holder = check_win = False
        # Bottom row
        if self.mouse_pos[1] > BOTTOMROW_XY[1]:
            for i in range(len(self.br_holder_hor_ranges)):
                if card_contact_point[0] > self.br_holder_hor_ranges[i][0] and card_contact_point[0] < self.br_holder_hor_ranges[i][1]:
                    new_holder = self.br_card_holders[i].addCard(bottom_card, player_action=True, contact_point=card_contact_point)
        # Top right row
        elif self.mouse_pos[0] > BOTTOMROW_XY[0] + 3*(CARD_SPACING + CARD_DIM[0]):
            for i in range(len(self.tr_holder_hor_ranges)):
                if card_contact_point[0] > self.tr_holder_hor_ranges[i][0] and card_contact_point[0] < self.tr_holder_hor_ranges[i][1]:
                    new_holder = self.trr_card_holders[i].addCard(bottom_card, player_action=True, contact_point=card_contact_point)
                    check_win = True
        last_holder = self.mouse_holder.last_holder
        if not new_holder: # put cards from mouse holder back to last holder
            self.mouse_holder.transferCards(last_holder)
        else: # put cards from mouse holder to new holder
            self.mouse_holder.transferCards(new_holder)
            if len(last_holder.cards) > 0:
                last_holder.cards[-1].revealed = True
        bottom_card = None

        if check_win:
            self.checkWin()

    def checkWin(self):
        for holder in self.trr_card_holders:
            if len(holder.cards) != 13:
                return
        self.player_won = True

    def initializeHolders(self):
        for i in range(7):
            new_br_pos = (BOTTOMROW_XY[0]+i*(CARD_SPACING + CARD_DIM[0]), BOTTOMROW_XY[1])
            self.br_holder_hor_ranges.append((new_br_pos[0], (new_br_pos[0] + CARD_DIM[0])))
            self.br_card_holders.append(BottomRowHolder(new_br_pos, self.empty_holder_tex, self.easy_mode))
            if i < 4:
                new_tr_pos = (BOTTOMROW_XY[0] + (i + 3)*(CARD_SPACING + CARD_DIM[0]), TOPROW_Y)
                self.tr_holder_hor_ranges.append((new_tr_pos[0], (new_tr_pos[0] + CARD_DIM[0])))
                self.trr_card_holders.append(TopRightHolder(new_tr_pos, self.empty_holder_tex))
        self.tl_card_holder = TopLeftHolder((BOTTOMROW_XY[0] + CARD_SPACING + CARD_DIM[0], TOPROW_Y), self.empty_holder_tex)

    def resetHolders(self):
        for holder in self.br_card_holders + self.trr_card_holders:
            holder.cards = []
        self.tl_card_holder.cards = []
        self.mouse_holder.cards = []

    def restartGame(self):
        self.resetHolders()
        self.deck.shuffleCards()
        self.deck.dealCards()
        self.drawn_once = False
        self.winAnimator = None
        if not self.autowin:
            self.player_won = False

    def drawBoard(self, screen):
        if self.player_won and self.drawn_once:
            if not self.winAnimator:
                self.winAnimator = WinAnimator(self.trr_card_holders)
            self.winAnimator.update(screen)
            return
        self.drawn_once = True
        for holder in self.br_card_holders + self.trr_card_holders:
            holder.drawCards(screen)

        one_held = len(self.mouse_holder.cards) > 0 and self.mouse_holder.last_holder == self.tl_card_holder
        self.tl_card_holder.drawCards(screen, one_held)

        self.deck.draw(screen)

        # Move and draw mouse holder
        if len(self.mouse_holder.cards) > 0:
            self.mouse_holder.drawCards(screen, position=self.mouse_pos)

