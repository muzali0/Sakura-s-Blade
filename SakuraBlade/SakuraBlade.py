import pygame, sys, random, os
import perlin_noise
import data.engine as e

from pygame.locals import *
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.set_num_channels(64)

window_icon = pygame.image.load('data\images\gladoicon.png')# window icon image load
pygame.display.set_icon(window_icon) # window icon
pygame.display.set_caption('Last Purpose') #WINDOW NAME
screen = pygame.display.set_mode((1920,1080),0,32) #defining screen
display = pygame.Surface((960, 540)) # scaling and defining display
#clock = pygame.time.Clock() #defining clock

pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]

detail1_block = pygame.image.load('data/images/grass_detail1.png').convert()
detail2_block = pygame.image.load('data/images/grass_detail2.png').convert()
detail3_block = pygame.image.load('data/images/grass_detail3.png').convert()
plant_detail = pygame.image.load('data/images/plant_detail.png').convert()
plant_detail.set_colorkey((255,255,255))
grass_block = pygame.image.load('data/images/grass.png').convert() # grass image load
dirt_block = pygame.image.load('data/images/dirt.png').convert() # dirt image load
        #bg = pygame.transform.scale(pygame.image.load('staraightpython\images/background.png').convert(), (640,360))
tile_index = {1:grass_block,
              2:dirt_block,
              3:plant_detail,
              4:detail1_block,
              5:detail2_block,
              6:detail3_block,
              }


jump_sound = pygame.mixer.Sound('data/audio/jump45.wav')
jump_sound.set_volume(0.15)
grass_sound = [pygame.mixer.Sound('data/audio/grass_0.wav'), pygame.mixer.Sound('data/audio/grass_1.wav')]
grass_sound[0].set_volume(0.15)
grass_sound[1].set_volume(0.15)
grass_sound_timer = 0

pygame.mixer.music.load('data/audio/main_music.wav')
pygame.mixer.music.set_volume(0.10)
pygame.mixer.music.play(-1)

true_scroll = [0,0]

#---------------------------CHUNK CREATION---------------------------------------
CHUNK_SIZE = 8

def generate_chunk(x, y):
    chunk_data = []
    for y_pos in range(CHUNK_SIZE):
        for x_pos in range(CHUNK_SIZE):
            target_x = x * CHUNK_SIZE + x_pos
            target_y = y * CHUNK_SIZE + y_pos
            tile_type = 0
            if target_y > 10:
                tile_type = 2  # Dirt block
                
            elif target_y == 10:
                tile_type = 1  # Grass block
                  
            elif target_y == 9:
                if random.randint(1, 3) == 1:
                    tile_type = 3  # Plant details
                          
            if tile_type != 0:
                chunk_data.append([[target_x, target_y], tile_type])
    return chunk_data

#{'1;1':chunk_data,'1:2':chunk_data}

e.load_animations('data\images\entities/')


game_map = {}

TILE_SIZE = grass_block.get_width()

player = e.entity(168, 50, 18, 19,'player')

movingright = False #moving right for player
movingleft = False #moving left for player

player_y_momentum = 0
air_timer = 0
jump_counter = 0
dash_counter = 0

#--------------------------FPS COUNTER---------------------------
class FPS:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Verdana", 10)
        self.text = self.font.render(str(self.clock.get_fps()), True, (0,0,0))

    def render(self, display):
        self.text = self.font.render(str(round(self.clock.get_fps(),2)), True, (0,0,0))
        display.blit(self.text, (200, 200))
        
deneme = pygame.Rect(470,200,25,150)
player_rect = e.entity(168, 50, 18, 19, 'player')

GameFPS = FPS()
font = pygame.font.SysFont("Verdana", 12, bold=True)

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

click = False

def main_menu():
    global click
    while True:
        
        screen.fill((0,0,0))
        draw_text("Menu", font, (255,255,255), screen, 200, 200)
        
        mx, my = pygame.mouse.get_pos()
        
        button_1 = pygame.Rect(200, 200, 200, 50)
        button_2 = pygame.Rect(200, 300, 200, 50)
        if button_1.collidepoint((mx, my)):
            if click:
                game()
        if button_2.collidepoint((mx, my)):
            if click:
                options()
        pygame.draw.rect(screen, (255,0,0), button_1)
        pygame.draw.rect(screen, (255,0,0), button_2)
        
        click = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == BUTTON_LEFT:
                    click = True
                    
        GameFPS.render(display)
        pygame.display.flip()
        GameFPS.clock.tick(60)

