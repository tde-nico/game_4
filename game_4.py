import pygame, random
import data.engine as e
clock = pygame.time.Clock()

from pygame.locals import *
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.set_num_channels(64)

#####------------------------------ MONITOR ------------------------------#####

pygame.display.set_caption('Caption')
# set icon

fullscreen = False
MONITOR_SIZE = (pygame.display.Info().current_w, pygame.display.Info().current_h)
SCREEN_SIZE = (736, 414)
WINDOW_SIZE = SCREEN_SIZE
screen = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)
display = pygame.Surface((368,207))
num_x_chunks, num_y_chunks = 5, 3

pygame.mouse.set_visible(False)

#####------------------------------ INITAL DATAS ------------------------------#####

font = e.Font('data/images/font.png')
true_scroll = [0,0]
CHUNK_SIZE = 8
switch = {
    'fullscreen': 0,
    'right_arrow': 0,
    'left_arrow': 0,
    'item_menu': 0
    }
menu_render = False
options_render = False
inventory_render = False
inventory_objects = {}

#####------------------------------ STANDARD EVENTS FUNCTION ------------------------------#####

def standard_events(event):
    global screen, fullscreen, WINDOW_SIZE, MONITOR_SIZE, SCREEN_SIZE
    if event.type == QUIT: # quit
        e.qt()
    if event.type == VIDEORESIZE and not fullscreen: # video resizing
        WINDOW_SIZE, screen = e.videoresize(event)
    if event.type == KEYDOWN:
        if event.key == K_DELETE: # quit
            e.qt()
        if event.key == K_F11: # fullscreen
            fullscreen = not fullscreen
            if fullscreen:
                WINDOW_SIZE, screen = e.set_fullscreen(MONITOR_SIZE)
            else:
                WINDOW_SIZE, screen = e.toggle_fullscreen(SCREEN_SIZE)


#####------------------------------ CHUNK GENERATION ------------------------------#####

def generate_chunk(x,y):
    chunk_data = []
    for y_pos in range(CHUNK_SIZE):
        for x_pos in range(CHUNK_SIZE):
            target_x = x * CHUNK_SIZE + x_pos
            target_y = y * CHUNK_SIZE + y_pos
            tile_type = 0 # nothing
            if target_y > 10:
                tile_type = 2 # dirt
            elif target_y == 10:
                tile_type = 1 # grass
            elif target_y == 9:
                if random.randint(1,5) == 1:
                    tile_type = 3 # plant
            elif target_y == 5:
                if random.randint(1,20) == 20:
                    tile_type = 4
            elif target_y == 4:
                if random.randint(1,30) == 15:
                    tile_type = 5
            if tile_type != 0:
                chunk_data.append([[target_x,target_y],tile_type])
    return chunk_data


#####------------------------------ MAP LOADING ------------------------------#####

game_map = {}
background = pygame.image.load('data/images/ground/background_0.png')
tile_index = {
    1:e.load_img('ground/grass.png'),
    2:e.load_img('ground/dirt.png'),
    3:e.load_img('ground/plant.png'),
    4:e.load_img('ground/tree.png'),
    5:e.load_img('ground/big_tree.png')
    }

#####------------------------------ SOUNDS LOADING ------------------------------#####

sounds = {
    'jump': pygame.mixer.Sound('data/audio/jump.wav'),
    'grass_0': pygame.mixer.Sound('data/audio/grass_0.wav'),
    'grass_1': pygame.mixer.Sound('data/audio/grass_1.wav')
    }

pygame.mixer.music.load('data/audio/music.wav')
pygame.mixer.music.play(-1)

grass_sound_timer = 0

#####------------------------------ GENERATION PLAYER ------------------------------#####

e.load_animations('data/images/entities/')
player = {
    'entity': e.entity(100,100,5,13,'player'),
    'speed': 2,
    'moving_right': False,
    'moving_left': False,
    'vertical_momentum': 0,
    'air_timer': 0,
    'inventory': [],
    'equipment': {}
    }
