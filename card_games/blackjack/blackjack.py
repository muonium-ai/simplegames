#!/usr/bin/python3

#Import Library
import pygame
from pygame.locals import *
import random
import copy
import sys

#Load Images
icon = pygame.image.load('resources/icon.png')
cBack = pygame.image.load('resources/cards/cardback.png')
diamondA = pygame.image.load('resources/cards/ad.png')
clubA = pygame.image.load('resources/cards/ac.png')
heartA = pygame.image.load('resources/cards/ah.png')
spadeA = pygame.image.load('resources/cards/as.png')
diamond2 = pygame.image.load('resources/cards/2d.png')
club2 = pygame.image.load('resources/cards/2c.png')
heart2 = pygame.image.load('resources/cards/2h.png')
spade2 = pygame.image.load('resources/cards/2s.png')
diamond3 = pygame.image.load('resources/cards/3d.png')
club3 = pygame.image.load('resources/cards/3c.png')
heart3 = pygame.image.load('resources/cards/3h.png')
spade3 = pygame.image.load('resources/cards/3s.png')
diamond4 = pygame.image.load('resources/cards/4d.png')
club4 = pygame.image.load('resources/cards/4c.png')
heart4 = pygame.image.load('resources/cards/4h.png')
spade4 = pygame.image.load('resources/cards/4s.png')
diamond5 = pygame.image.load('resources/cards/5d.png')
club5 = pygame.image.load('resources/cards/5c.png')
heart5 = pygame.image.load('resources/cards/5h.png')
spade5 = pygame.image.load('resources/cards/5s.png')
diamond6 = pygame.image.load('resources/cards/6d.png')
club6 = pygame.image.load('resources/cards/6c.png')
heart6 = pygame.image.load('resources/cards/6h.png')
spade6 = pygame.image.load('resources/cards/6s.png')
diamond7 = pygame.image.load('resources/cards/7d.png')
club7 = pygame.image.load('resources/cards/7c.png')
heart7 = pygame.image.load('resources/cards/7h.png')
spade7 = pygame.image.load('resources/cards/7s.png')
diamond8 = pygame.image.load('resources/cards/8d.png')
club8 = pygame.image.load('resources/cards/8c.png')
heart8 = pygame.image.load('resources/cards/8h.png')
spade8 = pygame.image.load('resources/cards/8s.png')
diamond9 = pygame.image.load('resources/cards/9d.png')
club9 = pygame.image.load('resources/cards/9c.png')
heart9 = pygame.image.load('resources/cards/9h.png')
spade9 = pygame.image.load('resources/cards/9s.png')
diamond10 = pygame.image.load('resources/cards/10d.png')
club10 = pygame.image.load('resources/cards/10c.png')
heart10 = pygame.image.load('resources/cards/10h.png')
spade10 = pygame.image.load('resources/cards/10s.png')
diamondJ = pygame.image.load('resources/cards/jd.png')
clubJ = pygame.image.load('resources/cards/jc.png')
heartJ = pygame.image.load('resources/cards/jh.png')
spadeJ = pygame.image.load('resources/cards/js.png')
diamondQ = pygame.image.load('resources/cards/qd.png')
clubQ = pygame.image.load('resources/cards/qc.png')
heartQ = pygame.image.load('resources/cards/qh.png')
spadeQ = pygame.image.load('resources/cards/qs.png')
diamondK = pygame.image.load('resources/cards/kd.png')
clubK = pygame.image.load('resources/cards/kc.png')
heartK = pygame.image.load('resources/cards/kh.png')
spadeK = pygame.image.load('resources/cards/ks.png')

#Set Icon
pygame.display.set_icon(icon)

#Global Constants
black = (0,0,0)
white = (255,255,255)
gray = (192,192,192)

cards = [ diamondA, clubA, heartA, spadeA, \
          diamond2, club2, heart2, spade2, \
          diamond3, club3, heart3, spade3, \
          diamond4, club4, heart4, spade4, \
          diamond5, club5, heart5, spade5, \
          diamond6, club6, heart6, spade6, \
          diamond7, club7, heart7, spade7, \
          diamond8, club8, heart8, spade8, \
          diamond9, club9, heart9, spade9, \
          diamond10, club10, heart10, spade10, \
          diamondJ, clubJ, heartJ, spadeJ, \
          diamondQ, clubQ, heartQ, spadeQ, \
          diamondK, clubK, heartK, spadeK ]
cardA = [ diamondA, clubA, heartA, spadeA ]
card2 = [ diamond2, club2, heart2, spade2 ]
card3 = [ diamond3, club3, heart3, spade3 ]
card4 = [ diamond4, club4, heart4, spade4 ]
card5 = [ diamond5, club5, heart5, spade5 ]
card6 = [ diamond6, club6, heart6, spade6 ]
card7 = [ diamond7, club7, heart7, spade7 ]
card8 = [ diamond8, club8, heart8, spade8 ]
card9 = [ diamond9, club9, heart9, spade9 ]
card10 = [ diamond10, club10, heart10, spade10, \
            diamondJ, clubJ, heartJ, spadeJ, \
            diamondQ, clubQ, heartQ, spadeQ, \
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
    #Local Variable
    ccards = copy.copy(cards)
    stand = False
    userCard = []
    dealCard = []
    winNum = 0
    loseNum = 0
   
    #Initialize Game
    pygame.init()
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
                elif userSum <= 21 and dealSum < userSum or dealSum > 21:
                    winNum += 1
                else:
                    loseNum += 1
                gameover = False
                stand = False
                userCard = []
                dealCard = []
                ccards = copy.copy(cards)
                userSum, userA, dealSum, dealA = initGame(ccards, userCard, dealCard)
                restartB = pygame.draw.rect(background, (80, 150, 15), (270, 225, 75, 25))

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
            restartB = pygame.draw.rect(background, gray, (270, 225, 75, 25))
            screen.blit(restartTxt, (287, 228))
            screen.blit(dealCard[1], (120, 10))
            
        pygame.display.update()
            

if __name__ == '__main__':
    main()
