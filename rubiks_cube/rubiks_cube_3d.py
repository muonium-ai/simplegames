import pygame
import sys
import random
import numpy as np
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

# Initialize pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)
pygame.display.set_caption("3D Rubik's Cube")

# Colors for cube faces
colors = {
    'white': (1.0, 1.0, 1.0),
    'yellow': (1.0, 1.0, 0.0),
    'green': (0.0, 1.0, 0.0),
    'blue': (0.0, 0.0, 1.0),
    'orange': (1.0, 0.5, 0.0),
    'red': (1.0, 0.0, 0.0),
    'black': (0.0, 0.0, 0.0)
}

# Button definitions
button_width, button_height = 100, 40
button_margin = 10
button_color = (100, 100, 100)
button_hover_color = (150, 150, 150)
text_color = (255, 255, 255)

# Define buttons (x, y, width, height, text)
reset_button = pygame.Rect(
    button_margin,
    HEIGHT - button_height - button_margin,
    button_width,
    button_height
)

scramble_button = pygame.Rect(
    button_margin * 2 + button_width,
    HEIGHT - button_height - button_margin,
    button_width,
    button_height
)

solve_button = pygame.Rect(
    button_margin * 3 + button_width * 2,
    HEIGHT - button_height - button_margin,
    button_width,
    button_height
)

# Setup OpenGL
glEnable(GL_DEPTH_TEST)
glMatrixMode(GL_PROJECTION)
gluPerspective(45, (WIDTH / HEIGHT), 0.1, 50.0)
glMatrixMode(GL_MODELVIEW)
glTranslatef(0.0, 0.0, -15)

class CubeletFace:
    """Represents a single face of a cubelet"""
    def __init__(self, color, normal, vertices):
        self.color = color
        self.normal = normal  # Direction the face is pointing
        self.vertices = vertices  # 3D coordinates of the face vertices

