from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # Hide pygame support prompt

import pygame, sys, time, random, math
from pygame.locals import *
import kociemba  # Make sure you have installed this library

# Define colors for each face (using letters for cube state)
BLACK   = (  0,   0,   0)
WHITE   = (255, 255, 255)
RED     = (255,   0,   0)
GREEN   = (  0, 255,   0)
BLUE    = (  0,   0, 255)
ORANGE  = (255, 165,   0)
YELLOW  = (255, 255,   0)

# Map face letter to color for drawing
FACE_COLORS = {
    'U': WHITE,   # Up
    'D': YELLOW,  # Down
    'F': GREEN,   # Front
    'B': BLUE,    # Back
    'L': ORANGE,  # Left
    'R': RED      # Right
}

# Cube Module: Represents cube state as 6 faces (each 3x3)
class RubiksCube:
    def __init__(self):
        # Initialize cube faces
        self.faces = {face: [[face]*3 for _ in range(3)] for face in "UDFBLR"}
        self.scramble_moves = []
        self.move_history = []
        self.current_move = ""
        self.solution_attempt = 0  # NEW: Track number of solution attempts
        self.max_solution_attempts = 3  # NEW: Limit solution attempts

    def rotate_face(self, face_matrix, clockwise=True):
        """Rotate a face clockwise or counterclockwise"""
        if clockwise:
            return [list(row) for row in zip(*face_matrix[::-1])]
        else:
            return [list(row) for row in zip(*face_matrix)][::-1]

    def update_adjacent_faces(self, face: str, clockwise: bool):
        """Update adjacent faces when rotating a face"""
        if face == 'F':
            temp = self.faces['U'][2].copy()
            if clockwise:
                self.faces['U'][2] = [self.faces['L'][2][2], self.faces['L'][1][2], self.faces['L'][0][2]]
                for i in range(3):
                    self.faces['L'][i][2] = self.faces['D'][0][2-i]
                self.faces['D'][0] = [self.faces['R'][0][0], self.faces['R'][1][0], self.faces['R'][2][0]]
                for i in range(3):
                    self.faces['R'][i][0] = temp[i]
            else:
                self.faces['U'][2] = [self.faces['R'][0][0], self.faces['R'][1][0], self.faces['R'][2][0]]
                for i in range(3):
                    self.faces['R'][i][0] = self.faces['D'][0][2-i]
                self.faces['D'][0] = [self.faces['L'][2][2], self.faces['L'][1][2], self.faces['L'][0][2]]
                for i in range(3):
                    self.faces['L'][i][2] = temp[2-i]

        elif face == 'R':
            temp = [self.faces['F'][i][2] for i in range(3)]
            if clockwise:
                for i in range(3):
                    self.faces['F'][i][2] = self.faces['D'][i][2]
                    self.faces['D'][i][2] = self.faces['B'][2-i][0]
                    self.faces['B'][2-i][0] = self.faces['U'][i][2]
                    self.faces['U'][i][2] = temp[i]
            else:
                for i in range(3):
                    self.faces['F'][i][2] = self.faces['U'][i][2]
                    self.faces['U'][i][2] = self.faces['B'][2-i][0]
                    self.faces['B'][2-i][0] = self.faces['D'][i][2]
                    self.faces['D'][i][2] = temp[i]

        elif face == 'U':
            temp = self.faces['F'][0].copy()
            if clockwise:
                self.faces['F'][0] = self.faces['R'][0]
                self.faces['R'][0] = self.faces['B'][0]
                self.faces['B'][0] = self.faces['L'][0]
                self.faces['L'][0] = temp
            else:
                self.faces['F'][0] = self.faces['L'][0]
                self.faces['L'][0] = self.faces['B'][0]
                self.faces['B'][0] = self.faces['R'][0]
                self.faces['R'][0] = temp

        elif face == 'L':
            temp = [self.faces['F'][i][0] for i in range(3)]
            if clockwise:
                for i in range(3):
                    self.faces['F'][i][0] = self.faces['U'][i][0]
                    self.faces['U'][i][0] = self.faces['B'][2-i][2]
                    self.faces['B'][2-i][2] = self.faces['D'][i][0]
                    self.faces['D'][i][0] = temp[i]
            else:
                for i in range(3):
                    self.faces['F'][i][0] = self.faces['D'][i][0]
                    self.faces['D'][i][0] = self.faces['B'][2-i][2]
                    self.faces['B'][2-i][2] = self.faces['U'][i][0]
                    self.faces['U'][i][0] = temp[i]

        elif face == 'D':
            temp = self.faces['F'][2].copy()
            if clockwise:
                self.faces['F'][2] = self.faces['L'][2]
                self.faces['L'][2] = self.faces['B'][2]
                self.faces['B'][2] = self.faces['R'][2]
                self.faces['R'][2] = temp
            else:
                self.faces['F'][2] = self.faces['R'][2]
                self.faces['R'][2] = self.faces['B'][2]
                self.faces['B'][2] = self.faces['L'][2]
                self.faces['L'][2] = temp

        elif face == 'B':
            temp = self.faces['U'][0].copy()
            if clockwise:
                self.faces['U'][0] = [self.faces['R'][0][2], self.faces['R'][1][2], self.faces['R'][2][2]]
                for i in range(3):
                    self.faces['R'][i][2] = self.faces['D'][2][2-i]
                self.faces['D'][2] = [self.faces['L'][2][0], self.faces['L'][1][0], self.faces['L'][0][0]]
                for i in range(3):
                    self.faces['L'][i][0] = temp[2-i]
            else:
                self.faces['U'][0] = [self.faces['L'][0][0], self.faces['L'][1][0], self.faces['L'][2][0]]
                for i in range(3):
                    self.faces['L'][i][0] = self.faces['D'][2][i]
                self.faces['D'][2] = [self.faces['R'][2][2], self.faces['R'][1][2], self.faces['R'][0][2]]
                for i in range(3):
                    self.faces['R'][i][2] = temp[i]

    def apply_move(self, move):
        """Apply a move to the cube state"""
        self.current_move = move
        self.move_history.append(move)
        
        face = move[0]  # Get the face to rotate (F, R, U, etc.)
        clockwise = "'" not in move  # Check if it's a counter-clockwise move
        
        # Rotate the main face
        self.faces[face] = self.rotate_face(self.faces[face], clockwise)
        
        # Update adjacent faces
        self.update_adjacent_faces(face, clockwise)
        print(f"Applied move: {move}")

    def scramble(self, moves=20):
        """Scramble the cube with random moves"""
        # Use all valid moves, not just simplified set
        valid_moves = ['F', 'R', 'U', 'B', 'L', 'D',
                      "F'", "R'", "U'", "B'", "L'", "D'"]
        self.scramble_moves = []
        
        for _ in range(moves):
            move = random.choice(valid_moves)
            self.apply_move(move)
            self.scramble_moves.append(move)
        
        return f"Scrambled with {moves} moves"

    def verify_solved_state(self) -> bool:
        """Verify if cube is in completely solved state"""
        # Check each face has all stickers matching center sticker
        for face in "UDFBLR":
            center = self.faces[face][1][1]  # Center sticker
            for row in self.faces[face]:
                for sticker in row:
                    if sticker != center:
                        return False
        return True

    def is_solved(self):
        for face in self.faces:
            if any(cell != self.faces[face][0][0] for row in self.faces[face] for cell in row):
                return False
        return True
    
    def draw(self, surface):
        # UI Module: Draw a simple flat 2D net of the cube
        sticker_size = 30
        gap = 5
        x_offset = 300
        y_offset = 50
        # Draw Up face
        self.draw_face(surface, self.faces['U'], x_offset, y_offset, sticker_size, gap)
        # Draw Left, Front, Right, Back in a row
        faces_row = ['L','F','R','B']
        for i, face in enumerate(faces_row):
            self.draw_face(surface, self.faces[face], x_offset + i*(3*sticker_size + 3*gap + gap), y_offset + 3*sticker_size + 2*gap, sticker_size, gap)
        # Draw Down face
        self.draw_face(surface, self.faces['D'], x_offset, y_offset + 6*sticker_size + 4*gap, sticker_size, gap)
    
    def draw_face(self, surface, face_matrix, x, y, size, gap):
        for i, row in enumerate(face_matrix):
            for j, val in enumerate(row):
                rect = pygame.Rect(x + j*(size+gap), y + i*(size+gap), size, size)
                pygame.draw.rect(surface, FACE_COLORS.get(val, BLACK), rect)
                pygame.draw.rect(surface, BLACK, rect, 1)