right_arm = e.load_img('entities/player/arm.png')
left_arm = e.flip(e.load_img('entities/player/arm.png'))

#####------------------------------ GENERATION ITEMS ------------------------------#####

objects = [
    e.Weapon((250, 160-16), 'objects/weapons/sword/sword.png', 'weapon sword'),
    e.Weapon((270, 160-15), 'objects/weapons/bow/bow.png', 'weapon bow'),
    e.Weapon((290, 160-15), 'objects/weapons/bow/arrow.png', 'object arrow'),
    ]

#####------------------------------ GENERATION BARS ------------------------------#####

life_bar = e.load_img('bars/life_bar.png')
mana_bar = e.load_img('bars/mana_bar.png')

#####------------------------------ CUSTOM MOUSE LOADING ------------------------------#####

mouse_img = e.load_img('mouse_arrow.png')

#####------------------------------ OPTIONS OBJECTS LOADING ------------------------------#####

options_objects = {'aspect_ratio_index': 0}

##########------------------------------------------------------------ GAME LOOP ------------------------------------------------------------##########

def game_loop():
    global grass_sound_timer, scroll, screen, WINDOW_SIZE, fullscreen, loop

#####------------------------------ FIXING LOOP ------------------------------#####

    if grass_sound_timer > 0:
        grass_sound_timer -= 1

    true_scroll[0] += (player['entity'].x-true_scroll[0]-(display.get_width()/2-8))/20
    true_scroll[1] += (player['entity'].y-true_scroll[1]-(display.get_height()-50+8))/20
    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0])
    scroll[1] = int(scroll[1])

#####------------------------------ MAP LOOP ------------------------------#####
    
    display.blit(background, (0, 0))
    
    tile_rects = []
    for y in range(num_y_chunks):
        for x in range(num_x_chunks):
            target_x = x - 1 + int(round(scroll[0]/(CHUNK_SIZE*16)))
            target_y = y - 1 + int(round(scroll[1]/(CHUNK_SIZE*16)))
            target_chunk = str(target_x) + ';' + str(target_y)
            if target_chunk not in game_map:
                game_map[target_chunk] = generate_chunk(target_x,target_y)
            for tile in game_map[target_chunk]:
                display.blit(tile_index[tile[1]],(tile[0][0]*16-scroll[0],tile[0][1]*16-scroll[1]))
                if tile[1] in [1,2]:
                    tile_rects.append(pygame.Rect(tile[0][0]*16,tile[0][1]*16,16,16))    

#####------------------------------ PLAYER LOOP ------------------------------#####

    player_movement = [0,0]
    if player['moving_right']:
        player_movement[0] += player['speed']
    if player['moving_left']:
        player_movement[0] -= player['speed']
    player_movement[1] += player['vertical_momentum']
    player['vertical_momentum'] += 0.2
    if player['vertical_momentum'] > 3:
        player['vertical_momentum'] = 3

    if player_movement[0] == 0:
        player['entity'].set_action('idle')
    if player_movement[0] > 0:
        player['entity'].set_flip(False)
        player['entity'].set_action('run')
    if player_movement[0] < 0:
        player['entity'].set_flip(True)
        player['entity'].set_action('run')

    collision_types = player['entity'].move(player_movement,tile_rects)

    if collision_types['bottom'] == True:
        player['air_timer'] = 0
        player['vertical_momentum'] = 0
        if player_movement[0] != 0:
            if grass_sound_timer == 0:
                grass_sound_timer = 30
                random.choice((sounds['grass_0'], sounds['grass_1'])).play()
    else:
        player['air_timer'] += 1
    
    
    player['entity'].change_frame(1)
    player['entity'].display(display,scroll)

    right_arm_loc = (player['entity'].x-scroll[0], player['entity'].y+9-scroll[1])
    left_arm_loc = (player['entity'].x+10-scroll[0], player['entity'].y+9-scroll[1])

    for equip in player['equipment']:
        if 'weapon' in equip:
            if 'sword' in player['equipment'][equip].tag:
                if player['entity'].flip:
                    player['equipment'][equip].equip_render(display,(left_arm_loc[0]-5-14,left_arm_loc[1]-8),rotation=0,flipped=player['entity'].flip)
                else:
                    player['equipment'][equip].equip_render(display,(left_arm_loc[0],left_arm_loc[1]-8),rotation=0,flipped=player['entity'].flip)
            elif 'bow' in player['equipment'][equip].tag:
                if player['entity'].flip:
                    player['equipment'][equip].equip_render(display,(left_arm_loc[0]-4-13,left_arm_loc[1]-9),rotation=-135,flipped=player['entity'].flip)
                else:
                    player['equipment'][equip].equip_render(display,(left_arm_loc[0]-6,left_arm_loc[1]-9),rotation=-135,flipped=player['entity'].flip)
            
    display.blit(pygame.transform.rotate(right_arm, 0), right_arm_loc)
    display.blit(pygame.transform.rotate(left_arm, 0), left_arm_loc) #rotatating



    