class Cubelet:
    """Represents a single small cube in the Rubik's Cube"""
    def __init__(self, position, colors):
        """
        position: (x, y, z) where each coordinate is -1, 0, or 1
        colors: dictionary mapping face directions to colors
        """
        self.position = np.array(position, dtype=float)
        self.original_position = np.array(position, dtype=float)
        self.colors = colors
        self.size = 0.95  # Size of each cubelet (smaller than 1 to see gaps)
        self.faces = self._create_faces()
        self.rotation_matrix = np.identity(3)  # For tracking rotations
        
    def _create_faces(self):
        """Create the 6 faces of the cubelet with appropriate colors"""
        s = self.size / 2  # Half size for vertex calculations
        x, y, z = self.position
        
        # Define the faces with normals and vertices
        faces = []
        
        # Only create faces that might be visible (on the outside of the cube)
        # Right face (positive x)
        if x == 1:
            faces.append(CubeletFace(
                self.colors.get('right', colors['black']),
                (1, 0, 0),
                [(x+s, y+s, z+s), (x+s, y+s, z-s), (x+s, y-s, z-s), (x+s, y-s, z+s)]
            ))
        
        # Left face (negative x)
        if x == -1:
            faces.append(CubeletFace(
                self.colors.get('left', colors['black']),
                (-1, 0, 0),
                [(x-s, y+s, z+s), (x-s, y-s, z+s), (x-s, y-s, z-s), (x-s, y+s, z-s)]
            ))
        
        # Top face (positive y)
        if y == 1:
            faces.append(CubeletFace(
                self.colors.get('top', colors['black']),
                (0, 1, 0),
                [(x+s, y+s, z+s), (x-s, y+s, z+s), (x-s, y+s, z-s), (x+s, y+s, z-s)]
            ))
        
        # Bottom face (negative y)
        if y == -1:
            faces.append(CubeletFace(
                self.colors.get('bottom', colors['black']),
                (0, -1, 0),
                [(x+s, y-s, z+s), (x+s, y-s, z-s), (x-s, y-s, z-s), (x-s, y-s, z+s)]
            ))
        
        # Front face (positive z)
        if z == 1:
            faces.append(CubeletFace(
                self.colors.get('front', colors['black']),
                (0, 0, 1),
                [(x+s, y+s, z+s), (x+s, y-s, z+s), (x-s, y-s, z+s), (x-s, y+s, z+s)]
            ))
        
        # Back face (negative z)
        if z == -1:
            faces.append(CubeletFace(
                self.colors.get('back', colors['black']),
                (0, 0, -1),
                [(x+s, y+s, z-s), (x-s, y+s, z-s), (x-s, y-s, z-s), (x+s, y-s, z-s)]
            ))
            
        # Add black faces for inner sides to make it look better
        if x != 1:
            faces.append(CubeletFace(
                colors['black'],
                (1, 0, 0),
                [(x+s, y+s, z+s), (x+s, y+s, z-s), (x+s, y-s, z-s), (x+s, y-s, z+s)]
            ))
        
        if x != -1:
            faces.append(CubeletFace(
                colors['black'],
                (-1, 0, 0),
                [(x-s, y+s, z+s), (x-s, y-s, z+s), (x-s, y-s, z-s), (x-s, y+s, z-s)]
            ))
        
        if y != 1:
            faces.append(CubeletFace(
                colors['black'],
                (0, 1, 0),
                [(x+s, y+s, z+s), (x-s, y+s, z+s), (x-s, y+s, z-s), (x+s, y+s, z-s)]
            ))
        
        if y != -1:
            faces.append(CubeletFace(
                colors['black'],
                (0, -1, 0),
                [(x+s, y-s, z+s), (x+s, y-s, z-s), (x-s, y-s, z-s), (x-s, y-s, z+s)]
            ))
        
        if z != 1:
            faces.append(CubeletFace(
                colors['black'],
                (0, 0, 1),
                [(x+s, y+s, z+s), (x+s, y-s, z+s), (x-s, y-s, z+s), (x-s, y+s, z+s)]
            ))
        
        if z != -1:
            faces.append(CubeletFace(
                colors['black'],
                (0, 0, -1),
                [(x+s, y+s, z-s), (x-s, y+s, z-s), (x-s, y-s, z-s), (x+s, y-s, z-s)]
            ))
        
        return faces
        
    def draw(self):
        """Draw the cubelet at its current position and orientation"""
        glPushMatrix()
        
        # Apply the current rotation matrix
        # This is for the whole cube rotation, not slice rotations
        # The actual position is handled by the face vertices
        
        # Draw each face
        for face in self.faces:
            glBegin(GL_QUADS)
            glColor3fv(face.color)
            for vertex in face.vertices:
                glVertex3fv(vertex)
            glEnd()
            
            # Draw black edges
            glColor3fv(colors['black'])
            glBegin(GL_LINE_LOOP)
            for vertex in face.vertices:
                glVertex3fv(vertex)
            glEnd()
            
        glPopMatrix()
        
    def update_position(self, new_position):
        """Update the cubelet's position and recalculate face vertices"""
        self.position = np.array(new_position, dtype=float)
        self.faces = self._create_faces()
    
    def rotate(self, axis_index, angle_degrees):
        """Rotate the cubelet around the specified axis"""
        # Convert degrees to radians
        angle_rad = np.radians(angle_degrees)
        
        # Create rotation matrix for the given axis
        c, s = np.cos(angle_rad), np.sin(angle_rad)
        if axis_index == 0:  # x-axis
            rotation = np.array([
                [1, 0, 0],
                [0, c, -s],
                [0, s, c]
            ])
        elif axis_index == 1:  # y-axis
            rotation = np.array([
                [c, 0, s],
                [0, 1, 0],
                [-s, 0, c]
            ])
        else:  # z-axis
            rotation = np.array([
                [c, -s, 0],
                [s, c, 0],
                [0, 0, 1]
            ])
            
        # Apply rotation to the position
        self.position = np.dot(rotation, self.position)
        
        # Round to avoid floating point errors
        self.position = np.round(self.position, 6)
        
        # Set exact values for positions that should be integers
        self.position = np.round(self.position)
        
        # Update face vertices
        self.faces = self._create_faces()

