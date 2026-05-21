from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame, random, math, sys
import numpy as np

# Simulation and physics constants
WIDTH, HEIGHT = 800, 600
FPS = 60
SIMULATION_TIME = 15 * FPS  # 15 seconds per generation
POPULATION_SIZE = 20
SPEED = 5  # horizontal speed component
GRAVITY = 0.3
JUMP_STRENGTH = -7  # impulse when jumping
MUTATION_RATE = 0.1  # per-element mutation probability for NN weights

# Track constants
TRACK_LENGTH = 2000
SEGMENT_LENGTH = 200  # change gradient every 200 pixels
TRACK_TOLERANCE = 100  # max vertical deviation allowed

# Camera offset will follow leading car
CAMERA_OFFSET_X = 100

# Predefined car variant names and colors
VARIANT_NAMES = ["Red Racer", "Blue Blitzer", "Green Machine", "Yellow Speedster", "Purple Phantom", "Orange Comet"]
VARIANT_COLORS = [(255,0,0), (0,0,255), (0,255,0), (255,255,0), (128,0,128), (255,165,0)]

# Generate track points with varying gradients
base_y = HEIGHT // 2
track_points = []
for x in range(0, TRACK_LENGTH + 1, SEGMENT_LENGTH):
    offset = random.randint(-50, 50)
    track_points.append((x, base_y + offset))