#####------------------------------ OBJECTS LOOP ------------------------------#####
    
    for obj in objects:
        obj.render_map(display, scroll)
        if obj.collision_test(player['entity'].obj.rect):
            player['inventory'].append(obj)
            objects[objects.index(obj)] = False
    for index, element in sorted(enumerate(objects), reverse=True):
        if not element:
            objects.pop(index)

    
    display.blit(life_bar, (5,5))
    display.blit(mana_bar, (5,20))
    
#####------------------------------ EVENTS LOOP ------------------------------#####

    for event in pygame.event.get():
        standard_events(event)
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                loop = 0
            if event.key == K_d:
                player['moving_right'] = True
            if event.key == K_a:
                player['moving_left'] = True
            if event.key == K_w:
                if player['air_timer'] < 6:
                    sounds['jump'].play()
                    player['vertical_momentum'] = -5
        if event.type == KEYUP:
            if event.key == K_d:
                player['moving_right'] = False
            if event.key == K_a:
                player['moving_left'] = False
            if event.key == K_i:
                pygame.image.save(display,'data/images/inventory/inventory_last_background.png')
                global inventory_objects
                inventory_objects['background'] = pygame.image.load('data/images/inventory/inventory_last_background.png')
                inventory_objects['objects'] = player['inventory']
                inventory_objects['session_render'] = False
                switch['item_menu'] = 150
                loop = 4

#####------------------------------ SCREEN UPDATE ------------------------------#####
                
    screen.blit(pygame.transform.scale(display,WINDOW_SIZE),(0,0))
    pygame.display.update()
    clock.tick(60)


##########------------------------------------------------------------ MENU LOOP ------------------------------------------------------------##########

def menu_loop():
    global screen, WINDOW_SIZE, fullscreen, loop, menu_render, menu_buttons
    display.fill((74,63,170))

#####------------------------------ RENDERING LOOP ------------------------------#####

    if not menu_render:
        menu_buttons = (
            e.Button((display.get_width()/2-80/2, 5+36), 'buttons/button_play.png', swap_colors=(((205,145,43),(255,210,49)),((255,204,102),(255,246,148)),((143,94,29),(234,143,23)))),
            e.Button((display.get_width()/2-80/2, (5+36)*2), 'buttons/button_options.png', swap_colors=(((205,145,43),(255,210,49)),((255,204,102),(255,246,148)),((143,94,29),(234,143,23)))),
            e.Button((display.get_width()/2-80/2, (5+36)*3), 'buttons/button_quit.png', swap_colors=(((205,145,43),(255,210,49)),((255,204,102),(255,246,148)),((143,94,29),(234,143,23))))
            )
        menu_render = True

#####------------------------------ MOUSE LOOP ------------------------------#####

    clicks, mouse = e.mouse_events(display)

