import pygame
import os
import random
import math
import sys
import neat
import pickle
import pandas as pd
import multiprocessing

pygame.init() # Initialize imported pygame modules.
pygame.display.set_caption('Flappy Bird AI Experimental A')

# Global variables.
screen_height = 600
screen_width = 270

best = None
best_fit = -1e400
# screen = pygame.display.set_mode((screen_width, screen_height))

results = []

bg = pygame.image.load(os.path.join(sys.path[0], 'FlappyBird/background-day.png'))

base = pygame.image.load(os.path.join(sys.path[0], 'FlappyBird/base.png'))

pipe = pygame.image.load(os.path.join(sys.path[0], 'FlappyBird/pipe-green.png'))

birds = [pygame.image.load(os.path.join(sys.path[0], 'FlappyBird/yellowbird-downflap.png')),
         pygame.image.load(os.path.join(sys.path[0], 'FlappyBird/yellowbird-midflap.png')),
         pygame.image.load(os.path.join(sys.path[0], 'FlappyBird/yellowbird-upflap.png'))]

numbers = [pygame.image.load(os.path.join(sys.path[0], 'FlappyBird/0.png')),
           pygame.image.load(os.path.join(sys.path[0], 'FlappyBird/1.png')),
           pygame.image.load(os.path.join(sys.path[0], 'FlappyBird/2.png')),
           pygame.image.load(os.path.join(sys.path[0], 'FlappyBird/3.png')),
           pygame.image.load(os.path.join(sys.path[0], 'FlappyBird/4.png')),
           pygame.image.load(os.path.join(sys.path[0], 'FlappyBird/5.png')),
           pygame.image.load(os.path.join(sys.path[0], 'FlappyBird/6.png')),
           pygame.image.load(os.path.join(sys.path[0], 'FlappyBird/7.png')),
           pygame.image.load(os.path.join(sys.path[0], 'FlappyBird/8.png')),
           pygame.image.load(os.path.join(sys.path[0], 'FlappyBird/9.png'))]

bg_height = bg.get_height()
base_height = base.get_height()

font = pygame.font.Font('freesansbold.ttf', 30)

def display_score(score): # Function to draw the user's score on the screen.
    score = str(score)
    
    displacement = 0
    
    for digit in score:
        displacement += numbers[int(digit)].get_width()
    displacement = displacement / 2
    
    for digit in score:
        image = numbers[int(digit)]
        # screen.blit(image, ((screen_width / 2)-displacement, 10))
        displacement -= image.get_width()
        