def get_track_y(x):
    if x <= 0:
        return track_points[0][1]
    if x >= TRACK_LENGTH:
        return track_points[-1][1]
    i = int(x // SEGMENT_LENGTH)
    x1, y1 = track_points[i]
    x2, y2 = track_points[i + 1]
    t = (x - x1) / (x2 - x1)
    return y1 + t * (y2 - y1)

def build_sky_gradient():
    """Build a vertical sky gradient surface once at startup."""
    surf = pygame.Surface((WIDTH, HEIGHT))
    top = (135, 206, 235)
    mid = (70, 130, 170)
    bot = (45, 90, 120)
    for y in range(HEIGHT):
        if y <= base_y:
            t = y / max(1, base_y)
            r = int(top[0] + (mid[0] - top[0]) * t)
            g = int(top[1] + (mid[1] - top[1]) * t)
            b = int(top[2] + (mid[2] - top[2]) * t)
        else:
            t = (y - base_y) / max(1, HEIGHT - base_y)
            r = int(mid[0] + (bot[0] - mid[0]) * t)
            g = int(mid[1] + (bot[1] - mid[1]) * t)
            b = int(mid[2] + (bot[2] - mid[2]) * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (WIDTH, y))
    return surf

def draw_markers(screen, cam_offset):
    """Draw start (green post) and finish (checkered flag) markers."""
    # Start at x=0
    start_x = int(0 - cam_offset)
    start_y = int(get_track_y(0))
    pygame.draw.rect(screen, (0, 200, 0), (start_x - 2, start_y - 60, 4, 60))
    pygame.draw.rect(screen, (255, 255, 255), (start_x + 2, start_y - 60, 14, 10))
    # Finish at x=TRACK_LENGTH
    fin_x = int(TRACK_LENGTH - cam_offset)
    fin_y = int(get_track_y(TRACK_LENGTH))
    pygame.draw.rect(screen, (40, 40, 40), (fin_x - 2, fin_y - 60, 4, 60))
    # Checkered flag pattern: 6 rows x 4 cols of 6px squares
    sq = 6
    for row in range(6):
        for col in range(4):
            color = (255, 255, 255) if (row + col) % 2 == 0 else (0, 0, 0)
            rx = fin_x + 2 + col * sq
            ry = fin_y - 60 + row * sq
            pygame.draw.rect(screen, color, (rx, ry, sq, sq))

def build_track_surface():
    """Pre-render the full-length track (brown ground + green surface band)."""
    surf = pygame.Surface((TRACK_LENGTH + 1, HEIGHT), pygame.SRCALPHA)
    surface_pts = [(x, get_track_y(x)) for x in range(0, TRACK_LENGTH + 1, 10)]
    brown_poly = surface_pts + [(TRACK_LENGTH, HEIGHT), (0, HEIGHT)]
    pygame.draw.polygon(surf, (101, 67, 33), brown_poly)
    pygame.draw.lines(surf, (34, 100, 34), False, surface_pts, 6)
    return surf

def draw_track(screen, cam_offset, track_surface=None):
    if track_surface is not None:
        screen.blit(track_surface, (-int(cam_offset), 0))
    else:
        # Fallback dynamic path (preserves original signature behavior)
        surface_pts = [(x - cam_offset, get_track_y(x)) for x in range(0, TRACK_LENGTH + 1, 10)]
        brown_poly = surface_pts + [(surface_pts[-1][0], HEIGHT), (surface_pts[0][0], HEIGHT)]
        pygame.draw.polygon(screen, (101, 67, 33), brown_poly)
        pygame.draw.lines(screen, (34, 100, 34), False, surface_pts, 6)
    # Translucent yellow tolerance band overlay (always dynamic — follows leader visually)
    surface_pts_screen = [(x - cam_offset, get_track_y(x)) for x in range(0, TRACK_LENGTH + 1, 10)]
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    top_line = [(px, py - TRACK_TOLERANCE) for px, py in surface_pts_screen]
    bot_line = [(px, py + TRACK_TOLERANCE) for px, py in surface_pts_screen]
    band_poly = top_line + list(reversed(bot_line))
    pygame.draw.polygon(overlay, (255, 255, 100, 60), band_poly)
    screen.blit(overlay, (0, 0))
    draw_markers(screen, cam_offset)

# Helper: rotate a point (px, py) around origin by an angle (radians)
def rotate_point(px, py, angle):
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    return (px * cos_a - py * sin_a, px * sin_a + py * cos_a)

# Neural-net topology constants
NN_INPUTS = 5
NN_HIDDEN = 6
NN_OUTPUTS = 2


def random_genome():
    """Create a fresh genome of small random weights for the controller NN."""
    return {
        "W1": np.random.randn(NN_HIDDEN, NN_INPUTS) * 0.5,
        "b1": np.random.randn(NN_HIDDEN) * 0.5,
        "W2": np.random.randn(NN_OUTPUTS, NN_HIDDEN) * 0.5,
        "b2": np.random.randn(NN_OUTPUTS) * 0.5,
    }


def crossover(p1, p2):
    """Uniform per-element crossover of two genomes."""
    child = {}
    for key in p1:
        shape = p1[key].shape
        mask = np.random.rand(*shape) < 0.5
        child[key] = p1[key] * mask + p2[key] * (~mask)
    return child


def mutate(genome):
    """Per-element Gaussian mutation with probability MUTATION_RATE."""
    mutated = {}
    for key, arr in genome.items():
        shape = arr.shape
        mask = np.random.rand(*shape) < MUTATION_RATE
        noise = np.random.randn(*shape) * 0.15
        mutated[key] = arr + mask * noise
    return mutated


def clone_genome(genome):
    """Deep copy a genome dict of numpy arrays."""
    return {k: v.copy() for k, v in genome.items()}


# Car class with extra variant properties and physics
class Car:
    def __init__(self, genome=None, name=None, color=None, left_wheel_size=None, right_wheel_size=None):
        self.x = 50
        self.y = get_track_y(50)
        # Deterministic initial rotation: all cars start facing right
        self.angle = 0.0
        self.genome = genome if genome is not None else random_genome()
        self.name = name if name is not None else random.choice(VARIANT_NAMES)
        self.color = color if color is not None else random.choice(VARIANT_COLORS)
        # Use different wheel sizes on both ends by default.
        self.left_wheel_size = left_wheel_size if left_wheel_size is not None else random.randint(8, 12)
        self.right_wheel_size = right_wheel_size if right_wheel_size is not None else random.randint(8, 12)
        self.vy = 0
        self.alive = True
        self.fitness = 0
        self.wheel_rotation = 0  # For rotation visualization
        self.trail = []  # recent (x,y) positions for fading trail

    def read_sensors(self):
        """Return a fixed-length tuple of 5 normalized look-ahead inputs.

        Each value is clamped to [-3.0, 3.0] so the NN sees bounded inputs.
        """
        def _clamp(v):
            if v > 3.0:
                return 3.0
            if v < -3.0:
                return -3.0
            return v
        dy_self = (self.y - get_track_y(self.x)) / TRACK_TOLERANCE
        slope_now = (get_track_y(self.x + 20) - get_track_y(self.x - 20)) / 40.0
        look_50 = (get_track_y(self.x + 50) - self.y) / 100.0
        look_150 = (get_track_y(self.x + 150) - self.y) / 200.0
        look_300 = (get_track_y(self.x + 300) - self.y) / 400.0
        return (_clamp(dy_self), _clamp(slope_now), _clamp(look_50),
                _clamp(look_150), _clamp(look_300))

    def forward(self):
        """Run the controller NN on the current sensors.

        Returns (lean, jump_decision).
        """
        x = np.asarray(self.read_sensors(), dtype=np.float64)
        h = np.tanh(self.genome["W1"] @ x + self.genome["b1"])
        out = self.genome["W2"] @ h + self.genome["b2"]
        return float(out[0]), float(out[1])

    def update(self):
        if not self.alive:
            return
        baseline = get_track_y(self.x)
        lean, jump_decision = self.forward()
        self.angle += float(lean) * 0.05

        ground_threshold = 5
        # Fixed local offsets for wheels relative to car center:
        # Left wheel at rear, right wheel at front.
        left_offset = (-20, 8)
        right_offset = (20, 8)
        r_left = rotate_point(*left_offset, self.angle)
        rx_left, ry_left = self.x + r_left[0], self.y + r_left[1]
        r_right = rotate_point(*right_offset, self.angle)
        rx_right, ry_right = self.x + r_right[0], self.y + r_right[1]
        # Check contact for both wheels.
        left_touch = abs(ry_left - get_track_y(rx_left)) < ground_threshold
        right_touch = abs(ry_right - get_track_y(rx_right)) < ground_threshold

        if left_touch and right_touch:
            dx = SPEED * math.cos(self.angle)
        else:
            dx = 0.2 * SPEED * math.cos(self.angle)
        self.x += dx
        # Continuous wheel rotation proportional to horizontal velocity
        self.wheel_rotation += dx / min(self.left_wheel_size, self.right_wheel_size)

        self.y += SPEED * math.sin(self.angle) + self.vy
        self.vy += GRAVITY

        grounded = abs(self.y - baseline) < ground_threshold and self.vy >= 0
        if grounded:
            self.y = baseline
            self.vy = 0
            if jump_decision > 0.5:
                self.vy = JUMP_STRENGTH

        # Enforce that no part of the car (chassis or wheels) goes below the track.
        max_corr = 0
        # Define chassis corners and wheel centers (using same offsets as in draw)
        parts = [
            (20, 5), (20, -5), (-20, -5), (-20, 5),  # chassis corners
            (-20, 8),  # left wheel center
            (20, 8)    # right wheel center
        ]
        for offset in parts:
            rx, ry = rotate_point(offset[0], offset[1], self.angle)
            part_x, part_y = self.x + rx, self.y + ry
            ground_y = get_track_y(part_x)
            diff = part_y - ground_y
            if diff > max_corr:
                max_corr = diff
        if max_corr > 0:
            self.y -= max_corr
            self.vy = 0

        baseline = get_track_y(self.x)
        deviation = abs(self.y - baseline)
        self.fitness = self.x - 0.2 * deviation

        # Maintain trail of last 20 positions for fading visual
        self.trail.append((self.x, self.y))
        if len(self.trail) > 20:
            self.trail.pop(0)

        # Death conditions:
        # 1) Reached end of track
        if self.x >= TRACK_LENGTH:
            self.x = TRACK_LENGTH
            self.alive = False
        # 2) Fell off the track (deviation beyond tolerance or off-screen vertically)
        elif deviation > TRACK_TOLERANCE or self.y > HEIGHT or self.y < 0:
            self.alive = False

    def draw(self, screen, cam_offset):
        x_draw = int(self.x - cam_offset)
        # Fading trail behind the car
        if self.trail:
            trail_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            n = len(self.trail)
            for idx, (tx, ty) in enumerate(self.trail):
                alpha = int(180 * (idx + 1) / n)
                radius = max(1, int(3 * (idx + 1) / n))
                pygame.draw.circle(trail_surf,
                                   (self.color[0], self.color[1], self.color[2], alpha),
                                   (int(tx - cam_offset), int(ty)), radius)
            screen.blit(trail_surf, (0, 0))
        # Chassis: a thin rectangle (length=40, height=10)
        half_length, half_height = 20, 5
        local_corners = [(half_length, half_height), (half_length, -half_height),
                         (-half_length, -half_height), (-half_length, half_height)]
        chassis_points = []
        for cx, cy in local_corners:
            rx, ry = rotate_point(cx, cy, self.angle)
            chassis_points.append((x_draw + int(rx), int(self.y + ry)))
        col = (150,150,150) if not self.alive else self.color
        pygame.draw.polygon(screen, col, chassis_points)

        # Draw wheels with rotation indicator.
        # Left wheel at rear.
        left_offset = (-20, 8)
        r_left = rotate_point(*left_offset, self.angle)
        wx_left = x_draw + int(r_left[0])
        wy_left = int(self.y + r_left[1])
        pygame.draw.circle(screen, (0, 0, 0), (wx_left, wy_left), self.left_wheel_size)
        line_length_left = int(self.left_wheel_size * 0.8)
        end_x_left = wx_left + int(line_length_left * math.cos(self.wheel_rotation))
        end_y_left = wy_left + int(line_length_left * math.sin(self.wheel_rotation))
        pygame.draw.line(screen, (255, 255, 255), (wx_left, wy_left), (end_x_left, end_y_left), 2)

        # Right wheel at front.
        right_offset = (20, 8)
        r_right = rotate_point(*right_offset, self.angle)
        wx_right = x_draw + int(r_right[0])
        wy_right = int(self.y + r_right[1])
        pygame.draw.circle(screen, (0, 0, 0), (wx_right, wy_right), self.right_wheel_size)
        line_length_right = int(self.right_wheel_size * 0.8)
        end_x_right = wx_right + int(line_length_right * math.cos(self.wheel_rotation))
        end_y_right = wy_right + int(line_length_right * math.sin(self.wheel_rotation))
        pygame.draw.line(screen, (255, 255, 255), (wx_right, wy_right), (end_x_right, end_y_right), 2)

# Genetic algorithm class with variant mutation
class GeneticAlgorithm:
    def __init__(self, population_size):
        self.population = [Car() for _ in range(population_size)]
        self.generation = 1

    def all_dead(self):
        return all(not car.alive for car in self.population)

    def update(self):
        for car in self.population:
            car.update()

    def draw(self, screen, cam_offset):
        for car in self.population:
            car.draw(screen, cam_offset)

    def evolve(self):
        sorted_population = sorted(self.population, key=lambda c: c.fitness, reverse=True)
        best = sorted_population[0]
        new_population = []
        # Elitism: preserve best genome verbatim (no mutation)
        new_population.append(Car(genome=clone_genome(best.genome), name=best.name, color=best.color,
                                  left_wheel_size=best.left_wheel_size, right_wheel_size=best.right_wheel_size))
        # Create children via uniform-mask crossover then per-element mutation
        while len(new_population) < len(self.population):
            parent1 = self.tournament_selection()
            parent2 = self.tournament_selection()
            child_genome = mutate(crossover(parent1.genome, parent2.genome))
            # Inherit and mutate variant properties slightly
            child_color = tuple(min(255, max(0, int((parent1.color[i] + parent2.color[i]) / 2 +
                            random.randint(-10, 10)))) for i in range(3))
            child_left_wheel_size = max(2, int((parent1.left_wheel_size + parent2.left_wheel_size) / 2 +
                                          random.choice([-1,0,1])))
            child_right_wheel_size = max(2, int((parent1.right_wheel_size + parent2.right_wheel_size) / 2 +
                                          random.choice([-1,0,1])))
            child_name = random.choice(VARIANT_NAMES)
            new_population.append(Car(genome=child_genome, name=child_name, color=child_color,
                                      left_wheel_size=child_left_wheel_size, right_wheel_size=child_right_wheel_size))
        self.population = new_population
        self.generation += 1

    def tournament_selection(self, k=3):
        candidates = random.sample(self.population, min(k, len(self.population)))
        return max(candidates, key=lambda c: c.fitness)

def draw_sparkline(screen, history, x, y, w, h, font):
    """Render a small best-fitness sparkline panel at (x, y)."""
    label = font.render("Best fitness", True, (255, 255, 255))
    screen.blit(label, (x, y))
    panel_y = y + label.get_height() + 2
    panel = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(panel, (20, 20, 20, 180), (0, 0, w, h), border_radius=6)
    screen.blit(panel, (x, panel_y))
    if len(history) < 2:
        return
    lo = min(history)
    hi = max(history)
    span = hi - lo if hi > lo else 1.0
    pad = 4
    n = len(history)
    points = []
    for i, v in enumerate(history):
        px = x + pad + int((w - 2 * pad) * (i / max(1, n - 1)))
        py = panel_y + pad + int((h - 2 * pad) * (1.0 - (v - lo) / span))
        points.append((px, py))
    if len(points) >= 2:
        pygame.draw.lines(screen, (0, 220, 220), False, points, 2)


def draw_leaderboard(screen, population, font):
    # Sort by fitness descending and display name and fitness
    sorted_pops = sorted(population, key=lambda c: c.fitness, reverse=True)
    panel_x = WIDTH - 170
    panel_y = 5
    panel_w = 165
    panel_h = 10 + 20 * len(sorted_pops) + 5
    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    pygame.draw.rect(panel, (20, 20, 20, 180), (0, 0, panel_w, panel_h), border_radius=8)
    screen.blit(panel, (panel_x, panel_y))
    y_offset = 10
    for car in sorted_pops:
        pygame.draw.circle(screen, car.color, (panel_x + 12, y_offset + 8), 5)
        text = font.render(f"{car.name}: {int(car.fitness)}", True, (255, 255, 255))
        screen.blit(text, (panel_x + 24, y_offset))
        y_offset += 20

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Genetic Car Simulation")
    clock = pygame.time.Clock()

    sky_surface = build_sky_gradient()
    track_surface = build_track_surface()
    FONT_HUD = pygame.font.SysFont(None, 24)
    FONT_LEADER = pygame.font.SysFont(None, 20)
    FONT_TITLE = pygame.font.SysFont(None, 60)

    ga = GeneticAlgorithm(POPULATION_SIZE)
    frame_count = 0
    cam_offset = 0.0
    transition_frames = 0
    transition_label = ""
    best_fitness_history = []

    running = True
    while running:
        clock.tick(FPS)
        frame_count += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit(0)

        if transition_frames > 0:
            transition_frames -= 1
        else:
            if frame_count >= SIMULATION_TIME or ga.all_dead():
                prev_gen = ga.generation
                best_fitness_history.append(max(c.fitness for c in ga.population))
                if len(best_fitness_history) > 60:
                    best_fitness_history.pop(0)
                ga.evolve()
                frame_count = 0
                transition_frames = 30
                transition_label = f"Gen {prev_gen} -> Gen {ga.generation}"
            ga.update()

        # Determine camera offset: smoothly follow the car with highest x
        leader = max(ga.population, key=lambda c: c.x)
        target = leader.x - CAMERA_OFFSET_X
        cam_offset += 0.1 * (target - cam_offset)
        if cam_offset < 0: cam_offset = 0.0

        screen.blit(sky_surface, (0, 0))
        draw_track(screen, cam_offset, track_surface)
        ga.draw(screen, cam_offset)
        # Leaderboard
        draw_leaderboard(screen, ga.population, FONT_LEADER)
        # Display generation counter
        gen_text = FONT_HUD.render(f"Gen: {ga.generation}", True, (255, 255, 255))
        screen.blit(gen_text, (10, 10))
        # Best-fitness sparkline directly under Gen label
        draw_sparkline(screen, best_fitness_history, 10, 10 + gen_text.get_height() + 4,
                       150, 40, FONT_LEADER)
        hint_text = FONT_HUD.render("ESC to quit", True, (255, 255, 255))
        screen.blit(hint_text, (10, HEIGHT - 24))

        # Generation transition card overlay
        if transition_frames > 0:
            card_w, card_h = 420, 140
            card_x = (WIDTH - card_w) // 2
            card_y = (HEIGHT - card_h) // 2
            card = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            pygame.draw.rect(card, (20, 20, 20, 200), (0, 0, card_w, card_h), border_radius=12)
            screen.blit(card, (card_x, card_y))
            title = FONT_TITLE.render(transition_label, True, (255, 255, 255))
            title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(title, title_rect)

        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()