#####------------------------------ BUTTONS LOOP ------------------------------#####
    
    for button in menu_buttons:
        if button.selection_swap_check(mouse) and clicks[0]:
            loop = menu_buttons.index(button)+1
        button.render(display)
        
#####------------------------------ EVENTS LOOP ------------------------------#####

    if pygame.mouse.get_focused():
        display.blit(mouse_img, (mouse.x,mouse.y))
    for event in pygame.event.get():
        standard_events(event)
    screen.blit(pygame.transform.scale(display,WINDOW_SIZE),(0,0))
    pygame.display.update()
    clock.tick(60)





    

##########------------------------------------------------------------ OPTIONS LOOP ------------------------------------------------------------##########

def options_loop():
    global display, screen, WINDOW_SIZE, MONITOR_SIZE, SCREEN_SIZE, fullscreen, loop, switch, options_render, options_objects
    display.fill((74,63,170))

#####------------------------------ RENDERING LOOP ------------------------------#####

    if not options_render:

        options_objects['button_fullscreen'] = e.Button((display.get_width()-65, 10), 'buttons/button_normal.png', swap_colors=(((205,145,43),(255,210,49)),((255,204,102),(255,246,148)),((143,94,29),(234,143,23))))
        options_objects['button_fullscreen_pressed'] = e.Button((display.get_width()-65, 14), 'buttons/button_normal_pressed.png', swap_colors=(((205,145,43),(255,210,49)),((255,204,102),(255,246,148)),((143,94,29),(234,143,23))))
        options_objects['volume_bar'] = e.load_img('bars/volume_bar.png')
        options_objects['music_volume_control'] = e.Button((display.get_width()-40,56), 'buttons/volume_control.png', swap_colors=(((205,145,43),(255,210,49)),((255,204,102),(255,246,148)),((143,94,29),(234,143,23))))
        options_objects['sfx_volume_control'] = e.Button((display.get_width()-40,86), 'buttons/volume_control.png', swap_colors=(((205,145,43),(255,210,49)),((255,204,102),(255,246,148)),((143,94,29),(234,143,23))))
        options_objects['button_back'] = e.Button((display.get_width()/2-80/2,display.get_height()-40), 'buttons/button_back.png', swap_colors=(((205,145,43),(255,210,49)),((255,204,102),(255,246,148)),((143,94,29),(234,143,23))))
        options_objects['right_arrow'] = e.Button((display.get_width()-40,116),'buttons/right_arrow.png', 'buttons/right_arrow_pressed.png', swap_colors=(((205,145,43),(255,210,49)),((255,204,102),(255,246,148)),((143,94,29),(234,143,23))))
        options_objects['left_arrow'] = e.Button((display.get_width()-130,116),'buttons/right_arrow.png', 'buttons/right_arrow_pressed.png', swap_colors=(((205,145,43),(255,210,49)),((255,204,102),(255,246,148)),((143,94,29),(234,143,23))))
        options_objects['aspect_ratio'] = ('16/9', '4/3', '5/4', '1/1', '16/10')
        options_objects['aspect_ratio_render'] = False
            
        options_objects['left_arrow'].img = e.flip(options_objects['left_arrow'].img.copy())
        options_objects['left_arrow'].pressed_img = e.flip(options_objects['left_arrow'].pressed_img.copy())
        options_objects['left_arrow'].released_img = e.flip(options_objects['left_arrow'].released_img.copy())
        options_render = True

