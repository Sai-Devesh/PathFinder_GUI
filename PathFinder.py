import pygame
import heapq

pygame.init()
WIDTH = 800
screen = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("GUI of Dijkstra's Path Finding Algorithm")

WHITE = (255, 255, 255) # Deafult colour for weight 1 (no traffic)
BLUE = (0, 0, 255)      # Colour for Less Traffic (weight 2)
ORANGE = (255, 165, 0)  # Colour for Moderate traffic (weight 4)
RED = (255, 0, 0)       # Colour for Heavy Traffic (weight 8)
CYAN = (0, 255, 255)    # Colour for the Start point
PINK = (255, 192, 203)  # Colour for destination point
YELLOW = (255, 255, 0)  # Colour for visited Boxes
GREEN = (0, 255, 0)     # Colour for Available Box
BLACK = (0, 0, 0)       # Colour for Blocked Box
PURPLE = (128, 0, 128)  # Colour for displaying best path
GRAY = (127, 127, 127)  # Colour for drascreeng lines

class Spot:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows
        self.weight = 1

    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == YELLOW

    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == BLUE

    def is_end(self):
        return self.color == PINK

    def make_closed(self):
        self.color = YELLOW

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_start(self):
        self.color = BLUE

    def make_end(self):
        self.color = PINK

    def make_path(self):
        self.color = PURPLE

    def make_weighted_road(self, weight):
        if weight == 2:
            self.color = CYAN
        elif weight == 4:
            self.color = ORANGE
        elif weight == 8:
            self.color = RED
        self.weight = weight

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():  # Up
            self.neighbors.append(grid[self.row - 1][self.col])
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():  # Down
            self.neighbors.append(grid[self.row + 1][self.col])
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():  # Left
            self.neighbors.append(grid[self.row][self.col - 1])
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():  # Right
            self.neighbors.append(grid[self.row][self.col + 1])

# Implementation of Dijkstra's Algorithm
def dijkstra(draw, grid, start, end):
    count = 0
    open_set = []
    heapq.heappush(open_set, (0, count, start))
    predecessor = {}
    distances = {spot: float("inf") for row in grid for spot in row}
    distances[start] = 0
    open_set_hash = {start} # For searching in O(1) time

    while open_set:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = heapq.heappop(open_set)[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(predecessor, end, draw)
            end.make_end()
            return True

        for neighbor in current.neighbors:
            temp_distances = distances[current] + neighbor.weight

            if temp_distances < distances[neighbor]:
                predecessor[neighbor] = current
                distances[neighbor] = temp_distances
                if neighbor not in open_set_hash:
                    count += 1
                    heapq.heappush(open_set, (distances[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        draw()

        if current != start:
            current.make_closed()

    return False

# Reconstruct path from start to end
def reconstruct_path(predecessor, current, draw):
    while current in predecessor:
        current = predecessor[current]
        current.make_path()
        draw()

# Grid creation
def make_grid(rows, WIDTH, gap):
    grid = []
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot)

    return grid

# Draw grid lines
def draw_grid(screen, rows, WIDTH, gap):
    for i in range(rows):
        pygame.draw.line(screen, GRAY, (0, i * gap), (WIDTH, i * gap))
        for j in range(rows):
            pygame.draw.line(screen, GRAY, (j * gap, 0), (j * gap, WIDTH))

# Filling the grid but rectangular spots and then drawing lines to show them
def draw(screen, grid, rows, WIDTH, gap):
    screen.fill(WHITE)

    for row in grid:
        for spot in row:
            spot.draw(screen)

    draw_grid(screen, rows, WIDTH, gap)
    pygame.display.update()

# Main function
ROWS = 40
gap = WIDTH // ROWS
grid = make_grid(ROWS, WIDTH, gap)
start = None
end = None
run = True
current_weight = 1

while run:
    draw(screen, grid, ROWS, WIDTH, gap)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if pygame.mouse.get_pressed()[0]:  # Left mouse button
            row,col = pygame.mouse.get_pos()
            row = row // gap
            col = col // gap 
            spot = grid[row][col]
            if not start and spot != end:
                start = spot
                start.make_start()

            elif not end and spot != start:
                end = spot
                end.make_end()

            elif spot != end and spot != start:
                spot.make_weighted_road(current_weight)

        if pygame.mouse.get_pressed()[2]:  # Right mouse button
            row,col = pygame.mouse.get_pos()
            row = row // gap
            col = col // gap 
            spot = grid[row][col]
            if spot != start and spot != end:
                spot.make_barrier()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                current_weight = 2
            elif event.key == pygame.K_2:
                current_weight = 4
            elif event.key == pygame.K_3:
                current_weight = 8

            if event.key == pygame.K_SPACE and start and end:
                for row in grid:
                    for spot in row:
                        spot.update_neighbors(grid)

                dijkstra(lambda: draw(screen, grid, ROWS, WIDTH, gap), grid, start, end)

            if event.key == pygame.K_r:
                start = None
                end = None
                grid = make_grid(ROWS, WIDTH, gap)

pygame.quit()

