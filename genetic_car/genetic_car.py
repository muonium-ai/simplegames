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
    def __init__(self, gene=None, name=None, color=None, left_wheel_size=None, right_wheel_size=None):
        self.x = 50
        self.y = get_track_y(50)
        # Set a random initial rotation
        self.angle = random.uniform(0, 2 * math.pi)
        self.gene = gene if gene is not None else random.uniform(0.5, 1.5)
        self.name = name if name is not None else random.choice(VARIANT_NAMES)
        self.color = color if color is not None else random.choice(VARIANT_COLORS)
        # Use different wheel sizes on both ends by default.
        self.left_wheel_size = left_wheel_size if left_wheel_size is not None else random.randint(8, 12)
        self.right_wheel_size = right_wheel_size if right_wheel_size is not None else random.randint(8, 12)
        self.vy = 0
        self.alive = True
        self.fitness = 0
        self.wheel_rotation = 0  # For rotation visualization

    def update(self):
        if not self.alive:
            return
        baseline = get_track_y(self.x)
        sensor = (self.y - baseline) / (HEIGHT / 2)
        correction = -self.gene * sensor
        self.angle += correction * 0.05

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
            self.x += SPEED * math.cos(self.angle)
            self.wheel_rotation += SPEED / min(self.left_wheel_size, self.right_wheel_size)
        else:
            self.x += 0.2 * SPEED * math.cos(self.angle)
        
        self.y += SPEED * math.sin(self.angle) + self.vy
        self.vy += GRAVITY

        if abs(self.y - baseline) < ground_threshold and self.vy >= 0:
            self.y = baseline
            self.vy = 0
            if random.random() < JUMP_PROB:
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

    def draw(self, screen, cam_offset):
        x_draw = int(self.x - cam_offset)
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
        print(f"Generation {self.generation}: Best = {best.fitness:.2f} ({best.name}) gene = {best.gene:.2f}")
        new_population = []
        # Elitism: preserve winner exactly
        new_population.append(Car(gene=best.gene, name=best.name, color=best.color,
                                  left_wheel_size=best.left_wheel_size, right_wheel_size=best.right_wheel_size))
        # Create children with additional mutations in variant properties
        while len(new_population) < len(self.population):
            parent1 = self.tournament_selection()
            parent2 = self.tournament_selection()
            child_gene = (parent1.gene + parent2.gene) / 2
            child_gene = self.mutate(child_gene)
            # Inherit and mutate variant properties slightly
            child_color = tuple(min(255, max(0, int((parent1.color[i] + parent2.color[i]) / 2 +
                            random.randint(-10, 10)))) for i in range(3))
            child_left_wheel_size = max(2, int((parent1.left_wheel_size + parent2.left_wheel_size) / 2 +
                                          random.choice([-1,0,1])))
            child_right_wheel_size = max(2, int((parent1.right_wheel_size + parent2.right_wheel_size) / 2 +
                                          random.choice([-1,0,1])))
            child_name = random.choice(VARIANT_NAMES)
            new_population.append(Car(gene=child_gene, name=child_name, color=child_color,
                                      left_wheel_size=child_left_wheel_size, right_wheel_size=child_right_wheel_size))
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
