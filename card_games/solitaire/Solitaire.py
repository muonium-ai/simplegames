# Solitaire Game
# Source of card images: https://code.google.com/archive/p/vector-playing-deck/
import sys
import pygame
import random

# initialise pygame modules
pygame.init()

# rename caption
pygame.display.set_caption("Solitaire")

# load and scale image to new size
def loadImage(path, newSize=None):
    image = pygame.image.load(path)
    if newSize:
        image = pygame.transform.scale(image, newSize)
    return image

# --------------------creating card and pile classes---------------------#
# card class containing image, position, and size data
class Card:
    # set global card attributes
    size = width, height = 95, 140
    imagePath = "PNG-cards"
    suits = ("clubs", "diamonds", "hearts", "spades")

    # set cardback image
    cardbackImage = loadImage(f"{imagePath}/cardback.png", size)

    def __init__(self, number, suit):
        # set main card attributes
        self.number = number
        self.suit = suit
        self.colour = Card.getColour(suit)

        # set image attributes
        self.__faceUp = False
        self.image = loadImage(f"{Card.imagePath}/{number}_of_{suit}.png", Card.size)
        self.imageBuffer = Card.cardbackImage
        self.rect = self.image.get_rect()

    @staticmethod
    def getColour(suit):
        if suit == "clubs" or suit == "spades":
            return "black"
        return "red"

    @property
    def faceUp(self):
        return self.__faceUp

    @faceUp.setter
    def faceUp(self, faceUp):
        self.__faceUp = faceUp
        # if set face up, change buffer image to card image
        if self.__faceUp:
            self.imageBuffer = self.image
        else:
            self.imageBuffer = Card.cardbackImage
  
    def isOppositeColourTo(self, card):
        # return true if different colours
        return self.colour != card.colour

    def isOneMoreThan(self, card):
        # return true if this card is valued 1 more
        return self.number + 1 == card.number

    def draw(self, screen):
        screen.blit(self.imageBuffer, self.rect)

# pile class containing cards
class Pile:
    # pile and card spacing to define gaps between cards
    cardSpacing = 36
    pileSpacing = 140

    # set empty pile image
    emptyPileImage = loadImage(f"{Card.imagePath}/empty_pile_slot.png", Card.size)

    def __init__(self, pile=[], posX=0, posY=0):
        self.posX = posX
        self.posY = posY
        self.pile = pile
        self.emptyPileRect = pygame.Rect(posX, posY, Card.size[0], Card.size[1])

    def update(self):
        # update positions of the cards
        for index, card in enumerate(self.pile):
            card.rect.x = self.posX
            card.rect.y = self.posY + Pile.cardSpacing * index

    def draw(self, screen):
        # if pile exists
        if self.pile:
            # draw cards
            for card in self.pile:
                card.draw(screen)
        else: 
            # draw empty pile image
            screen.blit(Pile.emptyPileImage, self.emptyPileRect)

# Contains the remaining cards after setting up the tableau
class StockPile(Pile):
    def update(self):
        # update positions of the cards when being placed back in to stock pile
        for card in self.pile:
            card.faceUp = False
            card.rect.x = self.posX
            card.rect.y = self.posY

# Contains the card(s) pulled from the stock
class WastePile(Pile):
    # move cards to waste pile when mouse button is pressed
    def handleMouseDown(self, stockPile):
        # get mouse position
        mouseX, mouseY = pygame.mouse.get_pos()
        
        if stockPile.emptyPileRect.collidepoint(mouseX, mouseY): 
            if stockPile.pile:
                # move top card into waste pile
                self.pile.append(stockPile.pile.pop())
                self.pile[-1].faceUp = True
                self.update()

            else:
                # return waste pile to stock pile
                self.pile.reverse()
                stockPile.pile = self.pile.copy()
                self.pile.clear()

                stockPile.update()
                self.update()

    # overwrite update method
    def update(self):
    # update positions of the cards
        for card in self.pile:
            card.faceUp = True
            card.rect.x = self.posX
            card.rect.y = self.posY

