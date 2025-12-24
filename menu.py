import pygame_menu
from pygame_menu import themes
import math

def settings_menu(mainmenu, settingmenu):
    mainmenu._open(settingmenu)
def about_menu(mainmenu, about):
    mainmenu._open(about)

def build_menu(mainmenu, settingmenu, about, settings, screenHeight, run_the_game):
    menu_font_size = math.ceil(screenHeight/24)
    player1name = settingmenu.add.text_input('Player 1 Name: ', default=settings['Player1Name'], maxchar=20, font_size=menu_font_size)
    player2name = settingmenu.add.text_input('Player 2 Name: ', default=settings['Player2Name'], maxchar=20, font_size=menu_font_size)
    planetNumber = settingmenu.add.range_slider('Pick Number of Planets',
                          (settings['MinPlanets'],
                           settings['MaxPlanets']), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], 1, font_size=menu_font_size)
    allowBlackholes = settingmenu.add.toggle_switch('Allow Black holes', settings['Blackholes'], toggleswitch_id='blackholes', font_size=menu_font_size)
    allowNakedBlackholes = settingmenu.add.toggle_switch('Allow Naked Singularities', settings['NakedBlackholes'], toggleswitch_id='nakedblackholes', font_size=menu_font_size)
    removeTrails = settingmenu.add.toggle_switch('Erase Missile Trails', settings['RemoveTrails'], toggleswitch_id='removetrails', font_size=menu_font_size)
    alternateTurns = settingmenu.add.toggle_switch('Alternate Turns', settings['Alternate'], toggleswitch_id='alternateturns', font_size=menu_font_size)
    swapSides = settingmenu.add.toggle_switch('SwapSides', settings['SwapSides'], toggleswitch_id='swapsides', font_size=menu_font_size)
    seed = settingmenu.add.text_input('Solar System Seed: ', '', valid_chars=['1','2','3','4','5','6','7','8','9','0'], maxchar=12, font_size=menu_font_size)
    
    info_text = "This is a remake of Ed Bartz's Gravity Wars v2.0. With some additional tweaks"
    about.add.label(info_text, max_char=-1, font_size=menu_font_size)
    
    mainmenu.add.button('Start', run_the_game, player1name, 
                        player2name, planetNumber, 
                        allowBlackholes, 
                        allowNakedBlackholes,
                        removeTrails, alternateTurns, seed, swapSides,
                        settings['MaxMass'], font_size=menu_font_size)
    mainmenu.add.button('Settings', settings_menu, mainmenu, settingmenu, font_size=menu_font_size)
    mainmenu.add.button('About', about_menu, mainmenu, about, font_size=menu_font_size)
    mainmenu.add.button('Quit', pygame_menu.events.EXIT, font_size=menu_font_size)
