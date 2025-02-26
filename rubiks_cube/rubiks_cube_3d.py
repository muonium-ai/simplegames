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

# Define row/column controls - arranged in a 3x3 grid on each side
control_size = 30
control_margin = 5

# Row controls (for x-axis rotations) - on the left side
row_buttons = []
for i in range(3):  # 3 rows
    for direction in [-1, 1]:  # Two directions: counter-clockwise (-1) and clockwise (1)
        row_buttons.append({
            'rect': pygame.Rect(
                button_margin + (direction + 1) * (control_size + control_margin),  # x position
                button_margin + i * (control_size + control_margin),  # y position
                control_size,
                control_size
            ),
            'row': i - 1,  # Convert to -1, 0, 1
            'direction': direction,
            'axis': 1  # y-axis
        })

# Column controls (for y-axis rotations) - on the right side
col_buttons = []
for i in range(3):  # 3 columns
    for direction in [-1, 1]:  # Two directions
        col_buttons.append({
            'rect': pygame.Rect(
                WIDTH - button_margin - 2 * (control_size + control_margin) + 
                (direction + 1) * (control_size + control_margin),  # x position
                button_margin + i * (control_size + control_margin),  # y position
                control_size,
                control_size
            ),
            'col': i - 1,  # Convert to -1, 0, 1
            'direction': direction,
            'axis': 0  # x-axis
        })

