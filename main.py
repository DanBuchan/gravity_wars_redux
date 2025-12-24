import pygame
import pygame_menu
from pygame_menu import themes
import random
import time
import re
import math

from config import settings, set_settings
from menu import *
from sprites import *
from ui_widgets import *
# from menu import mainmenu
from pygame.locals import (
    K_ESCAPE,
    KEYDOWN,
    QUIT,
    K_TAB,
    K_RETURN,
)

pygame.init()
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.init()
pygame.display.set_caption('Gravity Wars Redux')
clock = pygame.time.Clock()

# maybe we'll load some background music...
# pygame.mixer.music.load("sounds/Apoxode_-_Electric_1.mp3")
# pygame.mixer.music.play(loops=-1)

#blackhole_strike = pygame.mixer.Sound("./audio/blackhole_strike.mp3")
blackhole_strike = pygame.mixer.Sound("./audio/planet_strike_reverse.mp3")
missile_launch = pygame.mixer.Sound("./audio/missile_launch.mp3")
missile_travelling = pygame.mixer.Sound("./audio/missile_travelling.mp3")
missile_puttering = pygame.mixer.Sound("./audio/missile_puttering.mp3")
planet_strike = pygame.mixer.Sound("./audio/planet_strike.mp3")
ship_strike = pygame.mixer.Sound("./audio/ship_strike.mp3")

blackhole_strike.set_volume(0.6)
missile_launch.set_volume(1)
missile_travelling.set_volume(0.5)
missile_puttering.set_volume(0.5)
planet_strike.set_volume(1)
ship_strike.set_volume(1)

MISSILE_LAUNCH = pygame.USEREVENT + 1
PLANET_STRIKE = pygame.USEREVENT + 2
SHIP_STRIKE = pygame.USEREVENT + 3
BLACKHOLE_STRIKE = pygame.USEREVENT + 4
MISSILE_PUTTERING = pygame.USEREVENT + 5
MISSILE_FADE = pygame.USEREVENT + 6
NEXT_STATE = pygame.USEREVENT + 7

screen = pygame.display.set_mode([settings['DisplayWidth'],
                                  settings['DisplayHeight']])
area_to_save = pygame.Rect(0, 0, settings['DisplayWidth'], settings['DisplayHeight'])
temp_screen = pygame.Surface(area_to_save.size)
master_layout = pygame.Surface(area_to_save.size)

# Game states
# 1: generating the sprites
# 2: generating the player 1 widgets
# 3: waiting/accepting player 1 input
# 4: generating the player 2 widgets
# 5: waiting/accepting player 2 input
# 6: animating missiles player 1
# 7: animating missiles player 2
# 8: animating both missiles
# 9: end of game state - win or draw    
player1_id = None
angle_dialogue = None
player1_angle_input = None
velocity_dialogue = None
player1_velocity_input = None
submit_button = None
player2_id = None
player2_angle_input = None
player2_velocity_input = None
running = True
frame_count = 0


def show_a_message(colour, message, adjustment=0):
    font = pygame.font.SysFont('bold', 16)
    text = font.render(message, True, colour, pygame.SRCALPHA)
    text.set_alpha()
    textRect = text.get_rect()
    textRect.center = (settings['ScreenWidth']/2, settings['ScreenHeight']/2+adjustment)
    screen.blit(text, textRect)
    pygame.display.flip()

def make_a_missile(player, colour):
    missile = Missile(player, colour, MISSILE_PUTTERING,
                      BLACKHOLE_STRIKE, PLANET_STRIKE, MISSILE_FADE)
    missile.set_starting_location(player)
    missile.missile_start_time = time.time()
    screen.blit(missile.surf, (missile.x, missile.y))
    pygame.event.post(pygame.event.Event(MISSILE_LAUNCH))
    return missile
            
