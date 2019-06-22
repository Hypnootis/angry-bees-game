import pygame #Some cool imports
import sys
import os
import random

"""
Todo:
    -Finish shop
        -Rest of the upgrades
    -Make better graphics
        -Draw them nice and shiny
    -Getting hit changes sprite?
    -Highest instance_score shown in menu? Make a list then replace it as it's broken?
    -Polish menus
    -Comment code
    -Polish the readme.txt
    -Tidy up code
    -Tidy up GitHub page
    -Launch on Itch.io
    
    In that order probably...
"""
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
buttons = []
pos = pygame.mouse.get_pos()
funky_mode = False

screen = pygame.display.set_mode((screen_width, screen_length)) #Setting the game window
pygame.display.set_caption("Dodging game 3000")

clock = pygame.time.Clock()
menu_png = pygame.image.load(os.path.join("assets", "menu_screen.png")).convert_alpha()

def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(os.path.join("assets", "coolfont.ttf"), size)
    text_surface = font.render(text, True, BLACK)
    text_rect = text_surface.get_rect()
    text_rect.x = x
    surf.blit(text_surface, (x, y))

class Background(pygame.sprite.Sprite):
    def __init__(self, surf):
        super().__init__()
        self.surf = surf
        if funky_mode == True:
            self.image = pygame.image.load(os.path.join("assets", "bg2.jpg")).convert_alpha()
        else:
            self.image = pygame.image.load(os.path.join("assets", "icon.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (800, 600))
        self.rect = self.image.get_rect()
    
    def update(self):
        self.surf.blit(self.image, [0, 0])
    
class Button(pygame.sprite.Sprite):
    def __init__(self, upgrade, price,  x, y, text = "", picture = ""):
        super().__init__()
        self.x = x
        self.y = y
        self.text = text
        self.picture = picture
        self.image = pygame.image.load(os.path.join("assets", self.picture)).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
        self.purchased = False
        self.price = price
        self._layer = self.rect.bottom
        self.upgrade = upgrade

class Projectile(pygame.sprite.Sprite): #Things that get shot at you
    def __init__(self):
        super().__init__()
        if funky_mode == True:
            self.image = self.image = pygame.image.load(os.path.join("assets", "enemy.gif")).convert_alpha()
        else:
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
        global funky_mode
        if funky_mode == True:
            self.image = pygame.image.load(os.path.join("assets", "dankey.jpg")).convert_alpha()
        else:
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

all_sprites = pygame.sprite.Group()
collide_list = pygame.sprite.Group()
enemy_list = pygame.sprite.Group()
clickables = pygame.sprite.Group()

upgrade1 = Button(3, 100, 200, 200, "100 Points", "100points.jpg")
clickables.add(upgrade1)
upgrade2 = Button(5, 1000, 500, 200, "1000 Points", "1kpoints.jpg")
clickables.add(upgrade2)
upgrade3 = Button(0, 500, 200, 400, "500 Points", "500points.jpg")
clickables.add(upgrade3)
upgrade4 = Button(0, 9999, 500, 400, "9999 Points", "10kpoints.jpg")
clickables.add(upgrade4)

def menu():
    intro = True
    global score
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
                elif event.key == pygame.K_z:
                    draw_text(screen, "DEBUG MODE ENABLED", 18, 0, 500)
                    score += 999999
            elif event.type == pygame.QUIT:
                pygame.quit()
        screen.fill(BLUE)
        screen.blit(menu_png, [0, 0])
        draw_text(screen, "Points: " + str(score), 18, 0, 0)

        pygame.display.flip()
        clock.tick(1)
            
def store():
    shop = True
    global score
    global items
    global funky_mode
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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button in clickables:
                    if button.rect.collidepoint(pos) and button.purchased == False and score >= button.price:
                        score -= button.price
                        items.append(button.upgrade)
                        button.kill()
                        if button.price == 9999:
                            funky_mode = True
            elif event.type == pygame.MOUSEMOTION:
                for button in clickables:
                    if score < button.price and button.rect.collidepoint(pos):
                        button.image = button.image = pygame.image.load(os.path.join("assets", "button1.jpg")).convert_alpha()
                    else:
                        button.image = button.image = pygame.image.load(os.path.join("assets", button.picture)).convert_alpha()
            elif event.type == pygame.QUIT:
                pygame.quit()

        screen.fill(BLUE)
        
        clickables.draw(screen)
        draw_text(screen, "Points: " + str(score), 18, 0, 0)
        draw_text(screen, "Spend your points on permanent upgrades!", 18, 70, 40)

        pygame.display.flip()
        clock.tick(60)

def main_game():
    running = True
    health = 5 + sum(items)
    bg = Background(screen)
    all_sprites.add(bg)
    player = Player()
    all_sprites.add(player)
    global instance_score
    global funky_mode
    if running == True:
        for i in range(8): #There are just 8 projectiles, they're just recycled constantly
            enemy = Projectile()
            enemy.rect.x = random.randrange(screen_width, screen_width + 100)
            enemy.rect.y = random.randrange(0, screen_length)
            enemy_list.add(enemy) #Add them to the spritegroups for ezpz collision detection
            all_sprites.add(enemy)
    else:
        enemy_list.empty()
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
            player.kill()
            all_sprites.empty()
            menu()

        screen.fill(BLUE)
        all_sprites.update() #Updates all the positions

        all_sprites.draw(screen) #Draws all the sprites
        draw_text(screen, "Points: " + str(instance_score), 18, 0, 0)
        draw_text(screen, "Health: " + str(health), 18, 0, 24)

        pygame.display.flip() 
        clock.tick(60) #FPS

menu()
pygame.QUIT()
