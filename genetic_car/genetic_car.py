from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame, random, math

# Simulation and physics constants
WIDTH, HEIGHT = 800, 600
FPS = 60
SIMULATION_TIME = 15 * FPS  # 15 seconds per generation
POPULATION_SIZE = 20
SPEED = 5  # horizontal speed component
GRAVITY = 0.3
JUMP_STRENGTH = -7  # impulse when jumping
JUMP_PROB = 0.05    # probability to auto-jump upon landing
MUTATION_RATE = 0.1

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
    if x <= track_points[0][0]:
        return track_points[0][1]
    if x >= track_points[-1][0]:
        return track_points[-1][1]
    for i in range(len(track_points)-1):
        x1, y1 = track_points[i]
        x2, y2 = track_points[i+1]
        if x1 <= x <= x2:
            t = (x - x1) / (x2 - x1)
            return y1 + t * (y2 - y1)
    return base_y

def draw_track(screen, cam_offset):
    pts = [(x - cam_offset, get_track_y(x)) for x in range(0, TRACK_LENGTH + 1, 10)]
    if pts:
        pygame.draw.lines(screen, (0, 255, 0), False, pts, 3)

# Helper: rotate a point (px, py) around origin by an angle (radians)
def rotate_point(px, py, angle):
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    return (px * cos_a - py * sin_a, px * sin_a + py * cos_a)

# Car class with extra variant properties and physics
class Car:
    def __init__(self, gene=None, name=None, color=None, wheel_size=None, wheel_offsets=None):
        self.x = 50
        self.y = get_track_y(50)
        self.angle = 0  # 0 radians: rightward
        self.gene = gene if gene is not None else random.uniform(0.5, 1.5)
        # Variant properties
        self.name = name if name is not None else random.choice(VARIANT_NAMES)
        self.color = color if color is not None else random.choice(VARIANT_COLORS)
        # Use bigger wheels by default.
        self.wheel_size = wheel_size if wheel_size is not None else random.randint(8, 12)
        # wheel_offsets: list of tuples relative to car center (can be more than one wheel)
        self.wheel_offsets = wheel_offsets if wheel_offsets is not None else [(-15, -10), (-15, 10)]
        self.vy = 0  # vertical speed
        self.alive = True
        self.fitness = 0
        self.wheel_rotation = 0  # New attribute for tracking rotation

    def update(self):
        if not self.alive:
            return
        # Sensor relative to track baseline
        baseline = get_track_y(self.x)
        sensor = (self.y - baseline) / (HEIGHT / 2)
        correction = -self.gene * sensor
        self.angle += correction * 0.05
        
        # Horizontal movement only happens fully if wheels touch ground.
        if abs(self.y - baseline) < 5:
            self.x += SPEED * math.cos(self.angle)
            self.wheel_rotation += SPEED / self.wheel_size
        else:
            self.x += 0.2 * SPEED * math.cos(self.angle)
        
        # Vertical physics: add jump physics and gravity
        self.y += SPEED * math.sin(self.angle) + self.vy
        self.vy += GRAVITY

        # Check if car is near the ground (track)
        if abs(self.y - baseline) < 5 and self.vy >= 0:
            self.y = baseline
            self.vy = 0
            # Allow jump with small probability
            if random.random() < JUMP_PROB:
                self.vy = JUMP_STRENGTH

        # If car falls too far from track, it crashes
        deviation = abs(self.y - baseline)
        if deviation > TRACK_TOLERANCE:
            self.alive = False
        # Fitness: horizontal progress with a penalty for deviation
        self.fitness = self.x - 0.2 * deviation

    def draw(self, screen, cam_offset):
        x_draw = int(self.x - cam_offset)
        # Draw two chassis triangles
        # Front triangle (larger)
        front_chassis = [(20, 0), (0, -15), (0, 15)]
        front_points = []
        for px, py in front_chassis:
            rx, ry = rotate_point(px, py, self.angle)
            front_points.append((x_draw + int(rx), int(self.y + ry)))
        # Rear triangle (smaller)
        rear_chassis = [(0, 0), (-15, -10), (-15, 10)]
        rear_points = []
        for px, py in rear_chassis:
            rx, ry = rotate_point(px, py, self.angle)
            rear_points.append((x_draw + int(rx), int(self.y + ry)))
        col = (150,150,150) if not self.alive else self.color
        pygame.draw.polygon(screen, col, front_points)
        pygame.draw.polygon(screen, col, rear_points)
        
        # Draw wheels with rotation indicator
        for off in self.wheel_offsets:
            rx, ry = rotate_point(off[0], off[1], self.angle)
            wx = x_draw + int(rx)
            wy = int(self.y + ry)
            pygame.draw.circle(screen, (0, 0, 0), (wx, wy), self.wheel_size)
            # Draw a line inside the wheel to show rotation.
            line_length = int(self.wheel_size * 0.8)
            end_x = wx + int(line_length * math.cos(self.wheel_rotation))
            end_y = wy + int(line_length * math.sin(self.wheel_rotation))
            pygame.draw.line(screen, (255, 255, 255), (wx, wy), (end_x, end_y), 2)

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
        print(f"Generation {self.generation}: Best = {best.fitness:.2f} ({best.name}) gene = {best.gene:.2f}")
        new_population = []
        # Elitism: preserve winner exactly
        new_population.append(Car(gene=best.gene, name=best.name, color=best.color,
                                  wheel_size=best.wheel_size, wheel_offsets=best.wheel_offsets))
        # Create children with additional mutations in variant properties
        while len(new_population) < len(self.population):
            parent1 = self.tournament_selection()
            parent2 = self.tournament_selection()
            child_gene = (parent1.gene + parent2.gene) / 2
            child_gene = self.mutate(child_gene)
            # Inherit and mutate variant properties slightly
            child_color = tuple(min(255, max(0, int((parent1.color[i] + parent2.color[i]) / 2 +
                            random.randint(-10, 10)))) for i in range(3))
            child_wheel_size = max(2, int((parent1.wheel_size + parent2.wheel_size) / 2 +
                                          random.choice([-1,0,1])))
            # Mutate wheel offsets randomly
            base_offsets = [(-15, -10), (-15, 10)]
            child_offsets = []
            for off in base_offsets:
                ox = off[0] + random.randint(-3, 3)
                oy = off[1] + random.randint(-3, 3)
                child_offsets.append((ox, oy))
            child_name = random.choice(VARIANT_NAMES)
            new_population.append(Car(gene=child_gene, name=child_name, color=child_color,
                                      wheel_size=child_wheel_size, wheel_offsets=child_offsets))
        self.population = new_population
        self.generation += 1

    def tournament_selection(self, k=3):
        candidates = random.sample(self.population, k)
        return max(candidates, key=lambda c: c.fitness)

    def mutate(self, gene):
        if random.random() < MUTATION_RATE:
            gene += random.uniform(-0.2, 0.2)
        return max(0.1, gene)