# Solver Module: Implements a stub solver (replace with a real algorithm like Kociemba)
# from kociemba import solve # Example import
# Assuming you have a separate module with a solving algorithm

def kociemba_solve(cube_state):
    """Convert cube state to Kociemba notation, validate it, then solve."""
    def convert_to_kociemba_notation(state):
        kociemba_map = {
            'U': 'U',  # White
            'D': 'D',  # Yellow
            'F': 'F',  # Green
            'B': 'B',  # Blue
            'L': 'L',  # Orange
            'R': 'R'   # Red
        }
        # Deep copy and fix centers
        state_copy = {face: [row[:] for row in face_matrix] for face, face_matrix in state.items()}
        centers = {'U': 'U', 'R': 'R', 'F': 'F', 'D': 'D', 'L': 'L', 'B': 'B'}
        for face in centers:
            state_copy[face][1][1] = centers[face]
        cube_str = ""
        for face in ['U', 'R', 'F', 'D', 'L', 'B']:
            for row in range(3):
                for col in range(3):
                    cube_str += kociemba_map[state_copy[face][row][col]]
        
        print("Generated cube string:", cube_str)
        # Validate: should be 54 characters and each letter appears 9 times.
        if len(cube_str) != 54:
            print("Error: Cube string length invalid.")
            return None
        counts = {letter: cube_str.count(letter) for letter in "URFDLB"}
        print("Letter counts:", counts)
        if any(count != 9 for count in counts.values()):
            print("Error: Cube string invalid. Each face must appear 9 times.")
            return None
        return cube_str

    try:
        notation_string = convert_to_kociemba_notation(cube_state)
        if notation_string is None:
            return []  # Abort solving if invalid string
        print("Calling kociemba.solve with:", notation_string)
        solution_str = kociemba.solve(notation_string)
        print("Kociemba solution:", solution_str)
        return solution_str.split()
    except Exception as e:
        print(f"Kociemba solver error: {e}")
        for face in "URFDLB":
            print(f"Face {face}:", cube_state[face])
        return []