# Bird Class.
class Bird:
    DY = 5
    
    def __init__(self, x, y, image = birds[0]):
        # Declare attributes of a bird instance.
        self.image = image
        self.x = x
        self.y = y
        
        self.dy = self.DY
        self.gravity = 0.1
        
        self.jump_state = 0
        self.jump_limit = 65
        self.jumping = False
        
        self.angle = 0
        
        self.step_index = 0
        
        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
    
    def update(self):
        global obstacles
        if self.jumping:
            self.dy = self.DY
            
            if self.jump_state < self.jump_limit:
                self.y -= self.dy
                self.jump_state += self.dy
            else:
                self.jumping = False
                self.jump_state = 0
                
            self.draw()
        else:
            self.y += self.dy
            self.dy += self.gravity
            
            self.draw()
        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())

        for obstacle in obstacles: # Detect collision between the bird and each obstacle.
            if (self.y+self.image.get_height() > bg_height):
                return -1
            if self.y < 0 and (self.x+self.image.get_width()) > obstacles[0].x:
                return -1
            if pygame.Rect.colliderect(self.rect, obstacle.rect1) or pygame.Rect.colliderect(self.rect, obstacle.rect2):
                return -1
    def draw(self):
        if self.jumping:
            if self.step_index >= 15:
                self.step_index = 0
                
            self.angle = 20
            self.image = pygame.transform.rotate(birds[self.step_index // 5], self.angle)
      
            
            # screen.blit(self.image, (self.x, self.y))
        else:
            self.angle -= 3 # Compute the angular displacement of the bird's beak.
            
            if self.angle < -90:
                self.angle = -90
            self.image = pygame.transform.rotate(birds[2], self.angle)
            
            # screen.blit(self.image, (self.x, self.y))

    
class Obstacle: # Obstacle class.
    global bg_height
    def __init__(self, x, image = pipe): # Declare attributes for obstacle instance.
        self.x = x
        self.image = image
        
        self.gap = 177
        self.dx = 1
        
        self.maximum = self.image.get_height()
        self.minimum = self.maximum * 0.2
        self.passed = False
        
        self.top_height = random.random()*(self.maximum-self.minimum)+self.minimum
        
        self.rect1 = pygame.Rect(self.x, bg_height-self.top_height-self.gap-self.image.get_height(), self.image.get_width(), self.image.get_height())
        self.rect2 = pygame.Rect(self.x, self.image.get_height()+self.rect1.topright[1]+self.gap, self.image.get_width(), self.image.get_height())
        
    def update(self):
        global points, obstacles
        self.x -= self.dx
        
        if living_birds[0].x > self.rect1.bottomright[0] and not self.passed:
            points += 1
                
            self.passed = True
            self.draw()
        elif self.x < -self.image.get_width():
            obstacles = obstacles[1:]
        else:
            self.draw()
        
        self.rect1 = pygame.Rect(self.x, bg_height-self.top_height-self.gap-self.image.get_height(), self.image.get_width(), self.image.get_height())
        self.rect2 = pygame.Rect(self.x, self.image.get_height()+self.rect1.topright[1]+self.gap, self.image.get_width(), self.image.get_height())
        
        
    def draw(self):
        top = pygame.transform.flip(self.image, False, True)
        bottom = self.image

        # screen.blit(top, (self.x, bg_height-self.top_height-self.gap-self.image.get_height()))
        # screen.blit(bottom, (self.x, top.get_height()+self.rect1.topright[1]+self.gap))

def remove(i): # Removes a bird, genome, and neural net at a particular index.
    living_birds.pop(i)
    ge.pop(i)
    nets.pop(i)
    
def eval_genomes(genomes, config): # main function.
    global bg_height, obstacles, ge, nets, living_birds, points, best, best_fit, results
    
    # Initialize variables.
    points = 0
    living_birds = []
    
    count = 0
    
    obstacle_gap = 200
    
    ge = []
    nets = []
    
    obstacles = [Obstacle(280)]
    
    if (screen_width-obstacles[-1].x-2*obstacles[0].image.get_width()-obstacle_gap) > 0:
        obstacles.append(Obstacle(280+obstacles[0].image.get_width()+obstacle_gap))
    
    # Declares the neural nets for a run.
    
    for genome_id, genome in genomes:
        living_birds.append(Bird(20, screen_height // 2))
        ge.append(genome)
        
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0
      
     
    
    while True:
        # screen.fill([255,255,255])
        # screen.blit(bg, (0, 0))
        for i, obstacle in enumerate(obstacles):
            obstacle.update()
        
        # screen.blit(base, (0, bg_height))
        
        count += 1
        
        for i, bird in enumerate(living_birds):
            if count % 9 == 0: # Only feed the bird's stats to the neural net every ninth iteration. It makes the movements look more human.
                output = nets[i].activate((bird.y, bird.dy, bird.angle, obstacles[0].rect1.bottomright[1], obstacles[0].rect2.topright[1], abs(obstacles[0].rect1.bottomleft[0]-bird.x)))
                if output[0] > 0.7: # If the probability that the bird should jump is > 0.7, the bird jumps.
                    bird.jumping = True

            
            if bird.update() == -1: # If collision is detected, remove the bird.
                
                ge[i].fitness = math.e ** (-points)
                
                if ge[i].fitness > best_fit: # If the genome is more 'fit' for the environment, it becomes the best genome.
                    best_fit = ge[i].fitness
                    best = nets[i]

                remove(i)
                
        
        if len(living_birds) == 0 or points > 300: # If there are no more birds, terminate the game. Also, this sets a max score so the game doesn't go on too long.
            print('\n')
            print(f'{pop.generation} : {points}')
            print('\n')
            
            results[0].append(points)
            break
        if len(obstacles) == 0 or (screen_width-obstacles[-1].x-obstacles[-1].image.get_width()-obstacle_gap > 0): # Adds a new obstacle.
            obstacles.append(Obstacle(screen_width))
        
        #display_score(points)

        #pygame.display.update()

def run(config_path, index):
    global pop, results
    
    results = [[]]
    
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )
    
    pop = neat.Population(config)
    pop.run(eval_genomes, 300) # Run eval_genomes for 300 generations.
    
    pickle.dump(best, open(os.path.join(sys.path[0], 'ExperimentalBirdsA/experimental_bird_a.pkl'), 'wb'))
    
    results = pd.DataFrame(results)
    
    results.to_csv(os.path.join(sys.path[0], f'ExperimentalBirdAData/experimental_bird_a_data.csv'), mode = 'a', index = False, header = False)

if __name__ == '__main__':
    config_path = os.path.join(os.path.join(sys.path[0], 'config.txt'))
    
    
    processes = []
    
    for index in range(6):
        processes.append(multiprocessing.Process(target = run, args = [config_path, index]))

    for index in range(len(processes)):
        processes[index].start()
