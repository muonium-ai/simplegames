#!/usr/bin/python3

#Import Library
import os
import pygame
from pygame.locals import *
import random
import copy
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

#Global Constants
black = (0,0,0)
white = (255,255,255)
gray = (192,192,192)

#Image and card-list placeholders; populated by loadImages() after pygame.init()
icon = None
cBack = None
cards = []
cardA = []
card2 = []
card3 = []
card4 = []
card5 = []
card6 = []
card7 = []
card8 = []
card9 = []
card10 = []

def loadImages():
    '''Loads all card/icon images. Must be called after pygame.init().'''
    global icon, cBack, cards, cardA, card2, card3, card4, card5, card6, card7, card8, card9, card10
    icon = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/icon.png'))
    cBack = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/cardback.png'))
    diamondA = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/ad.png'))
    clubA = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/ac.png'))
    heartA = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/ah.png'))
    spadeA = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/as.png'))
    diamond2 = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/2d.png'))
    club2_ = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/2c.png'))
    heart2 = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/2h.png'))
    spade2 = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/2s.png'))
    diamond3 = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/3d.png'))
    club3_ = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/3c.png'))
    heart3 = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/3h.png'))
    spade3 = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/3s.png'))
    diamond4 = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/4d.png'))
    club4_ = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/4c.png'))
    heart4 = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/4h.png'))
    spade4 = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/4s.png'))
    diamond5 = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/5d.png'))
    club5_ = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/5c.png'))
    heart5 = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/5h.png'))
    spade5 = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/5s.png'))
    diamond6 = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/6d.png'))
    club6_ = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/6c.png'))
    heart6 = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/6h.png'))
    spade6 = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/6s.png'))
    diamond7 = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/7d.png'))
    club7_ = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/7c.png'))
    heart7 = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/7h.png'))
    spade7 = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/7s.png'))
    diamond8 = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/8d.png'))
    club8_ = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/8c.png'))
    heart8 = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/8h.png'))
    spade8 = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/8s.png'))
    diamond9 = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/9d.png'))
    club9_ = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/9c.png'))
    heart9 = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/9h.png'))
    spade9 = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/9s.png'))
    diamond10 = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/10d.png'))
    club10_ = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/10c.png'))
    heart10 = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/10h.png'))
    spade10 = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/10s.png'))
    diamondJ = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/jd.png'))
    clubJ = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/jc.png'))
    heartJ = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/jh.png'))
    spadeJ = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/js.png'))
    diamondQ = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/qd.png'))
    clubQ = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/qc.png'))
    heartQ = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/qh.png'))
    spadeQ = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/qs.png'))
    diamondK = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/kd.png'))
    clubK = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/kc.png'))
    heartK = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/kh.png'))
    spadeK = pygame.image.load(os.path.join(SCRIPT_DIR, 'resources/cards/ks.png'))

    cards[:] = [ diamondA, clubA, heartA, spadeA,
                 diamond2, club2_, heart2, spade2,
                 diamond3, club3_, heart3, spade3,
                 diamond4, club4_, heart4, spade4,
                 diamond5, club5_, heart5, spade5,
                 diamond6, club6_, heart6, spade6,
                 diamond7, club7_, heart7, spade7,
                 diamond8, club8_, heart8, spade8,
                 diamond9, club9_, heart9, spade9,
                 diamond10, club10_, heart10, spade10,
                 diamondJ, clubJ, heartJ, spadeJ,
                 diamondQ, clubQ, heartQ, spadeQ,
                 diamondK, clubK, heartK, spadeK ]
    cardA[:] = [ diamondA, clubA, heartA, spadeA ]
    card2[:] = [ diamond2, club2_, heart2, spade2 ]
    card3[:] = [ diamond3, club3_, heart3, spade3 ]
    card4[:] = [ diamond4, club4_, heart4, spade4 ]
    card5[:] = [ diamond5, club5_, heart5, spade5 ]
    card6[:] = [ diamond6, club6_, heart6, spade6 ]
    card7[:] = [ diamond7, club7_, heart7, spade7 ]
    card8[:] = [ diamond8, club8_, heart8, spade8 ]
    card9[:] = [ diamond9, club9_, heart9, spade9 ]
    card10[:] = [ diamond10, club10_, heart10, spade10,
                  diamondJ, clubJ, heartJ, spadeJ,
                  diamondQ, clubQ, heartQ, spadeQ,
                  diamondK, clubK, heartK, spadeK ]

def getAmt(card):
    ''' Returns the amount the card is worth.
E.g. Ace is default 11. 10/Jack/Queen/King is 10.'''
    if card in cardA:
        return 11
    elif card in card2:
        return 2
    elif card in card3:
        return 3
    elif card in card4:
        return 4
    elif card in card5:
        return 5
    elif card in card6:
        return 6
    elif card in card7:
        return 7
    elif card in card8:
        return 8
    elif card in card9:
        return 9
    elif card in card10:
        return 10
    else:
        print('getAmt broke')
        sys.exit(1)