class CubeSolver:
    def __init__(self, cube: RubiksCube):
        self.cube = cube

    def solve(self):
        """Generate solution moves using Kociemba's algorithm"""
        if self.cube.verify_solved_state():
            self.solution_moves = []
            print("Cube is already solved.")
            return []
        else:
            try:
                # Call the Kociemba solver
                solution = kociemba_solve(self.cube.faces)
                if not solution:
                    print("Kociemba solver failed to find a solution.")
                    self.solution_moves = []
                    return []
                
                # Convert solution string to list of moves
                self.solution_moves = solution
                print("Solution:", self.solution_moves)
                return self.solution_moves
            except Exception as e:
                print(f"Solver error: {e}")
                self.solution_moves = []
                return []

def main():
    pygame.init()
    screen = pygame.display.set_mode((800,600))
    pygame.display.set_caption("Rubik's Cube Solver")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    small_font = pygame.font.SysFont(None, 24)  # NEW: For move history
    
    cube = RubiksCube()
    solver = CubeSolver(cube)
    
    # Create button rectangles for mouse control
    solve_button = pygame.Rect(20, 540, 150, 40)
    scramble_button = pygame.Rect(200, 540, 150, 40)
    
    solving = False
    solution_index = 0
    auto_solve = False
    status_message = "Ready"  # NEW: Status message for display
    
    def draw_interface():
        screen.fill(WHITE)
        cube.draw(screen)
        
        # Draw buttons
        pygame.draw.rect(screen, BLACK, solve_button, 2)
        solve_text = font.render("Solve", True, BLACK)
        screen.blit(solve_text, solve_text.get_rect(center=solve_button.center))
        
        pygame.draw.rect(screen, BLACK, scramble_button, 2)
        scramble_text = font.render("Scramble", True, BLACK)
        screen.blit(scramble_text, scramble_text.get_rect(center=scramble_button.center))
        
        # Draw status and current move
        status = font.render(status_message, True, BLACK)
        screen.blit(status, (20, 20))
        
        if cube.current_move:
            if solving and auto_solve:
                move_text = font.render(f"Move: {cube.current_move} ({solution_index}/{len(solver.solution_moves)})", True, BLACK)
            else:
                move_text = font.render(f"Move: {cube.current_move}", True, BLACK)
            screen.blit(move_text, (20, 60))
        
        # Draw move history with count
        history_y = 100
        history_text = small_font.render(f"Move History: (Total: {len(cube.move_history)})", True, BLACK)
        screen.blit(history_text, (20, history_y))
        
        # Show last 10 moves with numbers
        start_index = max(0, len(cube.move_history) - 10)
        for i, move in enumerate(cube.move_history[-10:]):
            move_num = start_index + i + 1
            move_text = small_font.render(f"#{move_num}: {move}", True, BLACK)
            screen.blit(move_text, (20, history_y + 20 + i*20))
        
        pygame.display.flip()
    
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                if solve_button.collidepoint(event.pos):
                    moves = solver.solve()
                    solving = True
                    solution_index = 0
                    auto_solve = True
                    status_message = "Solving..."
                elif scramble_button.collidepoint(event.pos):
                    status_message = cube.scramble(20)
                    solver = CubeSolver(cube)
                    solving = False
                    auto_solve = False

            elif event.type == KEYDOWN:
                if event.key == K_s:
                    moves = solver.solve()
                    solving = True
                    solution_index = 0
                    auto_solve = True
                    status_message = "Solving..."
                elif event.key == K_r:
                    status_message = cube.scramble(20)
                    solver = CubeSolver(cube)
                    solving = False
                    auto_solve = False

        # If auto-solving, apply moves one at a time
        if solving and auto_solve:
            if solution_index < len(solver.solution_moves):
                move = solver.solution_moves[solution_index]
                cube.apply_move(move)
                solution_index += 1
                # Instead of blocking time.sleep, you can use pygame.time.delay if preferred:
                pygame.time.delay(500)
            else:
                # Verify solution is complete
                if cube.verify_solved_state():
                    status_message = "Solved Successfully!"
                else:
                    status_message = "Solution incomplete - trying again..."
                    moves = solver.solve()  # Try solving again if needed
                    solution_index = 0
                    continue
                solving = False
        
        draw_interface()  # Update display each frame
        clock.tick(10)

if __name__ == "__main__":
    main()
