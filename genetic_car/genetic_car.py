from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame, random, math

# Simulation constants
WIDTH, HEIGHT = 800, 600
FPS = 60
SIMULATION_TIME = 15 * FPS  # simulate each generation for 15 seconds
POPULATION_SIZE = 20
SPEED = 5  # constant forward speed
MUTATION_RATE = 0.1

# Car class: each car has a gene (responsiveness), position, angle, alive status, and fitness (x distance)
class Car:
    def __init__(self, gene=None):
        self.x = 50
        self.y = HEIGHT // 2
        self.angle = 0         # in radians; 0 means rightward
        self.gene = gene if gene is not None else random.uniform(0.5, 1.5)
        self.alive = True
        self.fitness = 0

    def update(self):
        if not self.alive:
            return
        # Sensor: measure vertical offset normalized (-1 at top, +1 at bottom)
        sensor = (self.y - HEIGHT/2) / (HEIGHT/2)
        # Steering correction: if sensor > 0 then car is below center and should turn upward.
        correction = - self.gene * sensor
        # Update angle (small change proportional to correction)
        self.angle += correction * 0.05  # 0.05 is tuning factor
        # Move forward
        self.x += SPEED * math.cos(self.angle)
        self.y += SPEED * math.sin(self.angle)
        # Check boundaries: if out of vertical bounds, car crashes.
        if self.y < 0 or self.y > HEIGHT:
            self.alive = False
        # Fitness is horizontal progress
        self.fitness = self.x

    def draw(self, screen):
        if not self.alive:
            color = (150, 150, 150)
        else:
            color = (255, 0, 0)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 5)

# Genetic algorithm class: maintains population and reproduces new generations
class GeneticAlgorithm:
    def __init__(self, population_size):
        self.population = [Car() for _ in range(population_size)]
        self.generation = 1

    def all_dead(self):
        return all(not car.alive for car in self.population)

    def update(self):
        for car in self.population:
            car.update()

    def draw(self, screen):
        for car in self.population:
            car.draw(screen)

    def evolve(self):
        # Sort cars by fitness (highest first)
        sorted_population = sorted(self.population, key=lambda c: c.fitness, reverse=True)
        best = sorted_population[0]
        print(f"Generation {self.generation}: Best fitness = {best.fitness:.2f} with gene = {best.gene:.2f}")
        new_population = []
        # Elitism: copy top performer
        new_population.append(Car(gene=best.gene))
        while len(new_population) < len(self.population):
            # Select two parents via tournament selection
            parent1 = self.tournament_selection()
            parent2 = self.tournament_selection()
            child_gene = self.crossover(parent1.gene, parent2.gene)
            child_gene = self.mutate(child_gene)
            new_population.append(Car(gene=child_gene))
        self.population = new_population
        self.generation += 1

    def tournament_selection(self, k=3):
        # Randomly choose k individuals and return the best.
        candidates = random.sample(self.population, k)
        return max(candidates, key=lambda c: c.fitness)

    def crossover(self, gene1, gene2):
        # Simple average crossover
        return (gene1 + gene2) / 2

    def mutate(self, gene):
        if random.random() < MUTATION_RATE:
            gene += random.uniform(-0.2, 0.2)
        return max(0.1, gene)  # Ensure gene remains positive

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

        # Update simulation if generation time not exceeded and at least one car is alive
        if frame_count < SIMULATION_TIME and not ga.all_dead():
            ga.update()
        else:
            # Evolve new generation
            ga.evolve()
            frame_count = 0

        screen.fill((30, 30, 30))
        # Draw center line as ideal path reference
        pygame.draw.line(screen, (0, 255, 0), (0, HEIGHT//2), (WIDTH, HEIGHT//2), 1)
        ga.draw(screen)
        # Display generation counter
        font = pygame.font.SysFont(None, 24)
        gen_text = font.render(f"Generation: {ga.generation}", True, (255, 255, 255))
        screen.blit(gen_text, (10, 10))
        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()
