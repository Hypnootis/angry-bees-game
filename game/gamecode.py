import pygame #Some cool imports
import sys
import os
import random

"""
Hey, and thanks for checking out my first finished pygame project!
I learned a lot while making it, and it is in no means a polished game, just a learning experience/excercise
Pretty much everything is done by me with minimal amount of copy-pasting code, which probably shows

I have commented the code to explain why I did some things and I do know that the code has bad practises
and things that could've been done easier, but hindsight is 20/20 and honestly I just wanted
to push this project as "finished" so I can go work on something new with a better conscience!

I will most likely leave this game as is and won't come back to fix any bugs, I'm kind of scared to touch this pile of
noodles in all honesty.

Oh, and if you are actually reading this, you can press Z on the main menu for a bunch of free points, not that the upgrades are worth buying
"""



if getattr(sys, 'frozen', False): # PyInstaller adds this attribute
    # Running in a bundle
    CurrentPath = sys._MEIPASS
else:
    # Running in normal Python environment
    CurrentPath = ""                    #Copypasted from stackoverflow, not sure how it works or what it does, but it's there
pygame.init()
RED = [255, 0, 0] #I defined a bunch of colors here, later learned about the pygame.Color module, so go use that instead in your own projects! I couldn't be bothered to use it as this works as well ¯\_( ͡° ͜ʖ ͡°)_/¯
BLUE = [0, 0, 255]
GREEN = [0, 255, 0] #Constants in caps, (probably) a messy pile of variables in lowercase
BLACK = [0, 0, 0]
WHITE = [255, 255, 255]
clock = pygame.time.Clock()
screen_width = 800 #Fixed resolution of 800x600, it's a simple and small resolution
screen_length = 600
score = 0 #This keeps track of all the points gathered in total
instance_score = 0 #This keeps track of all the points gathered in a single session, that then gets added to the total score
items = []
buttons = []
pos = pygame.mouse.get_pos()
debug_mode = False

screen = pygame.display.set_mode((screen_width, screen_length)) #Setting the game window
pygame.display.set_caption("You've angered some bees and you are allergic!") #Title for the game window

clock = pygame.time.Clock()
menu_png = pygame.image.load(os.path.join("assets", "menu_pic.png")).convert_alpha() #Loading in the backgrounds for the store and menu so they are ready to be used if needed
store_png = pygame.image.load(os.path.join("assets", "store_background.png")).convert_alpha()

def draw_text(surf, text, size, x, y, color=""): #Surf is the surface you want to draw the text onto, then some basic parameters like what kind of text you want to draw
    font = pygame.font.Font(os.path.join("assets", "coolfont.ttf"), size) #The font I got off of some website
    if color == "":
        color = BLACK #If no color is specified, use black
    else:
        color = color
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.x = x
    surf.blit(text_surface, (x, y))