def genCard(cList, xList):
    '''Generates an card from cList, removes it from cList, and appends it to xList.
Returns if card is Ace and the card itself.'''
    cA = 0
    card = random.choice(cList)
    cList.remove(card)
    xList.append(card)
    if card in cardA:
        cA = 1
    return card, cA

def initGame(cList, uList, dList):
    '''Generates two cards for dealer and user, one at a time for each.
Returns if card is Ace and the total amount of the cards per person.'''
    userA = 0
    dealA = 0
    card1, cA = genCard(cList, uList)
    userA += cA
    card2, cA = genCard(cList, dList)
    dealA += cA
    card3, cA = genCard(cList, uList)
    userA += cA
    card4, cA = genCard(cList, dList)
    dealA += cA
    return getAmt(card1) + getAmt(card3), userA, getAmt(card2) + getAmt(card4), dealA

def main():
    #Initialize Game
    pygame.init()
    loadImages()
    pygame.display.set_icon(icon)

    #Local Variable
    ccards = copy.copy(cards)
    stand = False
    userCard = []
    dealCard = []
    winNum = 0
    loseNum = 0

    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption('Blackjack')
    font = pygame.font.SysFont('arial', 15)
    hitTxt = font.render('Hit', True, black)
    standTxt = font.render('Stand', True, black)
    restartTxt = font.render('Restart', True, black)
    gameoverTxt = font.render('GAME OVER', True, white)
    userSum, userA, dealSum, dealA = initGame(ccards, userCard, dealCard)

    #Fill Background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((80, 150, 15))
    hitB = pygame.draw.rect(background, gray, (10, 445, 75, 25))
    standB = pygame.draw.rect(background, gray, (95, 445, 75, 25))
    ratioB = pygame.draw.rect(background, gray, (555, 420, 75, 50))
    #Define restart button rect once up-front so click-handler can reference it safely
    restartB = pygame.Rect(270, 225, 75, 25)

    #Event Loop
    while True:
        #checks if game is over
        gameover = True if (userSum >= 21 and userA == 0) or len(userCard) == 5 else False
        if len(userCard) == 2 and userSum == 21:
            gameover = True
        elif len(dealCard) == 2 and dealSum == 21:
            gameover = True

        #background needs to be redisplayed because it gets updated
        winTxt = font.render('Wins: %i' % winNum, True, black)
        loseTxt = font.render('Losses: %i' % loseNum, True, black)

        #checks for mouse clicks on buttons
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and not (gameover or stand) and hitB.collidepoint(pygame.mouse.get_pos()):
                #gives player a card if they don't break blackjack rules
                card, cA = genCard(ccards, userCard)
                userA += cA
                userSum += getAmt(card)
                print('User: %i' % userSum)
                while userSum > 21 and userA > 0:
                    userA -= 1
                    userSum -= 10
            elif event.type == pygame.MOUSEBUTTONDOWN and not gameover and standB.collidepoint(pygame.mouse.get_pos()):
                #when player stands, the dealer plays
                stand = True
                while dealSum <= userSum and dealSum < 17:
                    card, cA = genCard(ccards, dealCard)
                    dealA += cA
                    dealSum += getAmt(card)
                    print('Dealer: %i' % dealSum)
                    while dealSum > 21 and dealA > 0:
                        dealA -= 1
                        dealSum -= 10
            elif event.type == pygame.MOUSEBUTTONDOWN and (gameover or stand) and restartB.collidepoint(pygame.mouse.get_pos()):
                #restarts the game, updating scores
                if userSum == dealSum:
                    pass
                elif userSum <= 21 and len(userCard) == 5:
                    winNum += 1
                elif userSum <= 21 and (dealSum < userSum or dealSum > 21):
                    winNum += 1
                else:
                    loseNum += 1
                gameover = False
                stand = False
                userCard = []
                dealCard = []
                ccards = copy.copy(cards)
                userSum, userA, dealSum, dealA = initGame(ccards, userCard, dealCard)
                #erase restart button from background (rect already defined above)
                pygame.draw.rect(background, (80, 150, 15), (270, 225, 75, 25))

        screen.blit(background, (0, 0))
        screen.blit(hitTxt, (39, 448))
        screen.blit(standTxt, (116, 448))
        screen.blit(winTxt, (565, 423))
        screen.blit(loseTxt, (565, 448))

        #displays dealer's cards
        for card in dealCard:
            x = 10 + dealCard.index(card) * 110
            screen.blit(card, (x, 10))
        screen.blit(cBack, (120, 10))

        #displays player's cards
        for card in userCard:
            x = 10 + userCard.index(card) * 110
            screen.blit(card, (x, 295))

        #when game is over, draws restart button and text, and shows the dealer's second card
        if gameover or stand:
            screen.blit(gameoverTxt, (270, 200))
            pygame.draw.rect(background, gray, (270, 225, 75, 25))
            screen.blit(restartTxt, (287, 228))
            screen.blit(dealCard[1], (120, 10))
            
        pygame.display.update()
            

if __name__ == '__main__':
    main()