# completing 4 of these piles (1 for each suit) will win the game
class FoundationPile(WastePile):
    # overwrite update method
    def update(self):
        # update positions of the cards
        for card in self.pile:
            card.rect.x = self.posX
            card.rect.y = self.posY

# When pile is being dragged by cursor
class MovingPile(Pile):
    # inherit pile class
    def __init__(self):
        Pile.__init__(self)
        # keep track of mouse positions
        self.prevMouseX = 0
        self.prevMouseY = 0
        # keep track of previous pile object
        self.previousPile = None

    def handleMouseDown(self, pile):
        # get current mouse position
        mouseX, mouseY = pygame.mouse.get_pos()

        # check if cursor is inside any of the cards in the pile (starting from last card)
        for index, card in reversed(list(enumerate(pile.pile))):
            # if mouse is inside card
            if card.rect.collidepoint(mouseX, mouseY) and card.faceUp: 
                # partition pile into moving pile
                self.pile = pile.pile[index:]
                pile.pile = pile.pile[:index]
                self.previousPile = pile
                
                # set moving pile position to the card
                self.posX = card.rect.x
                self.posY = card.rect.y

                # track position of mouse
                self.prevMouseX = mouseX
                self.prevMouseY = mouseY

                return

    def handleMouseMotion(self):
        # move card with cursor if held
        mouseX, mouseY = pygame.mouse.get_pos()
        
        # move pile based on previous position of mouse
        self.posX += mouseX - self.prevMouseX
        self.posY += mouseY - self.prevMouseY
        self.update()

        self.prevMouseX = mouseX
        self.prevMouseY = mouseY

    def handleMouseUp(self, piles):
        # assume no valid pile selected
        pileSelected = None
        
        # check if valid pile
        for pile in piles: 
            if pile.pile:
                # check if pile overlaps with card
                if self.pile[0].rect.colliderect(pile.pile[-1].rect):
                    # if moving pile contains only 1 card and pile is foundaiton pile
                    if len(self.pile) == 1 and type(pile) is FoundationPile:
                        # if the same same suit
                        if self.pile[0].suit == pile.pile[-1].suit:
                            # if moving card valued 1 higher than top foundation card
                            if self.pile[0].number == pile.pile[-1].number + 1:
                                pileSelected = pile
                                break
                    # else normal pile
                    else:
                        # check if opposite colours
                        if self.pile[0].isOppositeColourTo(pile.pile[-1]):
                            # check if last card of stationary pile is valued 1 more
                            if self.pile[0].isOneMoreThan(pile.pile[-1]):
                                pileSelected = pile
                                break

            # else if empty pile overlaps
            elif self.pile[0].rect.colliderect(pile.emptyPileRect):
                # if type is foundaiton pile
                if type(pile) is FoundationPile:
                    # if the moving card is an ace
                    if self.pile[0].number == 1:
                        # add card to foundation pile
                        pileSelected = pile
                        break
                # else it's a normal pile
                else:
                    # only a king can be placed in empty pile
                    if self.pile[0].number == 13:
                        pileSelected = pile
                        break

        if pileSelected:
            # Extend the stationary pile with the moving pile
            pile.pile.extend(self.pile)
            pile.update()
            pileSelected = pile

            # if there is a pile in the previous pile
            if self.previousPile.pile and not self.previousPile.pile[-1].faceUp:
                # flip the last card face up
                self.previousPile.pile[-1].faceUp = True
        else:
            # return the moving pile to the previous pile
            self.previousPile.pile.extend(self.pile)
            self.previousPile.update()
        
        # clear held card/pile held
        self.pile.clear()

    # overwrite draw method
    def draw(self, screen):
        # create seperate draw method to avoid drawing empty card slot
        if self.pile:
            Pile.draw(self, screen)