def run_the_game(play1, play2, planetNum, 
                 allowBlack, allowNakedBlack,
                 remove, alternate, seed, swapSides, maxMass):
    
        
    set_settings(play1, play2, planetNum, 
                 allowBlack, allowNakedBlack,
                 remove, alternate, seed, swapSides, maxMass)
    if not settings["Seed"]:
        settings["Seed"] = int(''.join(str(random.randint(0,9)) for _ in range(12)))
    #settings["Seed"] = 331357458685
    random.seed(int(settings["Seed"]))
    #712812482802
    
    # Many of theses booleans could live in settings object you know
    game_running = True
    player1_left = False
    player1 = None
    player2 = None
    players = None
    all_sprites = None
    planets = None
    collision_planets = None
    missile1_travelling = False
    missile2_travelling = False
    missile1_done = None
    missile2_done = None

    collisions1 = None
    collisions2 = None
    win_message = ''
    states = {'sprite_gen': True,
              'p1_widget_gen': False,
              'p1_input': False,
              
              'clear_ui': False,
              'p1_missiles': False,
              'p1_message': False,
              
              'p2_widget_gen': False,
              'p2_input': False,
              
              'clear_ui_2': False,
              'p2_missiles': False,
              'p2_message': False,

              'clear_ui_3': False,
              'both_missiles': False,
              'both_message': False,
              'end_game': False,

              'end_wait': False,
              }
    frames = 0
    while game_running:
        frames += 1
        # Look at every event in the queue
        events = pygame.event.get()
        for event in events:
            # Did the user hit a key?
            if event.type == KEYDOWN:
                # Was it the Escape key? If so, stop the loop.
                if event.key == K_ESCAPE:
                    blackhole_strike.stop()
                    missile_launch.stop()
                    missile_travelling.stop()
                    planet_strike.stop()
                    ship_strike.stop()
                    game_running = False
                if event.key == K_TAB:
                    # toggle between text input widgets
                    if states['p1_input']:
                        if player1_angle_input.selected:
                            player1_angle_input.selected = False
                            player1_velocity_input.selected = True
                        else:
                            player1_angle_input.selected = True
                            player1_velocity_input.selected = False
                    elif states['p2_input']:
                        if player2_angle_input.selected:
                            player2_angle_input.selected = False
                            player2_velocity_input.selected = True
                        else:
                            player2_angle_input.selected = True
                            player2_velocity_input.selected = False
                if event.key == K_RETURN:
                    if states['p1_input']:
                        if len(player1_angle_input.getText()) > 0:
                            player1.angle_text = player1_angle_input.getText()
                            player1.angle = float(player1.angle_text)
                        if len(player1_velocity_input.getText()) > 0:
                            player1.velocity_text = player1_velocity_input.getText()
                            player1.velocity = float(player1.velocity_text)
                        if player1.velocity == 0.0:
                            player1.velocity = 0.00001
                        # fire or go to p2input
                        states['p1_input'] = False
                        if settings['Alternate']:
                            states['clear_ui'] = True
                        else:
                            states['p2_widget_gen'] = True
                    elif states['p2_input']:
                        if len(player2_angle_input.getText()) > 0:
                            player2.angle_text = player2_angle_input.getText()
                            player2.angle = float(player2.angle_text)
                        if len(player2_velocity_input.getText()) > 0:
                            player2.velocity_text = player2_velocity_input.getText()
                            player2.velocity = float(player2.velocity_text)
                        if player2.velocity == 0.0:
                            player2.velocity = 0.00001
                        states['p2_input'] = False
                        if settings['Alternate']:
                            states['clear_ui_2'] = True
                        else:
                            states['clear_ui_3'] = True
                    if states['end_wait']:
                        states['end_wait'] = False
                        states['sprite_gen'] = True
                    if states['p1_message']:
                        states['p1_message'] = False
                        states['p2_widget_gen'] = True
                        screen.blit(temp_screen, (0, 0), area_to_save)
                    if states['p2_message']:
                        screen.blit(temp_screen, (0, 0), area_to_save)
                        states['p2_message'] = False
                        states['p1_widget_gen'] = True
                    if states['both_message']:
                        screen.blit(temp_screen, (0, 0), area_to_save)
                        states['both_message'] = False
                        states['p1_widget_gen'] = True
                    
            # Did the user click the window close button? If so, stop the loop.
            elif event.type == QUIT:
                blackhole_strike.stop()
                missile_launch.stop()
                missile_travelling.stop()
                planet_strike.stop()
                ship_strike.stop()
                game_running = False
            elif event.type == MISSILE_LAUNCH:
                missile_launch.play()
                missile_travelling.play(loops=-1, fade_ms=1389)
            elif event.type == PLANET_STRIKE:
                if not missile1_travelling and not missile2_travelling:
                    missile_travelling.stop()
                planet_strike.play()
                if not missile1_travelling:
                    missile1_travelling = True
                if not missile2_travelling:
                    missile2_travelling = True
            elif event.type == MISSILE_FADE:
                missile_travelling.fadeout(1000)
            elif event.type == MISSILE_PUTTERING:
                if not missile1_travelling and not missile2_travelling:
                    missile_travelling.stop()
                missile_puttering.play()
                if not missile1_travelling:
                    missile1_travelling = True
                if not missile2_travelling:
                    missile2_travelling = True
            elif event.type == BLACKHOLE_STRIKE:
                if not missile1_travelling and not missile2_travelling:
                    missile_travelling.stop()
                blackhole_strike.play()
                if not missile1_travelling:
                    missile1_travelling = True
                if not missile2_travelling:
                    missile2_travelling = True
            elif event.type == NEXT_STATE:
                if states['p1_message']:
                    states['p1_message'] = False
                    states['p2_widget_gen'] = True
                    screen.blit(temp_screen, (0, 0), area_to_save)
                if states['p2_message']:
                    screen.blit(temp_screen, (0, 0), area_to_save)
                    states['p2_message'] = False
                    states['p1_widget_gen'] = True
                if states['both_message']:
                    screen.blit(temp_screen, (0, 0), area_to_save)
                    states['both_message'] = False
                    states['p1_widget_gen'] = True
                
        # Using these ifs to handle game states. Not the best way apparently but it'll do
        if states['sprite_gen']:

            if settings['SwapSides']:
                if player1_left:
                    player1_left = False
                else:
                    player1_left = True
            else:
                player1_left = True
            blackhole_strike.stop()
            missile_launch.stop()
            missile_travelling.stop()
            planet_strike.stop()
            ship_strike.stop()
            # Instantiate players.
            print(settings)
            if player1_left:
                player1 = Player(settings, (64,64,255), True)
                player2 = Player(settings, (255,64,64), False)
            else:
                player1 = Player(settings, (64,64,255), False)
                player2 = Player(settings, (255,64,64), True)
            players = pygame.sprite.Group()
            players.add(player1)
            players.add(player2)
            planets = pygame.sprite.Group()
            collision_planets = pygame.sprite.Group()
            all_sprites = pygame.sprite.Group()
            all_sprites.add(player1)
            all_sprites.add(player2)
            screen.fill((0, 0, 0))
            # GENERATE STAR FIELD/BACKGROUND
            
            for i in range(0, 700):
                star_x = random.randint(0, settings['ScreenWidth'])
                star_y = random.randint(0, settings['ScreenWidth'])
                star_surf = pygame.Surface((1, 1))
                star_surf.fill((random.randint(200,255),200,random.randint(200,255)))
                screen.blit(star_surf, (star_x, star_y))
            planet_count = random.randint(settings['MinPlanets'],
                                          settings['MaxPlanets'])
            pygame.display.flip()
            time.sleep(1)
            accepted_count = 0
            while True:
                tmp_planet = Planet(settings)
                accept_planet = True
                for sprite in all_sprites:
                    # print(sprite, tmp_planet.rect.center[0], tmp_planet.rect.center[1], sprite.rect.center[0], sprite.rect.center[1])
                    dist = pygame.math.Vector2(tmp_planet.rect.center[0], tmp_planet.rect.center[1]).distance_to((sprite.rect.center[0], sprite.rect.center[1]))
                    spacing = player1.sprite_dim_x
                    if hasattr(sprite, 'radius'):
                        spacing = sprite.radius+5
                    if dist <= tmp_planet.radius+spacing:
                        accept_planet = False
                if accept_planet:
                    all_sprites.add(tmp_planet)

                    planets.add(tmp_planet)
                    if tmp_planet.planet_type == 7:
                        black_hole_type = random.choices((1,2),
                                          (3/4, 1/4), k=1)[0]
                        if black_hole_type == 1:
                            collision_planets.add(tmp_planet)
                    else:
                        collision_planets.add(tmp_planet)
                    
                    screen.blit(tmp_planet.image, (tmp_planet.x, tmp_planet.y))
                    pygame.display.flip()
                    time.sleep(0.3)
                    accepted_count += 1    
                if accepted_count == planet_count:
                    break
            
            screen.blit(player1.surf, (player1.x, player1.y))
            screen.blit(player1.canon, (player1.canon_x, player1.canon_y))
            screen.blit(player2.surf, (player2.x, player2.y))
            screen.blit(player2.canon, (player2.canon_x, player2.canon_y))
            
            pygame.display.flip()
            #copy the current state of screen to temp_screen
            temp_screen.blit(screen, (0, 0), area_to_save)
            master_layout.blit(screen, (0, 0), area_to_save)
            time.sleep(0.5)
            states['sprite_gen'] = False
            states['p1_widget_gen'] = True
            
        if states['p1_widget_gen']:
            missile1_done = None
            missile2_done = None
            collisions1 = None
            collisions2 = None
            if settings['RemoveTrails']:
                screen.blit(master_layout, (0, 0), area_to_save)
                      
            player1_id = create_text_area(screen, 10, 10, 65, 20, 'Player 1',(180, 180, 240), (160, 160, 220))
            angle_dialogue = create_text_area(screen, 80, 10, 85, 20, 'Angle (0-360)', (180, 180, 240), (160, 160, 220))
            player1_angle_input = create_text_input(screen, 165, 10, 65, 20, player1.angle_text, 0, 360, '000.0000', '359.9999', (180, 180, 240), (160, 160, 220))
            velocity_dialogue = create_text_area(screen, 235, 10, 90, 20, 'Velocity (0-10)', (180, 180, 240), (160, 160, 220))
            player1_velocity_input = create_text_input(screen, 325, 10, 60, 20, player1.velocity_text, 0, 10, '0.0000', '10.0000', (180, 180, 240), (160, 160, 220))
            
            submit_text = "Submit"
            next_state = 'p2_widget_gen'
            fire_colour = (120, 255, 120)
            fire_border_colour = (120, 200, 120)
            if settings["Alternate"]:
                submit_text = "Fire!"
                next_state = 'clear_ui'
                fire_colour = (255, 120, 120)
                fire_border_colour = (200, 120, 120)
            submit_button = create_submit_button(screen, 390, player1, states, player1_angle_input, player1_velocity_input, 'p1_input', next_state, submit_text, fire_colour, fire_border_colour)
            # create the widgets afresh with the current value
            #screenwidth-120-10
            seed_dialogue = create_text_area(screen, settings["ScreenWidth"]-120-10, 10, 120, 20, f"Seed: {settings['Seed']}", (220, 220, 180), (220, 220, 160))
            
            states['p1_widget_gen'] = False
            states['p1_input'] = True

        if states['p1_input']:
            pygame_widgets.update(events)
            pygame.display.update()

        if states['clear_ui']:
            screen.blit(temp_screen, (0, 0), area_to_save)
            missile1 = make_a_missile(player1,(190, 190, 255))
            states["p1_missiles"] = True
            states['clear_ui'] = False

        if states['p1_missiles']:
            missile_done = missile1.fire_missile(screen, planets, collision_planets, settings, player1)
            if missile_done:
                missile_launch.stop()
                states['p1_missiles'] = False
                states['p1_message'] = True
                temp_screen.blit(screen, (0, 0), area_to_save)
                show_a_message((200,255,200), missile1.message)
                missile1_travelling = False
                missile2_travelling = False
            collisions = pygame.sprite.spritecollide(missile1, players, 
                                                     False)
            if collisions:
                missile_travelling.stop()
                missile_launch.stop()
                ship_strike.play()
                missile1_travelling = False
                missile2_travelling = False
                states['p1_missiles'] = False
                states['end_game'] = True
                if collisions[0].name == player1.name:
                    win_message = f"{settings['Player2Name']} has won!"
                else:
                    win_message = f"{settings['Player1Name']} has won!"

            # 3. Check solarsystems bounds if left display message, then 
            # 4. Time missle, no missile gets more than 60 seconds.
            # 5. if erase trails is on blit the saved screen in to place 
            #.   before toggling
 
        if states['p1_message']:
            pass
        
        if states['p2_widget_gen']:
            player1_id.hide()
            player1_angle_input.hide()
            player1_velocity_input.hide()
            submit_button.hide()
            angle_dialogue.hide()
            velocity_dialogue.hide()
            
            player2_id = create_text_area(screen, 10, 10, 65, 20, 'Player 2', (240, 180, 180), (220, 160, 160))
            angle_dialogue = create_text_area(screen, 80, 10, 85, 20, 'Angle (0-360)', (240, 180, 180), (220, 160, 160))
            player2_angle_input = create_text_input(screen, 165, 10, 65, 20, player2.angle_text, 0, 360, '000.0000', '359.9999', (240, 180, 180), (220, 160, 160))
            velocity_dialogue = create_text_area(screen, 235, 10, 90, 20, 'Velocity (0-10)', (240, 180, 180), (220, 160, 160))
            player2_velocity_input = create_text_input(screen, 325, 10, 60, 20, player2.velocity_text, 0, 10, '0.0000', '10.0000', (240, 180, 180), (220, 160, 160))
            next_state = 'clear_ui_3'
            if settings["Alternate"]:
                next_state = 'clear_ui_2'
            submit_2_button = create_submit_button(screen, 390, player2, states, player2_angle_input, player2_velocity_input, 'p2_input', next_state, "Fire!", (255, 120, 120), (200, 120, 120))
            
            # create the widgets afresh with the current value
            states['p2_widget_gen'] = False
            states['p2_input'] = True

        if states['p2_input']:
            pygame_widgets.update(events)
            pygame.display.update()
       
        if states['clear_ui_2']:
            player2_id.hide()
            player2_angle_input.hide()
            player2_velocity_input.hide()
            submit_button.hide()
            angle_dialogue.hide()
            velocity_dialogue.hide()
            screen.blit(temp_screen, (0, 0), area_to_save)
            missile2 = make_a_missile(player2,(255, 200, 200))
            states["p2_missiles"] = True
            states['clear_ui_2'] = False

        if states['p2_missiles']:
            missile_done = missile2.fire_missile(screen, planets, collision_planets, settings, player2)
            if missile_done:
                missile_launch.stop()
                states['p2_missiles'] = False
                states['p2_message'] = True
                temp_screen.blit(screen, (0, 0), area_to_save)
                show_a_message((200,255,200), missile2.message)
                missile1_travelling = False
                missile2_travelling = False
                # if not settings['RemoveTrails']:
                #     temp_screen.blit(screen, (0, 0), area_to_save)

            collisions = pygame.sprite.spritecollide(missile2, players, 
                                                     False)
            if collisions:
                missile_travelling.stop()
                missile_launch.stop()
                ship_strike.play()
                states['p2_missiles'] = False
                states['end_game'] = True
                missile1_travelling = False
                missile2_travelling = False
                if collisions[0].name == player2.name:
                    win_message = f"{settings['Player1Name']} has won!"
                else:
                    win_message = f"{settings['Player2Name']} has won!"
            pygame.display.update()

        if states['p2_message']:
            pass

        if states['clear_ui_3']:
            player2_id.hide()
            player2_angle_input.hide()
            player2_velocity_input.hide()
            submit_button.hide()
            angle_dialogue.hide()
            velocity_dialogue.hide()
            screen.blit(temp_screen, (0, 0), area_to_save)
            missile1 = make_a_missile(player1,(190, 190, 255))
            missile2 = make_a_missile(player2,(255, 200, 200))
            missile1_travelling = True
            missile2_travelling = True
            states["both_missiles"] = True
            states['clear_ui_3'] = False

        if states['both_missiles']:
            if missile1_travelling:
                missile1_done = missile1.fire_missile(screen, planets, collision_planets, settings, player1)
                collisions1 = pygame.sprite.spritecollide(missile1, players, 
                                                          False)
            if missile2_travelling:
                missile2_done = missile2.fire_missile(screen, planets, collision_planets, settings, player2)
                collisions2 = pygame.sprite.spritecollide(missile2, players, 
                                                          False)
            if missile1_done or collisions1:
                missile1_travelling = False
            if missile2_done or collisions2:
                missile2_travelling = False

            if missile1_done and missile2_done:
                states['both_missiles'] = False
                states['both_message'] = True
                temp_screen.blit(screen, (0, 0), area_to_save)
                show_a_message((200,255,200), missile1.message, -30)
                show_a_message((200,255,200), missile2.message)
            elif missile1_done and collisions2:
                states['both_missiles'] = False
                states['end_game'] = True
                if collisions2[0].name == player2.name:
                    win_message = f"{settings['Player1Name']} has won!"
                else:
                    win_message = f"{settings['Player2Name']} has won!"
            elif missile2_done and collisions1:
                states['both_missiles'] = False
                states['end_game'] = True
                if collisions1[0].name == player1.name:
                    win_message = f"{settings['Player2Name']} has won!"
                else:
                    win_message = f"{settings['Player1Name']} has won!"
            elif collisions1 and collisions2: 
                states['both_missiles'] = False
                states['end_game'] = True
                hits = set()
                hits.add(collisions1[0].name)
                hits.add(collisions2[0].name)
                if len(list(hits)) == 2:
                    win_message = f"Its a draw!"
                elif list(hits)[0] == player1.name:
                    win_message = f"{settings['Player2Name']} has won!"
                else:
                    win_message = f"{settings['Player1Name']} has won!"
                
        if states['both_message']:
            pass
            
        if states['end_game']:
            temp_screen.blit(screen, (0, 0), area_to_save)
            show_a_message((200,255,200), win_message)
            show_a_message((200,255,200), f"Seed: {settings['Seed']}", 25)
            states['end_game'] = False
            states['end_wait'] = True
            player1 = None
            player2 = None
            players = None
            all_sprites = None
            planets = None
            collision_planets = None
            win_message = ''
            local_seed = None
            if len(seed.get_value()) > 0:
                local_seed = int(seed.get_value())
            settings['Seed'] = local_seed
            if not settings['Seed']:
                settings['Seed'] = int(''.join(str(random.randint(0,9)) for _ in range(12)))
            random.seed(int(settings["Seed"]))
            #screen.fill((0, 0, 0))
        
        if states['end_wait']:
            pass

        pygame.display.flip()
        clock.tick(60)
    return()


mysolarized = pygame_menu.themes.THEME_SOLARIZED.copy()
mysolarized.title_font_size=math.ceil(settings['DisplayHeight']/24)
mainmenu = pygame_menu.Menu('Welcome', settings['DisplayWidth'], settings['DisplayHeight'], 
                                     theme=mysolarized)
myblue = pygame_menu.themes.THEME_BLUE.copy()
myblue.title_font_size=math.ceil(settings['DisplayHeight']/24)
settingmenu = pygame_menu.Menu('Settings', settings['DisplayWidth'], settings['DisplayHeight'], 
                               theme=myblue)
about = pygame_menu.Menu('About', settings['DisplayWidth'], settings['DisplayHeight'], 
                                     theme=myblue)
    
build_menu(mainmenu, settingmenu, about, settings, settings['DisplayHeight'], run_the_game)
while running:
    # Look at every event in the queue
    mainmenu.mainloop(screen)
pygame.mixer.music.stop()
pygame.mixer.quit()
pygame.quit()