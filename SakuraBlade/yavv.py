import pygame, sys, os, random

from pygame.locals import *
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.set_num_channels(64)

#window_icon = pygame.image.load('staraightpython/images/gladoicon.png')# window icon image load
#pygame.display.set_icon(window_icon) # window icon
pygame.display.set_caption('Last Purpose') #WINDOW NAME
screen = pygame.display.set_mode((1920,1080),0,32) #defining screen
display = pygame.Surface((960, 540)) # scaling and defining display
#clock = pygame.time.Clock() #defining clock

pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]

detail1_block = pygame.image.load('images/grass_detail1.png').convert()
detail2_block = pygame.image.load('images/grass_detail2.png').convert()
detail3_block = pygame.image.load('images/grass_detail3.png').convert()
plant_detail = pygame.image.load('images/plant_detail.png').convert()
plant_detail.set_colorkey((255,255,255))
grass_block = pygame.image.load('images/grass.png').convert() # grass image load
dirt_block = pygame.image.load('images/dirt.png').convert() # dirt image load
        #bg = pygame.transform.scale(pygame.image.load('staraightpython\images/background.png').convert(), (640,360))
tile_index = {1:grass_block,
              2:dirt_block,
              3:plant_detail,
              4:detail1_block,
              5:detail2_block,
              6:detail3_block,
              }


jump_sound = pygame.mixer.Sound('sounds/jump45.wav')
jump_sound.set_volume(0.15)
grass_sound = [pygame.mixer.Sound('sounds/grass_0.wav'), pygame.mixer.Sound('sounds/grass_1.wav')]
grass_sound[0].set_volume(0.15)
grass_sound[1].set_volume(0.15)
grass_sound_timer = 0

pygame.mixer.music.load('music/main_music.wav')
pygame.mixer.music.set_volume(0.10)
pygame.mixer.music.play(-1)

true_scroll = [0,0]


CHUNK_SIZE = 8

def generate_chunk(x,y):
    chunk_data = []
    for y_pos in range(CHUNK_SIZE):
        for x_pos in range(CHUNK_SIZE):
            target_x = x * CHUNK_SIZE + x_pos
            target_y = y * CHUNK_SIZE + y_pos
            tile_type = 0
            if target_y > 10:
                tile_type = 2 # dirt block
                
            elif target_y == 10:
                tile_type = 1 # grass block
                    
            #elif target_y == 10:
                #if random.randint(4,10) == 4:
                    #tile_type = 4 # grass detail 4 ( named grass_detail1 at folder)
                    
            elif target_y == 9:
                if random.randint(1,3) == 1:
                    tile_type = 3 # plant details
            
            elif target_y == 9:
                if tile_type == 3:
                    target_y == 10
                
                    
            if tile_type != 0:
                chunk_data.append([[target_x, target_y], tile_type])
    return chunk_data

#{'1;1':chunk_data,'1:2':chunk_data}

global animation_frames
animation_frames = {}
def load_animation(path,frame_durations):
    global animation_frames
    animation_name = path.split('/')[-1]
    animation_frame_data = []
    n = 1
    for frame in frame_durations:
        animation_frame_id = animation_name + '_' + str(n)
        img_loc = path + '/' + animation_frame_id + '.png'
        animation_image = pygame.image.load(img_loc).convert()
        animation_image.set_colorkey((0,0,0))
        animation_frames[animation_frame_id] = animation_image.copy()
        for i in range(frame):
            animation_frame_data.append(animation_frame_id)
        n += 1
    return animation_frame_data

def change_action(action_var,frame,new_value):
    if action_var != new_value:
        action_var = new_value
        frame = 0
    return action_var,frame

animation_database = {}

animation_database['run'] = load_animation('animations/run',[6,6,6,7])
animation_database['idle'] = load_animation('animations/idle',[7,7,7,7,7,9])

player_action = 'idle'
player_frame = 0
player_flip = False

game_map = {}

TILE_SIZE = grass_block.get_width()

def collision_test(rect, tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list

def move(rect, movement, tiles): 
    collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False,}
    rect.x += movement[0]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[0] > 0:
            rect.right = tile.left
            collision_types['right'] = True
        elif movement[0] < 0:
            rect.left = tile.right
            collision_types['left'] = True
    rect.y += movement[1]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types['bottom'] = True
        elif movement[1] < 0:
            rect.top = tile.bottom
            collision_types['top'] = True
    return rect, collision_types

player_rect = pygame.Rect(168, 50, 18, 19)

movingright = False #moving right for player
movingleft = False #moving left for player

player_y_momentum = 0
air_timer = 0

class FPS:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Verdana", 10)
        self.text = self.font.render(str(self.clock.get_fps()), True, (0,0,0))

    def render(self, display):
        self.text = self.font.render(str(round(self.clock.get_fps(),2)), True, (0,0,0))
        display.blit(self.text, (140, 78))

fps = FPS()

running = True
while running: #loop start
    
    display.fill((170,130,120)) #filling screen with a color
    
    true_scroll[0] += (player_rect.x-true_scroll[0]-489)/20
    true_scroll[1] += (player_rect.y-true_scroll[1]-279)/20
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
    
    
    player_movement = [0, 0]
    if movingright:
        player_movement[0] += 3
    if movingleft:
        player_movement[0] -= 2.5
    player_movement[1] += player_y_momentum
    player_y_momentum += 0.257
    if player_y_momentum > 3.80:
        player_y_momentum = 7
        
    if player_movement[0] == 0:
        player_action,player_frame = change_action(player_action,player_frame,'idle')
    if player_movement[0] > 0:
        player_flip = False
        player_action,player_frame = change_action(player_action,player_frame,'run')
    if player_movement[0] < 0:
        player_flip = True
        player_action,player_frame = change_action(player_action,player_frame,'run')
        
    player_rect, collisions = move(player_rect, player_movement, tile_solid)
    
    if collisions['bottom']:
        player_y_momentum = 0
        air_timer = 0
        if player_movement[0] != 0:
            if grass_sound_timer == 0:
                grass_sound_timer = 22
                random.choice(grass_sound).play()
        #pygame.mixer.music.unpause()
        
    else:
        air_timer += 1   
        if collisions['top']:
            player_y_momentum += 3
            #pygame.mixer.music.pause()
    
    player_frame += 1
    if player_frame >= len(animation_database[player_action]):
        player_frame = 0
    player_img_id = animation_database[player_action][player_frame]
    player_img = animation_frames[player_img_id]
    display.blit(pygame.transform.flip(player_img,player_flip,False),(player_rect.x-scroll[0],player_rect.y-scroll[1]))
    
    for event in pygame.event.get(): #closing loop when pressed X button
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if event.type == KEYDOWN:
            if event.key == K_7:
                pygame.mixer.music.fadeout(1000)
            if event.key == K_d:
                movingright = True
            if event.key == K_a :
                movingleft = True
            if event.key == K_s:
                if air_timer > 1:
                    player_y_momentum = +5
            if event.key == K_SPACE:
                if air_timer < 8:
                    jump_sound.play()
                    player_y_momentum = -4.80
            if event.key == K_RCTRL:
                running = False
                
        if event.type == KEYUP:
            if event.key == K_d:
                movingright = False
            if event.key == K_a:
                movingleft = False
    
    fps.render(display)
    
    surf = (pygame.transform.scale(display,(1920,1080)))
    screen.blit(surf, (0,0))
    pygame.display.flip()
    fps.clock.tick(60)
pygame.quit()