#####------------------------------ ASPECT RATIO RENDERING LOOP ------------------------------#####

    if options_objects['aspect_ratio_render']:
        global num_x_chunks, num_y_chunks, menu_render, inventory_render, background
        if options_objects['aspect_ratio_index'] == 0:
            SCREEN_SIZE = (736, 414)
            num_x_chunks, num_y_chunks = 5, 3
        if options_objects['aspect_ratio_index'] == 1:
            SCREEN_SIZE = (600, 450)
            num_x_chunks, num_y_chunks = 4, 4
        if options_objects['aspect_ratio_index'] == 2:
            SCREEN_SIZE = (600, 480)
            num_x_chunks, num_y_chunks = 4, 4
        if options_objects['aspect_ratio_index'] == 3:
            SCREEN_SIZE = (600, 600)
            num_x_chunks, num_y_chunks = 4, 4
        if options_objects['aspect_ratio_index'] == 4:
            SCREEN_SIZE = (736, 460)
            num_x_chunks, num_y_chunks = 5, 4
        WINDOW_SIZE = SCREEN_SIZE
        display = pygame.Surface((WINDOW_SIZE[0]/2,WINDOW_SIZE[1]/2))
        if fullscreen:
            pygame.display.toggle_fullscreen()
            switch['fullscreen'] = -1
        screen = pygame.display.set_mode(WINDOW_SIZE, pygame.SCALED + pygame.RESIZABLE)
        screen = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)
        options_objects['aspect_ratio_render'] == False
        options_render = False
        menu_render = False
        inventory_render = False
        background = pygame.image.load('data/images/ground/background_' + str(options_objects['aspect_ratio_index']) + '.png')

#####------------------------------ BUTTONS LOOP ------------------------------#####
    
    clicks, mouse = e.mouse_events(display)

#####------------------------------ FULLSCREEN BUTTON LOOP ------------------------------#####

    font.render(display, 'FULLSCREEN', (20,20), 2)
    font.render(display, '(F11)', (options_objects['button_fullscreen'].rect.x-55,20), 2)
    if not fullscreen:
        button = options_objects['button_fullscreen']
    else:
        button = options_objects['button_fullscreen_pressed']
    if button.selection_swap_check(mouse) and clicks[0] and switch['fullscreen'] > 20:
        fullscreen = not fullscreen
        switch['fullscreen'] = 0
    else:
        switch['fullscreen'] += 1
    button.render(display)
    if fullscreen and switch['fullscreen'] == 0:
        WINDOW_SIZE = MONITOR_SIZE
        screen = pygame.display.set_mode(WINDOW_SIZE, pygame.SCALED + pygame.FULLSCREEN)
    elif switch['fullscreen'] == 0:
        pygame.display.toggle_fullscreen()
        WINDOW_SIZE = SCREEN_SIZE
        screen = pygame.display.set_mode(WINDOW_SIZE, pygame.SCALED + pygame.RESIZABLE)
        screen = pygame.display.set_mode(WINDOW_SIZE, pygame.SCALED + pygame.RESIZABLE)

#####------------------------------ MUSIC VOLUME BUTTON LOOP ------------------------------#####

    font.render(display, 'MUSIC VOLUME', (20,options_objects['music_volume_control'].rect.y+4), 2)
    display.blit(options_objects['volume_bar'], (display.get_width()-130,options_objects['music_volume_control'].rect.y+4))
    if options_objects['music_volume_control'].selection_swap_check(mouse) and clicks[0]:
        if mouse.x > display.get_width()-129 and mouse.x < display.get_width()-27:
            options_objects['music_volume_control'].rect.x = mouse.x-11
            pygame.mixer.music.set_volume(1-(display.get_width()-28-mouse.x)/100)
    pygame.draw.rect(display,(100,100,100),(
        options_objects['music_volume_control'].rect.x+11,
        options_objects['music_volume_control'].rect.y+6,
        display.get_width()-50-options_objects['music_volume_control'].rect.x+11,
        2))
    pygame.draw.rect(display,(50,50,50),(
        options_objects['music_volume_control'].rect.x+11,
        options_objects['music_volume_control'].rect.y+8,
        display.get_width()-50-options_objects['music_volume_control'].rect.x+11,
        8))
    options_objects['music_volume_control'].render(display)
    
