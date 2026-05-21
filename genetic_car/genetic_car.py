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

# Leader spotlight vignette (opt-out via this flag)
VIGNETTE_ENABLED = True

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

def build_clouds_layer():
    """Procedurally draw a wide tileable cloud layer with low-alpha white ovals."""
    layer_w = WIDTH * 2
    surf = pygame.Surface((layer_w, HEIGHT), pygame.SRCALPHA)
    rng = random.Random(1001)
    upper_third = HEIGHT // 3
    num_clouds = 14
    for _ in range(num_clouds):
        cx = rng.randint(0, layer_w)
        cy = rng.randint(10, max(11, upper_third))
        w = rng.randint(80, 160)
        h = rng.randint(20, 40)
        alpha = rng.randint(50, 110)
        # Soft cloud: draw a few overlapping ellipses to give a puffy look
        for k in range(3):
            ox = rng.randint(-w // 4, w // 4)
            oy = rng.randint(-h // 4, h // 4)
            pygame.draw.ellipse(surf, (255, 255, 255, alpha),
                                (cx + ox - w // 2, cy + oy - h // 2, w, h))
    return surf


def build_mountains_layer():
    """Procedurally draw a wide tileable zigzag mountain silhouette layer."""
    layer_w = WIDTH * 2
    surf = pygame.Surface((layer_w, HEIGHT), pygame.SRCALPHA)
    rng = random.Random(2002)
    color = (70, 90, 110)
    band_top = HEIGHT // 4
    band_bottom = HEIGHT // 2 + 20
    step = 60
    pts = [(0, band_bottom)]
    x = 0
    while x <= layer_w:
        peak_y = rng.randint(band_top, band_bottom - 40)
        pts.append((x, peak_y))
        x += step
    pts.append((layer_w, band_bottom))
    pts.append((layer_w, HEIGHT))
    pts.append((0, HEIGHT))
    pygame.draw.polygon(surf, color, pts)
    return surf


def build_hills_layer():
    """Procedurally draw a wide tileable smoother hill silhouette layer."""
    layer_w = WIDTH * 2
    surf = pygame.Surface((layer_w, HEIGHT), pygame.SRCALPHA)
    rng = random.Random(3003)
    color = (40, 80, 50)
    band_top = HEIGHT // 2 + 10
    band_bottom = HEIGHT // 2 + 80
    step = 30
    pts = [(0, band_bottom)]
    x = 0
    # Smoother: small step + averaged variation
    prev_y = rng.randint(band_top, band_bottom - 20)
    while x <= layer_w:
        target = rng.randint(band_top, band_bottom - 10)
        # average for smoothing
        y = (prev_y + target) // 2
        pts.append((x, y))
        prev_y = y
        x += step
    pts.append((layer_w, band_bottom))
    pts.append((layer_w, HEIGHT))
    pts.append((0, HEIGHT))
    pygame.draw.polygon(surf, color, pts)
    return surf


def draw_parallax_layer(screen, layer, cam_offset, scroll_factor):
    """Blit a wide tileable layer twice so it wraps seamlessly given cam_offset."""
    lw = layer.get_width()
    shift = (cam_offset * scroll_factor) % lw
    screen.blit(layer, (-int(shift), 0))
    screen.blit(layer, (lw - int(shift), 0))


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
        # Dense full-trail capture (up to 600 frames) for winning-run replay
        self.full_trail = []  # list of (x, y, angle)
        self.has_won = False
        # Particle system: list of dicts {x, y, vx, vy, life, max_life, color}
        self.particles = []
        # Track previous-frame wheel contact for dust transition detection
        self.left_touch_prev = False
        self.right_touch_prev = False

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

        # Maintain dense full-trail for winning replay (cap 600 frames).
        # Stop appending once the car has already won.
        if not self.has_won:
            self.full_trail.append((self.x, self.y, self.angle))
            if len(self.full_trail) > 600:
                self.full_trail.pop(0)

        # --- Particle system ---
        # Exhaust: when grounded and moving, spawn one gray particle behind
        if grounded and dx > 0.5:
            ex_off = rotate_point(-20, -2, self.angle)
            self.particles.append({
                "x": self.x + ex_off[0],
                "y": self.y + ex_off[1],
                "vx": -0.5 + random.uniform(-0.2, 0.2),
                "vy": -0.3 + random.uniform(-0.2, 0.2),
                "life": 30,
                "max_life": 30,
                "color": (150, 150, 150),
            })
        # Dust: when a wheel transitions from airborne -> grounded this frame
        if left_touch and not self.left_touch_prev:
            for _ in range(5):
                self.particles.append({
                    "x": rx_left,
                    "y": ry_left,
                    "vx": random.uniform(-0.6, 0.6),
                    "vy": random.uniform(-1.2, -0.3),
                    "life": 20,
                    "max_life": 20,
                    "color": (180, 150, 110),
                })
        if right_touch and not self.right_touch_prev:
            for _ in range(5):
                self.particles.append({
                    "x": rx_right,
                    "y": ry_right,
                    "vx": random.uniform(-0.6, 0.6),
                    "vy": random.uniform(-1.2, -0.3),
                    "life": 20,
                    "max_life": 20,
                    "color": (180, 150, 110),
                })
        # Update particles (advance, apply gravity, drop dead)
        alive_particles = []
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.05
            p["life"] -= 1
            if p["life"] > 0:
                alive_particles.append(p)
        self.particles = alive_particles
        # Cap total particles per car at 60 (drop oldest)
        if len(self.particles) > 60:
            self.particles = self.particles[-60:]
        # Store wheel-touch state for next frame's transition detection
        self.left_touch_prev = left_touch
        self.right_touch_prev = right_touch

        # Death conditions:
        # 1) Reached end of track
        if self.x >= TRACK_LENGTH:
            self.x = TRACK_LENGTH
            self.alive = False
            self.has_won = True
        # 2) Fell off the track (deviation beyond tolerance or off-screen vertically)
        elif deviation > TRACK_TOLERANCE or self.y > HEIGHT or self.y < 0:
            self.alive = False

    def draw(self, screen, cam_offset):
        x_draw = int(self.x - cam_offset)
        # Particles overlay (rendered before trail/chassis)
        if self.particles:
            part_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            for p in self.particles:
                a = max(0, min(255, int(255 * (p["life"] / p["max_life"]))))
                col = (p["color"][0], p["color"][1], p["color"][2], a)
                pygame.draw.circle(part_surf, col,
                                   (int(p["x"] - cam_offset), int(p["y"])), 2)
            screen.blit(part_surf, (0, 0))
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

def draw_ghost_car(screen, cam_offset, x, y, angle, color, left_wheel_size, right_wheel_size):
    """Render a translucent ghost-car at the given (x, y, angle) for replay."""
    x_draw = int(x - cam_offset)
    ghost = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    # Chassis
    half_length, half_height = 20, 5
    local_corners = [(half_length, half_height), (half_length, -half_height),
                     (-half_length, -half_height), (-half_length, half_height)]
    chassis_points = []
    for cx, cy in local_corners:
        rx, ry = rotate_point(cx, cy, angle)
        chassis_points.append((x_draw + int(rx), int(y + ry)))
    pygame.draw.polygon(ghost, (color[0], color[1], color[2], 200), chassis_points)
    # Wheels
    for offset, wsize in [((-20, 8), left_wheel_size), ((20, 8), right_wheel_size)]:
        r = rotate_point(offset[0], offset[1], angle)
        wx = x_draw + int(r[0])
        wy = int(y + r[1])
        pygame.draw.circle(ghost, (0, 0, 0, 220), (wx, wy), wsize)
    screen.blit(ghost, (0, 0))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Genetic Car Simulation")
    clock = pygame.time.Clock()

    sky_surface = build_sky_gradient()
    clouds_layer = build_clouds_layer()
    mountains_layer = build_mountains_layer()
    hills_layer = build_hills_layer()
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
    # Replay state for winning-run slow-mo (T-000087)
    replay_state = None  # None or "playing"
    replay_frames = 0    # remaining replay frames
    replay_trail_idx = 0
    winning_run = None   # dict with snapshot of winner's full_trail/color/wheels/gen

    running = True
    while running:
        clock.tick(FPS)
        frame_count += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit(0)

        if replay_state == "playing":
            # Pause normal simulation; advance ghost trail at 1/3 speed.
            replay_frames -= 1
            if replay_frames % 3 == 0 and winning_run is not None:
                if replay_trail_idx < len(winning_run["full_trail"]) - 1:
                    replay_trail_idx += 1
            # Camera centers on ghost position
            if winning_run is not None and winning_run["full_trail"]:
                gx, gy, _ga = winning_run["full_trail"][replay_trail_idx]
                cam_offset = gx - WIDTH // 2
                if cam_offset < 0:
                    cam_offset = 0.0
            if replay_frames <= 0:
                # Replay finished: do the deferred evolve + transition card.
                prev_gen = ga.generation
                best_fitness_history.append(max(c.fitness for c in ga.population))
                if len(best_fitness_history) > 60:
                    best_fitness_history.pop(0)
                ga.evolve()
                frame_count = 0
                transition_frames = 30
                transition_label = f"Gen {prev_gen} -> Gen {ga.generation}"
                replay_state = None
                winning_run = None
                replay_trail_idx = 0
        elif transition_frames > 0:
            transition_frames -= 1
        else:
            if frame_count >= SIMULATION_TIME or ga.all_dead():
                # Check for a winner this generation; if found, enter replay
                # BEFORE evolving (single-winner: pick first to win, i.e.
                # the one with the longest full_trail among winners).
                winners = [c for c in ga.population if c.has_won and c.full_trail]
                if winners:
                    winner = max(winners, key=lambda c: len(c.full_trail))
                    winning_run = {
                        "full_trail": list(winner.full_trail),
                        "color": winner.color,
                        "left_wheel_size": winner.left_wheel_size,
                        "right_wheel_size": winner.right_wheel_size,
                        "gen": ga.generation,
                    }
                    replay_state = "playing"
                    replay_frames = 360
                    replay_trail_idx = 0
                else:
                    prev_gen = ga.generation
                    best_fitness_history.append(max(c.fitness for c in ga.population))
                    if len(best_fitness_history) > 60:
                        best_fitness_history.pop(0)
                    ga.evolve()
                    frame_count = 0
                    transition_frames = 30
                    transition_label = f"Gen {prev_gen} -> Gen {ga.generation}"
            if replay_state != "playing":
                ga.update()

        # Determine camera offset: smoothly follow the car with highest x
        # (Skip lerp during replay: camera centered on ghost above.)
        leader = max(ga.population, key=lambda c: c.x)
        if replay_state != "playing":
            target = leader.x - CAMERA_OFFSET_X
            cam_offset += 0.1 * (target - cam_offset)
            if cam_offset < 0: cam_offset = 0.0

        screen.blit(sky_surface, (0, 0))
        draw_parallax_layer(screen, clouds_layer, cam_offset, 0.1)
        draw_parallax_layer(screen, mountains_layer, cam_offset, 0.3)
        draw_parallax_layer(screen, hills_layer, cam_offset, 0.6)
        draw_track(screen, cam_offset, track_surface)
        if replay_state == "playing" and winning_run is not None and winning_run["full_trail"]:
            # Replay: draw only the ghost-car following the recorded full_trail
            gx, gy, ga_angle = winning_run["full_trail"][replay_trail_idx]
            draw_ghost_car(screen, cam_offset, gx, gy, ga_angle,
                           winning_run["color"],
                           winning_run["left_wheel_size"],
                           winning_run["right_wheel_size"])
        else:
            ga.draw(screen, cam_offset)
            # Leader spotlight vignette (after world rendering, before HUD)
            if VIGNETTE_ENABLED:
                vignette = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                vignette.fill((0, 0, 0, 120))
                cx = int(leader.x - cam_offset)
                cy = int(leader.y)
                # Cut a soft hole by drawing successively smaller circles with
                # lower alpha — outer rings stay darker, the leader sits in the
                # brightest center. Drawn outer-to-inner so the smallest circle
                # (alpha=0) ends up on top in the middle.
                for r, a in [(250, 90), (200, 60), (150, 30), (100, 10), (50, 0)]:
                    pygame.draw.circle(vignette, (0, 0, 0, a), (cx, cy), r)
                screen.blit(vignette, (0, 0))
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

        # Winning-run replay overlay
        if replay_state == "playing" and winning_run is not None:
            replay_label = f"WINNING RUN -- Gen {winning_run['gen']}"
            title = FONT_TITLE.render(replay_label, True, (255, 255, 255))
            title_rect = title.get_rect(center=(WIDTH // 2, 80))
            # Backing card for legibility
            pad = 20
            card_w = title_rect.width + pad * 2
            card_h = title_rect.height + pad
            card = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            pygame.draw.rect(card, (20, 20, 20, 200), (0, 0, card_w, card_h), border_radius=12)
            screen.blit(card, (title_rect.centerx - card_w // 2,
                               title_rect.centery - card_h // 2))
            screen.blit(title, title_rect)

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