def draw_leaderboard(screen, population):
    # Sort by fitness descending and display name and fitness
    sorted_pops = sorted(population, key=lambda c: c.fitness, reverse=True)
    font = pygame.font.SysFont(None, 20)
    y_offset = 10
    for car in sorted_pops:
        text = font.render(f"{car.name}: {int(car.fitness)}", True, (255,255,255))
        screen.blit(text, (WIDTH - 150, y_offset))
        y_offset += 20

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Genetic Car Simulation")
    clock = pygame.time.Clock()

    ga = GeneticAlgorithm(POPULATION_SIZE)
    frame_count = 0

    running = True
    while running:
        clock.tick(FPS)
        frame_count += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if frame_count < SIMULATION_TIME and not ga.all_dead():
            ga.update()
        else:
            ga.evolve()
            frame_count = 0

        # Determine camera offset: follow the car with highest x
        leader = max(ga.population, key=lambda c: c.x)
        cam_offset = leader.x - CAMERA_OFFSET_X
        if cam_offset < 0: cam_offset = 0

        screen.fill((100, 100, 100))
        draw_track(screen, cam_offset)
        ga.draw(screen, cam_offset)
        # Leaderboard
        draw_leaderboard(screen, ga.population)
        # Display generation counter
        font = pygame.font.SysFont(None, 24)
        gen_text = font.render(f"Gen: {ga.generation}", True, (255, 255, 255))
        screen.blit(gen_text, (10, 10))
        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()