#####------------------------------ SFX VOLUME BUTTON LOOP ------------------------------#####

    font.render(display, 'SFX VOLUME', (20,options_objects['sfx_volume_control'].rect.y+4), 2)
    display.blit(options_objects['volume_bar'], (display.get_width()-130,options_objects['sfx_volume_control'].rect.y+4))
    if options_objects['sfx_volume_control'].selection_swap_check(mouse) and clicks[0]:
        if mouse.x > display.get_width()-129 and mouse.x < display.get_width()-27:
            options_objects['sfx_volume_control'].rect.x = mouse.x-11
            for sound in sounds:
                if 'grass' in sound:
                    sfx_coef = .2
                else:
                    sfx_coef = 1
                sounds[sound].set_volume((1-(display.get_width()-28-mouse.x)/100)*sfx_coef)
    pygame.draw.rect(display,(100,100,100),(
        options_objects['sfx_volume_control'].rect.x+11,
        options_objects['sfx_volume_control'].rect.y+6,
        display.get_width()-50-options_objects['sfx_volume_control'].rect.x+11,
        2))
    pygame.draw.rect(display,(50,50,50),(
        options_objects['sfx_volume_control'].rect.x+11,
        options_objects['sfx_volume_control'].rect.y+8,
        display.get_width()-50-options_objects['sfx_volume_control'].rect.x+11,
        8))
    options_objects['sfx_volume_control'].render(display)

#####------------------------------ ASPECT RATIO SETTINGS LOOP ------------------------------#####

    font.render(display, 'SCREEN SIZE', (20,116), 2)
    if options_objects['right_arrow'].selection_swap_check(mouse) and clicks[0] and switch['right_arrow'] > 20:
        options_objects['aspect_ratio_index'] += 1
        if options_objects['aspect_ratio_index'] > 4:
            options_objects['aspect_ratio_index'] = 0
        options_objects['aspect_ratio_render'] = True
        options_objects['right_arrow'].img = options_objects['right_arrow'].pressed_img.copy()
        options_objects['right_arrow'].selection = False
        options_objects['right_arrow'].pressed = True
        switch['right_arrow'] = 0
    else:
        if switch['right_arrow'] > 20 and options_objects['right_arrow'].pressed:
            options_objects['right_arrow'].img = options_objects['right_arrow'].released_img.copy()
            options_objects['right_arrow'].selection = False
            options_objects['right_arrow'].pressed = False
        switch['right_arrow'] += 1
    options_objects['left_arrow'].img = e.swap_color(options_objects['left_arrow'].img, (255,255,255), (255,255,255))
    if options_objects['left_arrow'].selection_swap_check(mouse) and clicks[0] and switch['left_arrow'] > 20:
        options_objects['aspect_ratio_index'] -= 1
        if options_objects['aspect_ratio_index'] < 0:
            options_objects['aspect_ratio_index'] = 4
        options_objects['aspect_ratio_render'] = True
        options_objects['left_arrow'].img = options_objects['left_arrow'].pressed_img.copy()
        options_objects['left_arrow'].selection = False
        options_objects['left_arrow'].pressed = True
        switch['left_arrow'] = 0
    else:
        if switch['left_arrow'] > 20  and options_objects['left_arrow'].pressed:
            options_objects['left_arrow'].img = options_objects['left_arrow'].released_img.copy()
            options_objects['left_arrow'].selection = False
            options_objects['left_arrow'].pressed = False
        switch['left_arrow'] += 1
    options_objects['right_arrow'].render(display)
    options_objects['left_arrow'].render(display)
    font.render(display, options_objects['aspect_ratio'][options_objects['aspect_ratio_index']],
                (display.get_width()-78-5*len(options_objects['aspect_ratio'][options_objects['aspect_ratio_index']]),122), 2)

#####------------------------------ BACK BUTTON LOOP ------------------------------#####

    if options_objects['button_back'].selection_swap_check(mouse) and clicks[0]:
        loop = 0
    options_objects['button_back'].render(display)