# --------------------------------buttons--------------------------------#
# reset button
class ResetButton:

    size = width, height = 150, 50

    def __init__(self, posX, posY):
        self.image = loadImage(f"{Card.imagePath}/reset.png", ResetButton.size)
        self.rect = self.image.get_rect()
        self.rect.x = posX
        self.rect.y = posY

    # return true if pressed
    def handleMouseDown(self):
        mouseX, mouseY = pygame.mouse.get_pos()
        return self.rect.collidepoint(mouseX, mouseY)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

# ------------------------set screen properties--------------------------#
screenSize = width, height = 1200, 800
darkGreen = 50, 122, 14 # for background

# set screen and clock
screen = pygame.display.set_mode(screenSize)
clock = pygame.time.Clock()

# initialise piles to none
piles = None
foundationPiles = None
movingPile = None
stockPile = None
wastePile = None
resetButton = None

# set reset flag to true to begin with to set up game
reset = True

# ---------------------------main game loop------------------------------#
while True:
    if reset:
        # create deck
        deck = []
        for suit in Card.suits:
            # 1 = ace, 11 = jack, 12 = queen, 13 = king
            for number in range(1, 14):
                deck.append(Card(number, suit))

        # shuffle deck
        random.shuffle(deck)

        # create 7 piles from shuffled deck
        piles = []
        pilePosX = 200
        pilePosY = 50
        numberOfPiles = 7
        numberOfCards = 1
        for pileNumber in range(numberOfPiles):
            # keep track of how many face downs have been placed
            faceDownCounter = 0
            # create new pile object
            newPile = Pile([], pilePosX, pilePosY)

            # iterate through pile of cards
            for cardNumber in range(numberOfCards):
                card = deck.pop()

                # turn card face up if card number is greater or equal to pile number
                if cardNumber >= pileNumber:
                    card.faceUp = True
                
                newPile.pile.append(card)

            # update positions of cards based on position of the pile
            newPile.update()
            piles.append(newPile)

            # move position of next pile in the x direction
            pilePosX += Pile.pileSpacing

            # next pile has 1 more card
            numberOfCards += 1

        # create a moving pile (intially empty)
        movingPile = MovingPile()

        # place remining cards in stock pile
        stockPile = StockPile(deck, posX=50, posY=20)
        stockPile.update()

        # create a pile to place cards pulled from the stock (initially empty)
        wastePile = WastePile([], posX=50, posY=200)

        # create 4 foundation piles that represent the 4 suits that need to be 
        foundationPiles = []
        pilePosX = 100
        pilePosY = 640
        numberOfSuits = 4
        for _ in range(numberOfSuits):
            newPile = FoundationPile([], pilePosX, pilePosY)
            foundationPiles.append(newPile)
            pilePosX += Pile.pileSpacing

        # create reset button
        resetButton = ResetButton(posX=700, posY=690)

        reset = False

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            # handle reset button
            reset = resetButton.handleMouseDown()
            
            # card(s) potentially moving from stock pile to waste pile
            wastePile.handleMouseDown(stockPile)

            # card(s) potentially moving from main pile to moving pile
            for pile in piles: 
                movingPile.handleMouseDown(pile)

            # card(s) potentially moving from waste pile to moving pile
            movingPile.handleMouseDown(wastePile)

            # card(s) potentially moving from foundation pile to moving pile
            for pile in foundationPiles: 
                movingPile.handleMouseDown(pile)

        if event.type == pygame.MOUSEMOTION and movingPile.pile:
            movingPile.handleMouseMotion()

        if event.type == pygame.MOUSEBUTTONUP and movingPile.pile:
            # handle potential pile placements on the main and foundation piles
            movingPile.handleMouseUp(piles + foundationPiles)

    # render
    screen.fill(darkGreen)
    for pile in piles: pile.draw(screen)
    for pile in foundationPiles: pile.draw(screen)
    stockPile.draw(screen)
    wastePile.draw(screen)
    resetButton.draw(screen)
    movingPile.draw(screen)
    pygame.display.flip()

    # maintain 60 fps
    clock.tick(60)

