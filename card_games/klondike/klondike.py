from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
import random
import time
from enum import Enum
import os

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1280  # updated from 800
WINDOW_HEIGHT = 800  # updated from 600
CARD_WIDTH = 71
CARD_HEIGHT = 96
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 128, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Add card image loading path
CARDS_PATH = os.path.join(os.path.dirname(__file__), 'cards')

class Suit(Enum):
    HEARTS = "h"    # Changed from ♥ to h
    DIAMONDS = "d"  # Changed from ♦ to d
    CLUBS = "c"     # Changed from ♣ to c
    SPADES = "s"    # Changed from ♠ to s

class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value
        self.face_up = False
        self.rect = pygame.Rect(0, 0, CARD_WIDTH, CARD_HEIGHT)
        self.front_image = None
        self.back_image = None
        self.create_card_back()  # Create default card back first
        self.load_images()
        
    def create_card_back(self):
        """Create a default card back design"""
        self.back_image = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
        # Fill with base blue color
        self.back_image.fill(BLUE)
        
        # Add a decorative pattern
        margin = 5
        inner_rect = pygame.Rect(margin, margin, 
                               CARD_WIDTH - 2*margin, 
                               CARD_HEIGHT - 2*margin)
        pygame.draw.rect(self.back_image, WHITE, inner_rect, 2)
        
        # Add diagonal lines pattern
        for i in range(0, CARD_WIDTH + CARD_HEIGHT, 10):
            start_pos = (max(0, i - CARD_HEIGHT), min(CARD_HEIGHT, i))
            end_pos = (min(CARD_WIDTH, i), max(0, i - CARD_WIDTH))
            pygame.draw.line(self.back_image, (0, 0, 200), start_pos, end_pos, 1)
        
        # Add border
        pygame.draw.rect(self.back_image, BLACK, (0, 0, CARD_WIDTH, CARD_HEIGHT), 2)
    
    def load_images(self):
        # Convert value to filename format
        value_str = {1: 'a', 11: 'j', 12: 'q', 13: 'k'}.get(self.value, str(self.value))
        suit_char = self.suit.value
        front_filename = f"{value_str}{suit_char}.png"
        front_path = os.path.join(CARDS_PATH, front_filename)
        
        try:
            # Load and scale front image
            original_front = pygame.image.load(front_path)
            self.front_image = pygame.transform.scale(original_front, (CARD_WIDTH, CARD_HEIGHT))
            
            # Try to load custom back image, keep default if not found
            try:
                back_path = os.path.join(CARDS_PATH, "back.png")
                original_back = pygame.image.load(back_path)
                self.back_image = pygame.transform.scale(original_back, (CARD_WIDTH, CARD_HEIGHT))
            except pygame.error:
                # Keep the default back design created in create_card_back()
                pass
                
        except pygame.error as e:
            print(f"Error loading card image: {front_filename}")
            self.create_fallback_image()

    def create_fallback_image(self):
        # Update fallback drawing to use symbols for display only
        self.front_image = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
        self.front_image.fill(WHITE)
        font = pygame.font.SysFont('arial', 30)
        # Still use ♥♦♣♠ for visual display in fallback
        suit_symbols = {"h": "♥", "d": "♦", "c": "♣", "s": "♠"}
        color = RED if self.suit in (Suit.HEARTS, Suit.DIAMONDS) else BLACK
        display_value = {1: 'A', 11: 'J', 12: 'Q', 13: 'K'}.get(self.value, str(self.value))
        value_text = font.render(display_value, True, color)
        suit_text = font.render(suit_symbols[self.suit.value], True, color)
        self.front_image.blit(value_text, (5, 5))
        self.front_image.blit(suit_text, (5, 35))
        pygame.draw.rect(self.front_image, BLACK, (0, 0, CARD_WIDTH, CARD_HEIGHT), 2)
        
        # Create basic back image
        self.back_image = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
        self.back_image.fill(BLUE)
        pygame.draw.rect(self.back_image, BLACK, (0, 0, CARD_WIDTH, CARD_HEIGHT), 2)

    @property
    def image(self):
        return self.front_image if self.face_up else self.back_image

    def flip(self):
        self.face_up = not self.face_up

