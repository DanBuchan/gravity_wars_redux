import pygame
import pygame_widgets
from pygame_widgets.textbox import TextBox
from pygame_widgets.button import Button
import re

number_pattern = re.compile('^[1234567890\\n]*\.*[1234567890\\n]*$')

def create_text_area(screen, x, y, width, height, dialogue_text, colour, bordercolour):
    return Button(screen,  x, y, width, height, text=dialogue_text,
                radius=2, onClick=lambda: None, 
                borderThickness=2, textColour=(20, 20, 20),
                borderColour=bordercolour, inactiveColour=colour,
                hoverColour=colour, pressedColour=colour,
                textHAlign="left", textVAlign="top", hoverBorderColour=bordercolour,
                pressedBorderColour=bordercolour, margin=5,
                font=pygame.font.SysFont('bold', 16))

def create_text_input(screen, x, y, width, height, field_text, min, max, min_text, max_text, colour, bordercolour):
    field = TextBox(screen, x, y, width, height, fontSize=16,
                borderColour=bordercolour, textColour=(0, 0, 0),
                colour=colour, radius=2, borderThickness=2,
                placeholderText=field_text)
    field.textOffsetTop = 12 // 3 + 2
    def verify():
        text = field.getText()
        #print(text)
        if len(text) == 0:
            return
        if re.search(number_pattern, text):
            value = float(text)
            if value < min:
                field.setText(min_text)
            if value > max:
                field.setText(max_text)
        else:
            field.setText('')
        return None
    field.onTextChanged = verify
    return(field)

def create_submit_button(screen, location, player, states, angle_input, velocity_input, this_state, next_state, text, colour, bordercolour): 
    submit_button = Button(screen, location, 10, 60, 20, text=text,
                fontSize=7, radius=2, onClickParams=[player, states, angle_input, velocity_input], 
                borderThickness=2,
                borderColour=bordercolour,
                inactiveColour=colour,
                hoverColour=colour,
                pressedColour=colour,
                hoverBorderColour=bordercolour,
                pressedBorderColour=bordercolour)
    
    def submit(player, states, angle_input, velocity_input):
        # Get text in the textbox
        if len(angle_input.getText()) > 0:
            player.angle_text = angle_input.getText()
            player.angle = float(player.angle_text)
        if len(velocity_input.getText()) > 0:
            player.velocity_text = velocity_input.getText()
            player.velocity = float(player.velocity_text)
            if player.velocity == 0.0:
                player.velocity = 0.00001
            
        states[this_state] = False
        states[next_state] = True
    submit_button.onClick = submit
    return submit_button