# Depth controls (for z-axis rotations) - on the top
depth_buttons = []
for i in range(3):  # 3 depths
    for direction in [-1, 1]:  # Two directions
        depth_buttons.append({
            'rect': pygame.Rect(
                WIDTH // 2 - control_size - control_margin + 
                i * (control_size + control_margin),  # x position
                button_margin + (direction + 1) * (control_size + control_margin),  # y position
                control_size,
                control_size
            ),
            'depth': i - 1,  # Convert to -1, 0, 1
            'direction': direction,
            'axis': 2  # z-axis
        })

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
        
        # Draw each face with fixed color intensities
        for face in self.faces:
            # Use immediate mode but with improved color handling
            glBegin(GL_QUADS)
            
            # Set material properties for better lighting consistency
            glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, 
                        face.color + (1.0,))  # Adding alpha=1.0
            glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.3, 0.3, 0.3, 1.0))
            glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 30.0)
            
            # Set color directly as well for compatibility
            glColor3fv(face.color)
            
            # Draw face with normal for proper lighting
            glNormal3fv(face.normal)
            for vertex in face.vertices:
                glVertex3fv(vertex)
            glEnd()
            
            # Draw black edges with lighting disabled
            glDisable(GL_LIGHTING)
            glColor3fv(colors['black'])
            glBegin(GL_LINE_LOOP)
            for vertex in face.vertices:
                glVertex3fv(vertex)
            glEnd()
            glEnable(GL_LIGHTING)
            
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
        
        # Parse move notation (e.g., "R", "L'", "U2", "M", "E", "S")
        face = move[0]
        direction = -1 if "'" in move else 1
        double = "2" in move
        
        # Convert face to axis and slice
        if face == "R":
            axis, slice_val = 0, 1
        elif face == "L":
            axis, slice_val = 0, -1
        elif face == "M":  # Middle slice between L and R
            axis, slice_val = 0, 0
        elif face == "U":
            axis, slice_val = 1, 1
        elif face == "D":
            axis, slice_val = 1, -1
        elif face == "E":  # Equatorial slice between U and D
            axis, slice_val = 1, 0
        elif face == "F":
            axis, slice_val = 2, 1
        elif face == "B":
            axis, slice_val = 2, -1
        elif face == "S":  # Standing slice between F and B
            axis, slice_val = 2, 0
        else:
            return  # Invalid move
        
        # Set up animation
        self.animating = True
        self.current_angle = 0
        self.target_angle = 180 if double else 90
        self.current_axis = axis
        self.current_slice = slice_val
        self.current_direction = direction
        
        # Record the move in history
        self.move_history.append(move)
    
    def rotate_row(self, row_index, direction):
        """Rotate a horizontal row of the cube
        
        row_index: -1, 0, or 1 for bottom, middle, or top row
        direction: 1 for clockwise, -1 for counter-clockwise
        """
        if self.animating:
            return
        
        # Convert row to a move in cube notation
        if row_index == 1:  # Top row = U
            move = "U" if direction == 1 else "U'"
        elif row_index == -1:  # Bottom row = D
            move = "D" if direction == -1 else "D'"  # D is opposite orientation
        else:  # Middle row - this doesn't have standard notation
            # We'll handle it as a special case
            # Use E notation (equator) - rotates like D
            move = "E" if direction == -1 else "E'"
        
        # Animate the move
        self.animate_move(move)
    
    def rotate_column(self, col_index, direction):
        """Rotate a vertical column of the cube
        
        col_index: -1, 0, or 1 for left, middle, or right column
        direction: 1 for clockwise, -1 for counter-clockwise
        """
        if self.animating:
            return
        
        # Convert column to a move in cube notation
        if col_index == 1:  # Right column = R
            move = "R" if direction == 1 else "R'"
        elif col_index == -1:  # Left column = L
            move = "L" if direction == 1 else "L'"
        else:  # Middle column 
            # Use M notation (middle) - rotates like L
            move = "M" if direction == 1 else "M'"
        
        # Animate the move
        self.animate_move(move)
    
    def rotate_depth(self, depth_index, direction):
        """Rotate a depth layer of the cube
        
        depth_index: -1, 0, or 1 for back, middle, or front layer
        direction: 1 for clockwise, -1 for counter-clockwise
        """
        if self.animating:
            return
        
        # Convert depth to a move in cube notation
        if depth_index == 1:  # Front face = F
            move = "F" if direction == 1 else "F'"
        elif depth_index == -1:  # Back face = B
            move = "B" if direction == 1 else "B'"
        else:  # Middle layer
            # Use S notation (standing) - rotates like F
            move = "S" if direction == 1 else "S'"
        
        # Animate the move
        self.animate_move(move)
        
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
    """Render all buttons for cube controls"""
    # Create a solid overlay for buttons (not transparent)
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    
    # Fill with a very transparent background to see overlay boundaries (for debugging)
    overlay.fill((200, 200, 200, 10))
    
    # Draw main action buttons with more opaque colors
    for button, text in [
        (reset_button, "Reset"), 
        (scramble_button, "Scramble"),
        (solve_button, "Solve")
    ]:
        # Check if mouse is over the button
        mouse_pos = pygame.mouse.get_pos()
        # Use more visible colors (fully opaque)
        color = (150, 150, 220, 255) if button.collidepoint(mouse_pos) else (100, 100, 180, 255)
        
        # Draw button background
        pygame.draw.rect(overlay, color, button)
        # Add a border for better visibility
        pygame.draw.rect(overlay, (50, 50, 50, 255), button, 2)
        
        # Draw button text in black for better contrast
        font = pygame.font.SysFont(None, 24)
        text_surface = font.render(text, True, (0, 0, 0, 255))
        text_rect = text_surface.get_rect(center=button.center)
        overlay.blit(text_surface, text_rect)
    
    # Draw row control buttons with improved visibility
    for btn in row_buttons:
        color = (200, 150, 150, 255) if btn['rect'].collidepoint(pygame.mouse.get_pos()) else (180, 100, 100, 255)
        pygame.draw.rect(overlay, color, btn['rect'])
        pygame.draw.rect(overlay, (50, 50, 50, 255), btn['rect'], 2)  # Add border
        direction_text = "↑" if btn['direction'] == 1 else "↓"
        font = pygame.font.SysFont(None, 20)
        text_surface = font.render(direction_text, True, (0, 0, 0, 255))
        text_rect = text_surface.get_rect(center=btn['rect'].center)
        overlay.blit(text_surface, text_rect)
    
    # Draw column control buttons
    for btn in col_buttons:
        color = (150, 200, 150, 255) if btn['rect'].collidepoint(pygame.mouse.get_pos()) else (100, 180, 100, 255)
        pygame.draw.rect(overlay, color, btn['rect'])
        pygame.draw.rect(overlay, (50, 50, 50, 255), btn['rect'], 2)  # Add border
        direction_text = "→" if btn['direction'] == 1 else "←"
        font = pygame.font.SysFont(None, 20)
        text_surface = font.render(direction_text, True, (0, 0, 0, 255))
        text_rect = text_surface.get_rect(center=btn['rect'].center)
        overlay.blit(text_surface, text_rect)
    
    # Draw depth control buttons
    for btn in depth_buttons:
        color = (150, 150, 200, 255) if btn['rect'].collidepoint(pygame.mouse.get_pos()) else (100, 100, 180, 255)
        pygame.draw.rect(overlay, color, btn['rect'])
        pygame.draw.rect(overlay, (50, 50, 50, 255), btn['rect'], 2)  # Add border
        direction_text = "⟳" if btn['direction'] == 1 else "⟲"
        font = pygame.font.SysFont(None, 20)
        text_surface = font.render(direction_text, True, (0, 0, 0, 255))
        text_rect = text_surface.get_rect(center=btn['rect'].center)
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
    
    # Set up OpenGL clear color (background color)
    glClearColor(0.9, 0.9, 0.9, 1.0)  # Light gray background
    
    # Configure OpenGL for optimal rendering
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)  # Change depth function for more accurate depth testing
    
    # Improve line rendering
    glEnable(GL_LINE_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    glLineWidth(1.5)  # Slightly thicker lines for better visibility
    
    # Better polygon rendering
    glEnable(GL_POLYGON_SMOOTH)
    glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)
    
    # More stable lighting setup
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    # Better light positioning (from the front top right)
    light_position = [5.0, 5.0, 5.0, 0.0]  # Directional light
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    
    # Improved ambient and diffuse settings for more consistent colors
    ambient_light = [0.4, 0.4, 0.4, 1.0]  # More ambient for less contrast
    diffuse_light = [0.7, 0.7, 0.7, 1.0]  # Less intense diffuse
    specular_light = [0.2, 0.2, 0.2, 1.0]  # Low specular to reduce glare
    
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambient_light)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse_light)
    glLightfv(GL_LIGHT0, GL_SPECULAR, specular_light)
    
    # Enable normalization of normals for proper lighting
    glEnable(GL_NORMALIZE)
    
    # Disable color tracking to ensure stable colors
    glDisable(GL_COLOR_MATERIAL)
    
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
                
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Check for main button clicks
                    if reset_button.collidepoint(event.pos):
                        cube.reset()
                    elif scramble_button.collidepoint(event.pos):
                        cube.scramble(20)  # Scramble with 20 moves
                    elif solve_button.collidepoint(event.pos):
                        cube.solve()
                    
                    # Check for row controls
                    for btn in row_buttons:
                        if btn['rect'].collidepoint(event.pos):
                            cube.rotate_row(btn['row'], btn['direction'])
                    
                    # Check for column controls
                    for btn in col_buttons:
                        if btn['rect'].collidepoint(event.pos):
                            cube.rotate_column(btn['col'], btn['direction'])
                    
                    # Check for depth controls
                    for btn in depth_buttons:
                        if btn['rect'].collidepoint(event.pos):
                            cube.rotate_depth(btn['depth'], btn['direction'])
                    
                    # If no button was clicked, start cube rotation
                    if not any(b.collidepoint(event.pos) for b in [reset_button, scramble_button, solve_button]) and \
                       not any(b['rect'].collidepoint(event.pos) for b in row_buttons + col_buttons + depth_buttons):
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
        
        # Clear both the color and depth buffer completely
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Draw the cube with stable OpenGL state
        glEnable(GL_LIGHTING)
        glEnable(GL_DEPTH_TEST)
        cube.draw()
        
        # Completely disable all OpenGL features for UI rendering
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glDisable(GL_COLOR_MATERIAL)
        glDisable(GL_CULL_FACE)
        
        # Use a more reliable approach for 2D rendering
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, WIDTH, HEIGHT, 0, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Clear any potential OpenGL errors
        while glGetError() != GL_NO_ERROR:
            pass
        
        # Ensure the rendering pipeline is clear
        glFinish()
        
        # Separate rendering pass for UI
        # Using a separate Surface ensures clean 2D drawing
        ui_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        ui_surface.fill((0, 0, 0, 0))  # Transparent background
        
        # Draw buttons on the UI surface
        # Main action buttons
        for button, text in [
            (reset_button, "Reset"), 
            (scramble_button, "Scramble"),
            (solve_button, "Solve")
        ]:
            # Button background
            pygame.draw.rect(ui_surface, (100, 100, 180), button)
            pygame.draw.rect(ui_surface, (0, 0, 0), button, 2)  # Border
            
            # Button text
            font = pygame.font.SysFont(None, 24)
            text_surface = font.render(text, True, (255, 255, 255))
            ui_surface.blit(text_surface, text_surface.get_rect(center=button.center))
        
        # Row control buttons and label
        row_label = pygame.font.SysFont(None, 20).render("Row Controls", True, (0, 0, 0))
        ui_surface.blit(row_label, (10, 10))
        for btn in row_buttons:
            pygame.draw.rect(ui_surface, (180, 100, 100), btn['rect'])
            pygame.draw.rect(ui_surface, (0, 0, 0), btn['rect'], 2)
            direction_text = "↑" if btn['direction'] == 1 else "↓"
            text_surface = pygame.font.SysFont(None, 20).render(direction_text, True, (0, 0, 0))
            ui_surface.blit(text_surface, text_surface.get_rect(center=btn['rect'].center))
            
        # Column control buttons and label   
        col_label = pygame.font.SysFont(None, 20).render("Column Controls", True, (0, 0, 0))
        ui_surface.blit(col_label, (WIDTH - 130, 10))
        for btn in col_buttons:
            pygame.draw.rect(ui_surface, (100, 180, 100), btn['rect'])
            pygame.draw.rect(ui_surface, (0, 0, 0), btn['rect'], 2)
            direction_text = "→" if btn['direction'] == 1 else "←"
            text_surface = pygame.font.SysFont(None, 20).render(direction_text, True, (0, 0, 0))
            ui_surface.blit(text_surface, text_surface.get_rect(center=btn['rect'].center))
            
        # Depth control buttons and label
        depth_label = pygame.font.SysFont(None, 20).render("Depth", True, (0, 0, 0))
        ui_surface.blit(depth_label, (WIDTH // 2 - 20, 10))
        for btn in depth_buttons:
            pygame.draw.rect(ui_surface, (100, 100, 180), btn['rect'])
            pygame.draw.rect(ui_surface, (0, 0, 0), btn['rect'], 2)
            direction_text = "⟳" if btn['direction'] == 1 else "⟲"
            text_surface = pygame.font.SysFont(None, 20).render(direction_text, True, (0, 0, 0))
            ui_surface.blit(text_surface, text_surface.get_rect(center=btn['rect'].center))
        
        # Draw UI surface to screen
        screen.blit(ui_surface, (0, 0))
        
        # Restore OpenGL state
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        
        # Final display update - single flip to avoid tearing
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