#------------------------------MAIN LOOP---------------------------

def game():
    running = True
    while running: #loop start
        global grass_sound_timer
        global movingleft
        global movingright
        global player_y_momentum
        global dash_counter
        global jump_counter
        
        display.fill((170,130,120)) #filling screen with a color
        #draw_text("Sakura's Blade", font, (255,255,255), display, 440, 80)
        
        true_scroll[0] += (player.x-true_scroll[0]-489)/20
        true_scroll[1] += (player.y-true_scroll[1]-279)/20
        #true_scroll[0] = max(0, true_scroll[0])
        scroll = true_scroll.copy()
        scroll[0] = int(scroll[0])
        scroll[1] = int(scroll[1])

        if grass_sound_timer > 0:
            grass_sound_timer -= 1
        
        tile_solid = []
        for y in range(5):
            for x in range(8):
                target_x = x - 1 + int(round(scroll[0]/(CHUNK_SIZE*16)))
                target_y = y - 1 + int(round(scroll[1]/(CHUNK_SIZE*16)))
                target_chunk = str(target_x) + ';' + str(target_y)
                if target_chunk not in game_map:
                    game_map[target_chunk] = generate_chunk(target_x,target_y)
                for tile in game_map[target_chunk]:
                    display.blit(tile_index[tile[1]],(tile[0][0]*16-scroll[0],tile[0][1]*16-scroll[1]))
                    if tile[1] in [1,2]:
                        tile_solid.append(pygame.Rect(tile[0][0]*16,tile[0][1]*16,16,16))
        
        #---------------------------PLAYER MOVEMENT--------------------------------
        player_movement = [0, 0]
        if movingright:
            player_movement[0] += 3
        if movingleft:
            player_movement[0] -= 3
        player_movement[1] += player_y_momentum
        player_y_momentum += 0.257
        if player_y_momentum > 3.80:
            player_y_momentum = 7
            
        if player_movement[0] == 0:
            player.set_action('idle')
        if player_movement[0] > 0:
            player.set_flip(False)
            player.set_action('run')
        if player_movement[0] < 0:
            player.set_flip(True)
            player.set_action('run')
        
        #-----------------------------PLAYER COLLISION--------------------------    
        collision_types = player.move(player_movement, tile_solid)
        
        if collision_types['bottom']:
            player_y_momentum = 0
            jump_counter = 2
            dash_counter = 1
            if player_movement[0] != 0:
                if grass_sound_timer == 0:
                    grass_sound_timer = 22
                    random.choice(grass_sound).play()
            #pygame.mixer.music.unpause()
            
        else:   
            if collision_types['top']:
                player_y_momentum += 3
                #pygame.mixer.music.pause()
        
        player.change_frame(1)
        player.display(display,scroll)
        
        for event in pygame.event.get(): #closing loop when pressed X button
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
    #----------------------------------KEYBOARD INPUTS---------------------------
            if event.type == KEYDOWN:
                if event.key == K_7:
                    pygame.mixer.music.fadeout(1000)
                if event.key == K_d:
                    movingright = True
                if event.key == K_a :
                    movingleft = True
                if event.key == K_s:
                        player_y_momentum = +5
                if event.key == K_SPACE:
                    if jump_counter > 0:
                        jump_counter -= 1
                        player_y_momentum = -4.80
                        jump_sound.play()
                if event.key == K_LSHIFT:
                    if dash_counter > 0:
                        dash_counter -= 1
                        
                           
                if event.key == K_RCTRL:
                    running = False
                if event.key == K_ESCAPE:
                    main_menu()
                    
            if event.type == KEYUP:
                if event.key == K_d:
                    movingright = False
                if event.key == K_a:
                    movingleft = False
        
        GameFPS.render(display)
        
        surf = (pygame.transform.scale(display,(1920,1080)))
        screen.blit(surf, (0,0))
        pygame.display.flip()
        GameFPS.clock.tick(60)
    pygame.quit()
    
def options():
    running = True
    while running: #loop start
    
        screen.fill((180,150,120)) #filling screen with a color
        draw_text('Options', font, (0, 0, 255), screen, 200, 200)
        
        for event in pygame.event.get(): #closing loop when pressed X button
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    main_menu()
        GameFPS.render(display)
        pygame.display.flip()
        GameFPS.clock.tick(60)
    pygame.quit()

main_menu()