#####------------------------------ EVENTS LOOP ------------------------------#####

    if pygame.mouse.get_focused():
        display.blit(mouse_img, (mouse.x,mouse.y))
    

    for event in pygame.event.get():
        standard_events(event)
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                loop = 0
    screen.blit(pygame.transform.scale(display,WINDOW_SIZE),(0,0))
    pygame.display.update()
    clock.tick(60)







##########------------------------------------------------------------ INVENTORY LOOP ------------------------------------------------------------##########

def inventory_loop():
    global screen, WINDOW_SIZE, mouse, loop, inventory_render, inventory_objects

#####------------------------------ RENDERING LOOP ------------------------------#####

    if not inventory_render:
        e.load_animations('data/images/')
        slots = {}
        for row in range(5):
            for column in range(8):
                slots[str(row)+str(column)] = [e.Button((display.get_width()-264+30*column,39+30*row), 'inventory/inventory_slot.png'), 0]
        inventory_objects['inventory'] = e.load_img('inventory/inventory.png')
        inventory_objects['slots'] = slots
        inventory_objects['selection'] = e.entity(0,0,32,32,'inventory')
        inventory_objects['equipment_section'] = e.Button((display.get_width()-125,10), 'inventory/inventory_equipment_section.png')
        inventory_objects['level_section'] = e.Button((display.get_width()-155,10), 'inventory/inventory_level_section.png')
        inventory_objects['list_section'] = e.Button((display.get_width()-187,10), 'inventory/inventory_list_section.png')
        inventory_objects['button_equip'] = e.Button((display.get_width()+10,display.get_height()+10), 'buttons/button_equip.png', swap_colors=((205,145,43),(255,210,49)))
        inventory_objects['button_info'] = e.Button((display.get_width()+10,display.get_height()+10), 'buttons/button_info.png', swap_colors=((205,145,43),(255,210,49)))
        inventory_objects['button_drop'] = e.Button((display.get_width()+10,display.get_height()+10), 'buttons/button_drop.png', swap_colors=((205,145,43),(255,210,49)))
        inventory_objects['item_menu_datas'] = [pygame.Rect((display.get_width()+10,display.get_height()+10),(23,25)), 0]
        inventory_render = True

    if not inventory_objects['session_render']:
        key_list = list(inventory_objects['slots'].keys())
        for obj_num in range(len(inventory_objects['objects'])):
            inventory_objects['slots'][key_list[obj_num]][1] = inventory_objects['objects'][obj_num]
        inventory_objects['session_render'] = True