class Pile:
    def __init__(self, x, y, type_name):
        self.cards = []
        self.rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        self.type = type_name
        # Draw empty pile outline
        self.empty_image = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
        self.empty_image.fill(GREEN)
        pygame.draw.rect(self.empty_image, WHITE, (0, 0, CARD_WIDTH, CARD_HEIGHT), 2)

    def add(self, cards):
        if isinstance(cards, list):
            self.cards.extend(cards)
        else:
            self.cards.append(cards)

    def remove(self, count=1):
        if len(self.cards) >= count:
            return [self.cards.pop() for _ in range(count)][::-1]
        return []

    def draw(self, screen, offset_y=30):  # Changed default offset_y to 30
        if not self.cards:
            screen.blit(self.empty_image, self.rect)
        else:
            for i, card in enumerate(self.cards):
                card.rect.x = self.rect.x
                if self.type == "tableau":
                    card.rect.y = self.rect.y + (i * offset_y)
                else:
                    card.rect.y = self.rect.y
                screen.blit(card.image, card.rect)

    def get_clicked_card(self, pos):
        """Return clicked card and cards above it"""
        if not self.rect.collidepoint(pos):
            return None, []
        
        if self.type == "foundation" and self.cards:
            top_card = self.cards[-1]
            if top_card.rect.collidepoint(pos) and top_card.face_up:
                return top_card, [top_card]
        
        if self.type == "tableau":
            offset_y = 30  # Increased vertical gap from 20 to 30
            for i in range(len(self.cards) - 1, -1, -1):
                card_top = self.rect.y + i * offset_y
                card_bottom = card_top + (CARD_HEIGHT if i == len(self.cards) - 1 else offset_y)
                clickable_rect = pygame.Rect(self.rect.x, card_top, CARD_WIDTH, card_bottom - card_top)
                card = self.cards[i]
                if card.face_up and clickable_rect.collidepoint(pos):
                    return card, self.cards[i:]
        return None, []

    def can_accept(self, cards):
        """Check if this pile can accept the given cards"""
        if not cards:
            return False
            
        if self.type == "foundation":
            # Only accept single cards on foundation
            if len(cards) > 1:
                return False
            card = cards[0]
            if not self.cards:
                # Accept only Ace
                return card.value == 1
            top_card = self.cards[-1]
            # Same suit and exactly one value higher
            return (card.suit == top_card.suit and 
                   card.value == top_card.value + 1)
                   
        elif self.type == "tableau":
            first_card = cards[0]
            if not self.cards:
                # Empty tableau accepts only King
                return first_card.value == 13
            top_card = self.cards[-1]
            # Different color (red vs black) and one value lower
            red_suits = {Suit.HEARTS, Suit.DIAMONDS}
            first_is_red = first_card.suit in red_suits
            top_is_red = top_card.suit in red_suits
            
            return (first_is_red != top_is_red and  # Must be different colors
                   first_card.value == top_card.value - 1)  # Must be one less
        
        return False

    def get_top_card(self):
        """Get the top card of the pile without removing it"""
        return self.cards[-1] if self.cards else None

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Klondike Solitaire")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('arial', 24)
        # Generate and save seed before deck creation
        self.seed = random.randint(0, 10**9)
        random.seed(self.seed)
        # Create deck and piles
        self.create_deck()
        
        # Create piles
        self.stock = Pile(50, 50, "stock")
        self.waste = Pile(150, 50, "waste")
        # Reposition foundation piles vertically along the right side
        self.foundations = [Pile(WINDOW_WIDTH - CARD_WIDTH - 20, 50 + i*(CARD_HEIGHT + 20), "foundation") for i in range(4)]
        self.tableaus = [Pile(50 + i*100, 200, "tableau") for i in range(7)]
        
        # Deal initial cards
        self.deal_initial_cards()
        
        # Game state
        self.selected_cards = []
        self.selected_pile = None
        self.start_time = time.time()
        self.moves = 0
        # New attributes for menu and pause state
        self.paused = False
        self.menu_buttons = {
            'pause': pygame.Rect(WINDOW_WIDTH - 330, WINDOW_HEIGHT - 50, 100, 40),
            'restart': pygame.Rect(WINDOW_WIDTH - 220, WINDOW_HEIGHT - 50, 100, 40),
            'new': pygame.Rect(WINDOW_WIDTH - 110, WINDOW_HEIGHT - 50, 100, 40),
        }
    
    def reset_game(self):
        # Set seed so deck and deal are reproducible
        random.seed(self.seed)
        self.create_deck()
        self.stock.cards = []
        self.waste.cards = []
        for pile in self.foundations + self.tableaus:
            pile.cards = []
        self.deal_initial_cards()
        self.selected_cards = []
        self.selected_pile = None
        self.start_time = time.time()
        self.moves = 0

    def create_deck(self):
        self.deck = []
        for suit in Suit:
            for value in range(1, 14):
                self.deck.append(Card(suit, value))
        random.shuffle(self.deck)

    def deal_initial_cards(self):
        # Deal to tableau piles
        for i, tableau in enumerate(self.tableaus):
            for j in range(i + 1):
                card = self.deck.pop()
                if j == i:  # Top card
                    card.face_up = True
                tableau.add(card)
        
        # Remaining cards go to stock
        self.stock.cards = self.deck
        self.deck = []

    def draw_stock(self):
        if not self.stock.cards:
            # Recycle waste pile
            self.stock.cards = self.waste.cards[::-1]
            for card in self.stock.cards:
                card.face_up = False
                # Fix: Change create_image() to load_images()
                card.load_images()
            self.waste.cards = []
        elif self.stock.cards:
            card = self.stock.cards.pop()
            card.face_up = True
            # Fix: Change create_image() to load_images()
            card.load_images()
            self.waste.add(card)

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
            
            self.draw()
            pygame.display.flip()

    def handle_click(self, pos):
        # Check if a menu button was clicked
        for name, rect in self.menu_buttons.items():
            if rect.collidepoint(pos):
                if name == 'pause':
                    self.paused = not self.paused
                elif name == 'restart':
                    self.reset_game()        # Use existing seed
                elif name == 'new':
                    self.seed = random.randint(0, 10**9)  # Save a new seed
                    self.reset_game()
                return  # Do not process further clicks when menu button pressed
        
        # If paused, ignore other clicks.
        if self.paused:
            return
        
        # If we have selected cards, try to place them
        if self.selected_cards:
            placed = False
            
            # Try foundations first (if it's a single card)
            if len(self.selected_cards) == 1:
                for foundation in self.foundations:
                    if foundation.rect.collidepoint(pos):
                        if foundation.can_accept(self.selected_cards):
                            self.move_cards(foundation)
                            placed = True
                            break
            
            # Try tableau piles if not placed in foundation
            if not placed:
                for tableau in self.tableaus:
                    if tableau.rect.collidepoint(pos):
                        if tableau.can_accept(self.selected_cards):
                            self.move_cards(tableau)
                            placed = True
                            break
            
            # Deselect cards if placed or clicked elsewhere
            if placed or not any(pile.rect.collidepoint(pos) for pile in self.tableaus + self.foundations):
                self.selected_cards = []
                self.selected_pile = None
            return

        # If no cards selected, try to select cards
        # Check stock pile
        if self.stock.rect.collidepoint(pos):
            self.draw_stock()
            return

        # Check waste pile
        if self.waste.cards and self.waste.rect.collidepoint(pos):
            if self.waste.cards[-1].rect.collidepoint(pos):
                self.selected_cards = [self.waste.cards[-1]]
                self.selected_pile = self.waste
                return

        # Check foundation piles
        for foundation in self.foundations:
            card, cards = foundation.get_clicked_card(pos)
            if card:
                self.selected_cards = cards
                self.selected_pile = foundation
                return

        # Check tableau piles
        for tableau in self.tableaus:
            card, cards = tableau.get_clicked_card(pos)
            if card:
                self.selected_cards = cards
                self.selected_pile = tableau
                return

    def move_cards(self, destination):
        """Move selected cards to destination pile"""
        if self.selected_pile and self.selected_cards:
            # Remove cards from source pile
            start_idx = len(self.selected_pile.cards) - len(self.selected_cards)
            self.selected_pile.cards = self.selected_pile.cards[:start_idx]
            
            # Add cards to destination
            destination.add(self.selected_cards)
            
            # If we moved from tableau, flip top card
            if (self.selected_pile.type == "tableau" and 
                self.selected_pile.cards and 
                not self.selected_pile.cards[-1].face_up):
                self.selected_pile.cards[-1].face_up = True
            
            self.moves += 1
            self.selected_cards = []
            self.selected_pile = None

    def draw(self):
        self.screen.fill(GREEN)
        
        # Draw all piles
        self.stock.draw(self.screen)
        self.waste.draw(self.screen)
        
        for foundation in self.foundations:
            foundation.draw(self.screen)
        
        for tableau in self.tableaus:
            tableau.draw(self.screen, offset_y=20)
        
        # Highlight selected cards
        if self.selected_cards:
            for card in self.selected_cards:
                pygame.draw.rect(self.screen, (255, 255, 0), card.rect, 2)
        
        # Draw UI elements
        elapsed = int(time.time() - self.start_time)
        time_text = self.font.render(f"Time: {elapsed//60:02d}:{elapsed%60:02d}", True, WHITE)
        moves_text = self.font.render(f"Moves: {self.moves}", True, WHITE)
        
        self.screen.blit(time_text, (10, 10))
        self.screen.blit(moves_text, (WINDOW_WIDTH - 120, 10))
        
        # Draw menu buttons
        for name, rect in self.menu_buttons.items():
            pygame.draw.rect(self.screen, BLUE, rect)
            btn_text = self.font.render(name.capitalize(), True, WHITE)
            self.screen.blit(btn_text, (rect.centerx - btn_text.get_width()//2,
                                        rect.centery - btn_text.get_height()//2))
        # Overlay paused message, if applicable
        if self.paused:
            pause_overlay = self.font.render("Paused", True, RED)
            self.screen.blit(pause_overlay, (WINDOW_WIDTH//2 - pause_overlay.get_width()//2,
                                             WINDOW_HEIGHT//2 - pause_overlay.get_height()//2))

def main():
    game = Game()
    game.run()
    pygame.quit()

if __name__ == "__main__":
    main()
