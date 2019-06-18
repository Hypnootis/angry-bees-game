import pygame #Some cool imports
import sys
import os
import random
import time

if getattr(sys, 'frozen', False): # PyInstaller adds this attribute
    # Running in a bundle
    CurrentPath = sys._MEIPASS
else:
    # Running in normal Python environment
    CurrentPath = ""                    #Copypasted from stackoverflow, not sure how it works or what it does, but it's there
pygame.init()
RED = [255, 0, 0]
BLUE = [0, 0, 255]
GREEN = [0, 255, 0] #Constants in caps, (probably) a messy pile of variables in lowercase
BLACK = [0, 0, 0]
WHITE = [255, 255, 255]
clock = pygame.time.Clock()
screen_width = 800
screen_length = 600
score = 0
instance_score = 0
items = []

font = pygame.font.Font(os.path.join("assets", "coolfont.ttf"), 24) #Font, duh

screen = pygame.display.set_mode((screen_width, screen_length)) #Setting the game window
pygame.display.set_caption("Dodging game 3000")

clock = pygame.time.Clock()
menu_png = pygame.image.load(os.path.join("assets", "menu_screen.png")).convert_alpha()

class button():
    def __init__(self, color, x,y,width,height, text=''):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.purchased = False

    def draw(self,win,outline=None):
        #Call this method to draw the button on the screen
        if outline:
            pygame.draw.rect(win, outline, (self.x-2,self.y-2,self.width+4,self.height+4),0)
            
        pygame.draw.rect(win, self.color, (self.x,self.y,self.width,self.height),0)
        
        if self.text != '':
            font = pygame.font.SysFont('comicsansms', 24)
            text = font.render(self.text, 1, (0,0,0))
            win.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))

    def isOver(self, pos):
        #Pos is the mouse position or a tuple of (x,y) coordinates
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True
            
        return False

class Projectile(pygame.sprite.Sprite): #Things that get shot at you
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(os.path.join("assets", "aurinko.jpg")).convert_alpha() #Placeholder image for the projectiles I had laying around
        self.image = pygame.transform.scale(self.image, (32, 32))
        self.set_colorkey = WHITE
        self.rect = self.image.get_rect()
        self.x_speed = random.randrange(5, 15) #Speed random to give illusion of clever programming
        
    def update(self): #Handles movement and stuff
        global score
        global instance_score
        if self.rect.x < 0: #If they go off the screen, put them back so it seems like more projectiles are spawning
            self.rect.x = screen_width + 64
            self.rect.y = random.randrange(0, screen_length)
            instance_score += 1
            score += 1
        self.rect.x -= self.x_speed + instance_score * 0.05 #speed * score enables for the enemies to speed up when you get more points, making for EXCITING gameplay
    
    def reset_pos(self):
        self.rect.x = screen_width + 64
        self.rect.y = random.randrange(0, screen_length)

class Player(pygame.sprite.Sprite): #Player class, filled with all the good stuff
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(os.path.join("assets", "player.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (64, 64))
        self.set_colorkey = BLACK
        self.rect = self.image.get_rect()
        self.y_speed = 0
    
    def update(self):
        self.y_speed = 0
        keystate = pygame.key.get_pressed() #This way of handling input I found to be really neat, but not 100% sure how it works
        if keystate[pygame.K_w]:
            self.y_speed = -10
        if keystate[pygame.K_s]:
            self.y_speed = 10
        self.rect.y += self.y_speed
        if self.rect.y < 0 - 64: #Come out from the opposite end if you leave the screen!
            self.rect.y = screen_length
        if self.rect.y > screen_length:
            self.rect.y = 0 - 64

player = Player() #Sprite groups, fancy!
all_sprites = pygame.sprite.Group()
collide_list = pygame.sprite.Group()
enemy_list = pygame.sprite.Group()
all_sprites.add(player)

for i in range(8): #There are just 8 projectiles, they're just recycled constantly
    enemy = Projectile()
    enemy.rect.x = random.randrange(screen_width, screen_width + 100)
    enemy.rect.y = random.randrange(0, screen_length)
    enemy_list.add(enemy) #Add them to the spritegroups for ezpz collision detection
    all_sprites.add(enemy)

def menu():
    intro = True
    while intro:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                elif event.key == pygame.K_SPACE:
                    intro = False
                    main_game()
                elif event.key == pygame.K_c:
                    intro = False
                    store()
            elif event.type == pygame.QUIT:
                pygame.quit()
        screen.fill(BLUE)
        menu_text = font.render("Total points: " + str(score), True, BLACK)
        screen.blit(menu_png, [0, 0])
        screen.blit(menu_text, [0, 0])

        pygame.display.flip()
        clock.tick(1)
            
def store():
    shop = True
    global score
    upgrade1 = button(RED, 20, 75, 180, 180, "Health Upgrade")
    global items
    while shop:
        for event in pygame.event.get():
            pos = pygame.mouse.get_pos()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                elif event.key == pygame.K_SPACE:
                    shop = False
                    main_game()
                elif event.key == pygame.K_c:
                    shop = False
                    menu()
            elif event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEMOTION and score <= 100:
                if upgrade1.isOver(pos):
                    upgrade1.color = (200, 0, 0)
                else:
                    upgrade1.color = RED
            if event.type == pygame.MOUSEMOTION and score >= 100:
                if upgrade1.isOver(pos):
                    upgrade1.color = (0, 200, 0)
                else:
                    upgrade1.color = GREEN
            if event.type == pygame.MOUSEBUTTONDOWN:
                if upgrade1.isOver(pos) and score >= 100:
                    items.append(3)
                    score -= 100
                    upgrade1.purchased = True
        screen.fill(BLUE)
        
        menu_text = font.render("Total points: " + str(score), True, BLACK)
        menu_text2 = font.render("Spend your points for permanent upgrades!", True, BLACK)
        upgrade1_price = font.render("100 Points", True, BLACK)
        bottom_text = font.render("C to retun to menu", True, BLACK)


        screen.blit(menu_text, (0, 0))
        screen.blit(menu_text2, (0, 30))
        screen.blit(bottom_text, (50, screen_length - 50))

        if upgrade1.purchased == False:
            upgrade1.draw(screen)
            screen.blit(upgrade1_price, (upgrade1.x, upgrade1.y + upgrade1.height + 5))
  

        pygame.display.flip()
        clock.tick(60)

def main_game():
    running = True
    health = 5 + sum(items)
    global instance_score
    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
            elif event.type == pygame.QUIT:
                pygame.quit()

        collision_list = pygame.sprite.spritecollide(player, enemy_list, False) #Checks for collisions

        for enemy in collision_list:
            health -= 1
            enemy.reset_pos() #If projectile hits player, put them to the right side of the screen

        if health <= 0: #Out of health? No more game for you. Unless you launch it again
            instance_score = 0
            running = False
            menu()

        screen.fill(BLUE)
        all_sprites.update() #Updates all the positions

        all_sprites.draw(screen) #Draws all the sprites
        score_text = font.render("Points: " + str(instance_score), True, BLACK) #All the text on the screen
        health_text = font.render("Health: " + str(health), True, BLACK)
        screen.blit(score_text, [0, 0])
        screen.blit(health_text, [0, 25])

        pygame.display.flip() 
        clock.tick(60) #FPS

menu()