#####------------------------------ BUTTONS LOOP ------------------------------#####

    clicks, mouse = e.mouse_events(display)




    display.blit(inventory_objects['background'], (0,0))
    display.blit(inventory_objects['inventory'], (display.get_width()-277,3))
    render_selection = False
    
    if inventory_objects['list_section'].rect.colliderect(mouse):
        if clicks[0]:
            pass                #list section
        inventory_objects['selection'].x = inventory_objects['list_section'].rect.x-3
        inventory_objects['selection'].y = inventory_objects['list_section'].rect.y-4
        render_selection = True
    inventory_objects['list_section'].render(display)
    
    if inventory_objects['level_section'].rect.colliderect(mouse):
        if clicks[0]:
            pass                #level section
        inventory_objects['selection'].x = inventory_objects['level_section'].rect.x-4
        inventory_objects['selection'].y = inventory_objects['level_section'].rect.y-4
        render_selection = True
    inventory_objects['level_section'].render(display)
    
    if inventory_objects['equipment_section'].rect.colliderect(mouse):
        if clicks[0]:
            pass                #equipment section
        inventory_objects['selection'].x = inventory_objects['equipment_section'].rect.x-3
        inventory_objects['selection'].y = inventory_objects['equipment_section'].rect.y-4
        render_selection = True
    inventory_objects['equipment_section'].render(display)
    
    for slot in inventory_objects['slots']:
        if inventory_objects['slots'][slot][0].rect.colliderect(mouse):
            inventory_objects['selection'].x = inventory_objects['slots'][slot][0].rect.x-1
            inventory_objects['selection'].y = inventory_objects['slots'][slot][0].rect.y-1
            if clicks[2] and not inventory_objects['button_equip'].rect.colliderect(mouse) and not inventory_objects['button_info'].rect.colliderect(mouse) and not inventory_objects['button_drop'].rect.colliderect(mouse):
                inventory_objects['button_equip'].rect.x = mouse.x+6
                inventory_objects['button_equip'].rect.y = mouse.y+1
                inventory_objects['button_info'].rect.x = mouse.x+6
                inventory_objects['button_info'].rect.y = mouse.y+9
                inventory_objects['button_drop'].rect.x = mouse.x+6
                inventory_objects['button_drop'].rect.y = mouse.y+17
                inventory_objects['item_menu_datas'][0].x = mouse.x+5
                inventory_objects['item_menu_datas'][0].y = mouse.y
                inventory_objects['item_menu_datas'][1] = slot
                switch['item_menu'] = 0
            render_selection = True
        inventory_objects['slots'][slot][0].render(display)
        if inventory_objects['slots'][slot][1]:
            inventory_objects['slots'][slot][1].scale_render(display,(inventory_objects['slots'][slot][0].rect.x+1,inventory_objects['slots'][slot][0].rect.y+1), scale=2)



    if render_selection:
        inventory_objects['selection'].change_frame(1)
        inventory_objects['selection'].display(display,[0,0])

    if switch['item_menu'] < 120:
        if inventory_objects['button_equip'].selection_swap_check(mouse):
            if clicks[0] and inventory_objects['slots'][inventory_objects['item_menu_datas'][1]][1]:
                if 'weapon' in inventory_objects['slots'][inventory_objects['item_menu_datas'][1]][1].tag:
                    player['equipment']['weapon'] = inventory_objects['slots'][inventory_objects['item_menu_datas'][1]][1]
                                       # item equipping
            switch['item_menu'] = 0
        if inventory_objects['button_info'].selection_swap_check(mouse):
            if clicks[0]:
                pass                   # item info
            switch['item_menu'] = 0
        if inventory_objects['button_drop'].selection_swap_check(mouse):
            if clicks[0] and inventory_objects['slots'][inventory_objects['item_menu_datas'][1]][1]:
                if player['entity'].flip:
                    inventory_objects['slots'][inventory_objects['item_menu_datas'][1]][1].rect.x = player['entity'].x - 30
                else:
                    inventory_objects['slots'][inventory_objects['item_menu_datas'][1]][1].rect.x = player['entity'].x + 30
                inventory_objects['slots'][inventory_objects['item_menu_datas'][1]][1].rect.y = player['entity'].y-2
                objects.append(inventory_objects['slots'][inventory_objects['item_menu_datas'][1]][1].copy())
                player['inventory'].remove(inventory_objects['slots'][inventory_objects['item_menu_datas'][1]][1])
                inventory_objects['slots'][inventory_objects['item_menu_datas'][1]][1] = 0
            switch['item_menu'] = 0
        pygame.draw.rect(display, (48,36,51), inventory_objects['item_menu_datas'][0])
        inventory_objects['button_equip'].render(display)
        inventory_objects['button_info'].render(display)
        inventory_objects['button_drop'].render(display)
    switch['item_menu'] += 1

#####------------------------------ EVENTS LOOP ------------------------------#####

    if pygame.mouse.get_focused():
        display.blit(mouse_img, (mouse.x,mouse.y))
    
    for event in pygame.event.get():
        standard_events(event)
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                loop = 0
        if event.type == KEYUP:
            if event.key == K_i:
                loop = 1          
    screen.blit(pygame.transform.scale(display,WINDOW_SIZE),(0,0))
    pygame.display.update()
    clock.tick(60)






##########------------------------------------------------------------ SYSTEM LOOP ------------------------------------------------------------##########


loops = (menu_loop, game_loop, options_loop, e.qt, inventory_loop)
loop = 0

while True:
    loops[loop]()





    