class Background(pygame.sprite.Sprite): #I am 99% sure here that I wouldn't have needed to use a class here, but there are multiple backgrounds so why not?
    def __init__(self, surf):
        super().__init__()
        self.surf = surf      
        self.image = pygame.image.load(os.path.join("assets", "background_pic.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (800, 600))
        self.rect = self.image.get_rect()
    
    def update(self):
        self.surf.blit(self.image, [0, 0])
    
class Button(pygame.sprite.Sprite): #My handmade button class
    def __init__(self, upgrade, price,  x, y, text = "", picture = ""): #Kinda self explanatory, though I can't remember how it works exactly and if there are any redundant attributes, always comment your code kids!
        super().__init__()
        self.x = x
        self.y = y
        self.text = text
        self.picture = picture
        self.image = pygame.image.load(os.path.join("assets", self.picture)).convert_alpha()
        self.image = pygame.transform.scale(self.image, (256, 128))
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
        self.purchased = False
        self.price = price
        self.upgrade = upgrade

class Projectile(pygame.sprite.Sprite): #Things that get shot at you, aka bees
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(os.path.join("assets", "projectile.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (32, 32)) #I use transform.Scale to change the size of the sprite, otherwise it would be 256x256 which is too big
        self.set_colorkey = WHITE
        self.rect = self.image.get_rect()
        self.x_speed = -7 #How fast the bees move
        
    def update(self): #Handles movement and stuff
        global score
        global instance_score
        if self.rect.x < 0: #If they go off the screen, put them back so it seems like more projectiles are spawning
            self.rect.x = screen_width + 64
            self.rect.y = random.randrange(0, screen_length)
            instance_score += 1
            score += 1 
            self.x_speed -= 0.2 + random.uniform(0.05, 0.2) #I make them go faster everytime they go offscreen, and also add a small random value to give them a bit of variation
        self.rect.y += random.randrange(-10, 10) #To make them look like they are buzzing I made them "vibrate" by adding random values to their y-movement
        self.rect.x += self.x_speed
    
    def reset_pos(self):
        self.rect.x = screen_width + 64
        self.rect.y = random.randrange(0, screen_length)

class Player(pygame.sprite.Sprite): #Player class, filled with all the good stuff
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(os.path.join("assets", "player_picture.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (96, 96))
        self.set_colorkey = BLACK
        self.rect = self.image.get_rect()
        self.y_speed = 0
    
    def update(self):
        self.y_speed = 0
        keystate = pygame.key.get_pressed() #This way of handling input I found to be really neat
        if keystate[pygame.K_w]:
            self.y_speed = -10
        if keystate[pygame.K_s]:
            self.y_speed = 10
        self.rect.y += self.y_speed
        if self.rect.y < 0 - 64: #Come out from the opposite end if you leave the screen!
            self.rect.y = screen_length
        if self.rect.y > screen_length:
            self.rect.y = 0 - 64

all_sprites = pygame.sprite.Group() #A handy feature of the pygame library, sprite groups!
collide_list = pygame.sprite.Group()
enemy_list = pygame.sprite.Group()
clickables = pygame.sprite.Group()

upgrade1 = Button(3, 100, 200, 400, "100 Points", "100points_new.png")
clickables.add(upgrade1)
upgrade2 = Button(5, 1000, 600, 400, "1000 Points", "1kpoints_new.png")
clickables.add(upgrade2) #Defines the buttons in the store

def menu():
    intro = True
    pygame.mixer.music.load("song.mp3") #Plays the annoying copyright free song at the start of the game
    pygame.mixer.music.play(0) #0 means that it will play for forever
    global score
    global debug_mode
    while intro:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN: #Here by pressing keys you can change the state you're in
                if event.key == pygame.K_ESCAPE: #Notice I am using the bad practice of having multiple while loops instead of a state class handling changing states
                    pygame.quit()
                elif event.key == pygame.K_SPACE:
                    intro = False
                    main_game()
                elif event.key == pygame.K_c:
                    intro = False
                    store()
                elif event.key == pygame.K_z:
                    debug_mode = True
                    score += 999999
            elif event.type == pygame.QUIT:
                pygame.quit()
        screen.fill(BLUE)
        screen.blit(menu_png, [0, 0])
        draw_text(screen, "Points: " + str(score), 18, 0, 0)
        if debug_mode == True:
            draw_text(screen, "MONEY CHEAT ACTIVATED", 18, 0, 550)

        pygame.display.flip()
        clock.tick(1)
            
def store():
    shop = True
    global score
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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button in clickables:
                    if button.rect.collidepoint(pos) and button.purchased == False and score >= button.price: #Using a for-loop to check if an upgrade can be purchased
                        score -= button.price #Removes the cost of the upgrade from the total point-total
                        items.append(button.upgrade) #Adds the upgrade to the items list
                        button.kill()
            elif event.type == pygame.MOUSEMOTION:
                for button in clickables:
                    if score < button.price and button.rect.collidepoint(pos): #Here I check if you have enough points, if not, it will display the not-enough-points image
                        button.image = pygame.image.load(os.path.join("assets", "no_points.png")).convert_alpha()
                        button.image = pygame.transform.scale(button.image, (256, 128))
                    else:
                        button.image = button.image = pygame.image.load(os.path.join("assets", button.picture)).convert_alpha() #Here is an example of why you should use classes, in the form of button.picture
                        button.image = pygame.transform.scale(button.image, (256, 128)) #No hardcoding pictures for multiple buttons, but all buttons support this function with just around 4 lines of code!
            elif event.type == pygame.QUIT:
                pygame.quit()

        screen.fill(BLUE)
        
        screen.blit(store_png, [0, 0])
        clickables.draw(screen)
        draw_text(screen, "Points: " + str(score), 18, 0, 0)

        pygame.display.flip()
        clock.tick(60)

def main_game():
    running = True
    health = 5 + sum(items) #This should realistically be in the player class, but player health amounts to starting health and health given by items
    bg = Background(screen)
    all_sprites.add(bg)
    player = Player()
    all_sprites.add(player)
    global instance_score

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
            all_sprites.empty() #I found a bug where the projectiles and player were still technically alive even after dying and going to the menu, so I kill them all and then go to the menu
            menu()

        screen.fill(BLUE)
        all_sprites.update() #Updates all the positions

        all_sprites.draw(screen) #Draws all the sprites
        draw_text(screen, "Points: " + str(instance_score), 18, 0, 0) #Using my handy text-drawing function
        draw_text(screen, "Health: " + str(health), 18, 0, 24)
        draw_text(screen, "FPS: " + str(round(clock.get_fps(), 1)), 18, 670, 572, RED)

        pygame.display.flip() 
        clock.tick(60) #FPS

menu()
pygame.QUIT()