class RubiksCube:
    """Represents a 3x3x3 Rubik's Cube"""
    def __init__(self):
        self.size = 3
        self.cubelets = []
        self.create_cube()
        self.rotation_x = 0
        self.rotation_y = 0
        
        # Animation properties
        self.animating = False
        self.animation_moves = []
        self.current_angle = 0
        self.target_angle = 90  # 90 degrees for a quarter turn
        self.animation_speed = 5  # degrees per frame
        self.current_axis = None
        self.current_slice = None
        self.current_direction = None
        
        # Solution and scramble properties
        self.move_history = []
        self.solving = False
        self.solution_moves = []
        
    def create_cube(self):
        """Create all cubelets for a solved cube"""
        self.cubelets = []
        
        # Define colors for each face
        face_colors = {
            'right': colors['red'],
            'left': colors['orange'],
            'top': colors['white'],
            'bottom': colors['yellow'],
            'front': colors['green'],
            'back': colors['blue']
        }
        
        # Create each cubelet with appropriate colors
        for x in range(-1, 2):
            for y in range(-1, 2):
                for z in range(-1, 2):
                    # Skip the center cubelet
                    if x == 0 and y == 0 and z == 0:
                        continue
                        
                    cubelet_colors = {}
                    
                    # Assign colors based on position
                    if x == 1:
                        cubelet_colors['right'] = face_colors['right']
                    if x == -1:
                        cubelet_colors['left'] = face_colors['left']
                    if y == 1:
                        cubelet_colors['top'] = face_colors['top']
                    if y == -1:
                        cubelet_colors['bottom'] = face_colors['bottom']
                    if z == 1:
                        cubelet_colors['front'] = face_colors['front']
                    if z == -1:
                        cubelet_colors['back'] = face_colors['back']
                        
                    self.cubelets.append(Cubelet((x, y, z), cubelet_colors))
                    
    def draw(self):
        """Draw the entire cube"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0, 0, -15)
        
        # Apply overall cube rotation
        glRotatef(self.rotation_x, 1, 0, 0)
        glRotatef(self.rotation_y, 0, 1, 0)
        
        # Draw each cubelet
        for cubelet in self.cubelets:
            cubelet.draw()
            
    def rotate_slice(self, axis_index, slice_index, angle):
        """Rotate a slice of the cube
        
        axis_index: 0 for x, 1 for y, 2 for z
        slice_index: -1, 0, or 1 for which slice along the axis
        angle: degrees to rotate
        """
        # Find cubelets in the slice
        slice_cubelets = []
        for cubelet in self.cubelets:
            if abs(cubelet.position[axis_index] - slice_index) < 0.1:
                slice_cubelets.append(cubelet)
        
        # Rotate each cubelet
        for cubelet in slice_cubelets:
            cubelet.rotate(axis_index, angle)
    
    def update_animation(self):
        """Update the animation state if an animation is in progress"""
        if not self.animating:
            return
            
        # Continue animation
        remaining_angle = self.target_angle - self.current_angle
        angle_step = min(self.animation_speed, remaining_angle)
        self.current_angle += angle_step
        
        # Apply the rotation
        self.rotate_slice(self.current_axis, self.current_slice, 
                         angle_step * self.current_direction)
        
        # Check if animation is complete
        if self.current_angle >= self.target_angle:
            self.animating = False
            
            # Snap positions to grid
            for cubelet in self.cubelets:
                cubelet.position = np.round(cubelet.position)
                cubelet.faces = cubelet._create_faces()
            
            # Process next move if solving
            if self.solving and self.solution_moves:
                self.animate_move(self.solution_moves.pop(0))
                
    def animate_move(self, move):
        """Start animation for a cube move"""
        if self.animating:
            # Queue the move if already animating
            self.animation_moves.append(move)
            return
            
        # Parse move notation (e.g., "R", "L'", "U2")
        face = move[0]
        direction = -1 if "'" in move else 1
        double = "2" in move
        
        # Convert face to axis and slice
        if face == "R":
            axis, slice_val = 0, 1
        elif face == "L":
            axis, slice_val = 0, -1
        elif face == "U":
            axis, slice_val = 1, 1
        elif face == "D":
            axis, slice_val = 1, -1
        elif face == "F":
            axis, slice_val = 2, 1
        elif face == "B":
            axis, slice_val = 2, -1
        else:
            return  # Invalid move
            
        # Set up animation
        self.animating = True
        self.current_angle = 0
        self.target_angle = 180 if double else 90
        self.current_axis = axis
        self.current_slice = slice_val
        self.current_direction = direction
        
        # Record the move
        self.move_history.append(move)
        
    def scramble(self, num_moves=20):
        """Scramble the cube with random moves"""
        if self.animating or self.solving:
            return
            
        # Available moves
        moves = ["R", "R'", "L", "L'", "U", "U'", "D", "D'", "F", "F'", "B", "B'"]
        
        # Generate random moves
        scramble_moves = []
        last_face = None
        
        for _ in range(num_moves):
            # Avoid moves on the same face consecutively
            valid_moves = [m for m in moves if m[0] != last_face]
            move = random.choice(valid_moves)
            scramble_moves.append(move)
            last_face = move[0]
            
        # Clear move history and start animation
        self.move_history = []
        self.solution_moves = scramble_moves.copy()
        self.animate_move(self.solution_moves.pop(0))
        
    def solve(self):
        """Start solving the cube by reversing the move history"""
        if self.animating or not self.move_history:
            return
            
        # Create solution by reversing the moves
        self.solution_moves = []
        
        for move in reversed(self.move_history):
            # Invert the move
            if "'" in move:
                self.solution_moves.append(move[0])
            else:
                self.solution_moves.append(f"{move[0]}'")
                
        # Start solving
        self.solving = True
        self.animate_move(self.solution_moves.pop(0))
        
    def reset(self):
        """Reset the cube to its initial solved state"""
        if self.animating:
            return
            
        # Create a new solved cube
        self.cubelets = []
        self.create_cube()
        self.move_history = []
        self.solving = False
        self.solution_moves = []
        self.animating = False

def render_buttons():
    """Render buttons for cube controls"""
    # Create a transparent overlay for buttons
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    
    # Draw buttons
    for button, text in [(reset_button, "Reset"), 
                         (scramble_button, "Scramble"),
                         (solve_button, "Solve")]:
        # Check if mouse is over the button
        mouse_pos = pygame.mouse.get_pos()
        color = button_hover_color if button.collidepoint(mouse_pos) else button_color
        
        # Draw button background
        pygame.draw.rect(overlay, color, button)
        
        # Draw button text
        font = pygame.font.SysFont(None, 24)
        text_surface = font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=button.center)
        overlay.blit(text_surface, text_rect)
    
    # Blit overlay onto screen
    screen.blit(overlay, (0, 0))

def main():
    """Main game loop"""
    cube = RubiksCube()
    
    # Mouse drag tracking
    dragging = False
    last_mouse_pos = None
    
    clock = pygame.time.Clock()
    
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
                
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Check for button clicks
                    if reset_button.collidepoint(event.pos):
                        cube.reset()
                    elif scramble_button.collidepoint(event.pos):
                        cube.scramble()
                    elif solve_button.collidepoint(event.pos):
                        cube.solve()
                    else:
                        # Start dragging for cube rotation
                        dragging = True
                        last_mouse_pos = event.pos
                        
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False
                    
            elif event.type == MOUSEMOTION and dragging:
                # Rotate cube based on mouse movement
                dx, dy = event.pos[0] - last_mouse_pos[0], event.pos[1] - last_mouse_pos[1]
                cube.rotation_y += dx * 0.5
                cube.rotation_x += dy * 0.5
                last_mouse_pos = event.pos
                
            elif event.type == KEYDOWN:
                # Keyboard controls for cube moves
                if not cube.animating:
                    key_to_move = {
                        K_r: "R", K_l: "L", K_u: "U", K_d: "D", K_f: "F", K_b: "B"
                    }
                    
                    if event.key in key_to_move:
                        move = key_to_move[event.key]
                        if pygame.key.get_mods() & KMOD_SHIFT:
                            move += "'"
                        cube.animate_move(move)
        
        # Update animation state
        cube.update_animation()
        
        # Draw everything
        cube.draw()
        
        # Swap from OpenGL to Pygame context to draw buttons
        pygame.display.flip()
        glClear(GL_DEPTH_BUFFER_BIT)
        
        # Draw buttons
        render_buttons()
        
        # Display final frame and maintain frame rate
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
