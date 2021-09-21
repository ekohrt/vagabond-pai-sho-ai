# -*- coding: utf-8 -*-
"""
Created on Wed Sep 15 15:59:08 2021

@source: improved from https://github.com/russs123/pygame_button
--> explanation video here: https://www.youtube.com/watch?v=jyrP0dDGqgY
"""

import pygame

#define colours
black = (0, 0, 0)
white = (255, 255, 255)

light_grey = (212, 212, 212)
light_blue = (140, 200, 235)
darker_blue = (75, 170, 225)


class Button():
        
    """
    Constructor
    
    @param x, y are the top left coordinates of the button. 
    @param screen is the screen on which to draw this button
    @param text is the button's text.
    
    Optional parameters:
    @param width is the width in pixels
    @param height is the height in pixels
    @param button_color is the resting color, for when the button is not being interacted with.
    @param hover_color is the color when mouse is hovering over button
    @param click_color is the color when the button is being clicked
    """
    def __init__(self, x, y, screen, text, width=180, height=70, button_color=light_grey,
                 hover_color=light_blue, click_color=darker_blue, text_color=black, text_size=30):
        self.x = x
        self.y = y
        self.screen = screen    # save reference to the screen where this button is drawn
        self.text = text
        self.font = pygame.font.SysFont('Constantia', text_size)
        self.clicked = False    # flag for tracking when mouse is clicking the button
        
        #optional params
        self.width = width
        self.height = height
        self.button_color = button_color
        self.hover_color = hover_color
        self.click_color = click_color
        self.text_color = text_color

    """
    Draws the button on screen, and also returns True if it's clicked.
    Call this method in the main game loop.
    
    @return action is True if button is clicked once: so perform some action
    """
    def draw_button(self):
        action = False

        #get mouse position
        pos = pygame.mouse.get_pos()

        #create pygame Rect object for the button
        button_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        #check mouseover and clicked conditions
        if button_rect.collidepoint(pos):     #if cursor is within/over the button:
            #if mouse clicked, set flags:
            if pygame.mouse.get_pressed()[0] == 1:
                self.clicked = True
                pygame.draw.rect(self.screen, self.click_color, button_rect)
            #when mouse click is released, perform action. Then reset flags:
            elif pygame.mouse.get_pressed()[0] == 0 and self.clicked == True:
                self.clicked = False
                action = True
                pygame.draw.rect(self.screen, self.hover_color, button_rect) 
            #if just hovering, change color:
            else:
                pygame.draw.rect(self.screen, self.hover_color, button_rect)
        else:
            pygame.draw.rect(self.screen, self.button_color, button_rect) #if mouse not over button: draw button normally
        
        #add shading to button (aesthetic white and black border to look 3D)
        pygame.draw.line(self.screen, white, (self.x, self.y), (self.x + self.width, self.y), 2)
        pygame.draw.line(self.screen, white, (self.x, self.y), (self.x, self.y + self.height), 2)
        pygame.draw.line(self.screen, black, (self.x, self.y + self.height), (self.x + self.width, self.y + self.height), 2)
        pygame.draw.line(self.screen, black, (self.x + self.width, self.y), (self.x + self.width, self.y + self.height), 2)

        #add text to button
        text_img = self.font.render(self.text, True, self.text_color)
        #try to center the text in the button
        text_len = text_img.get_width()
        text_hgt = text_img.get_height()
        text_x = self.x + self.width//2 - text_len//2
        text_y = self.y + self.height//2 - text_hgt//2 +2
        self.screen.blit(text_img, (text_x, text_y))
        return action     #(True/False)



"""
Example Code
"""
#
#pygame.init()
#
##define colours
#bg = (204, 102, 0)
#red = (255, 0, 0)
#
#counter = 0
#
#screen_width = 600
#screen_height = 600
#
#myScreen = pygame.display.set_mode((screen_width, screen_height))
#pygame.display.set_caption('Button Demo')
#
#font = pygame.font.SysFont('Constantia', 30)
#
#againBtn = Button(75, 200, myScreen, 'Play Again?')
#quitBtn = Button(325, 200, myScreen, 'Quit?')
#downBtn = Button(75, 350, myScreen, 'Down')
#upBtn = Button(325, 350, myScreen, 'Up')
#
##game loop
#run = True
#while run:
#    myScreen.fill(bg)
#    #draw the button on screen, and 
#    if againBtn.draw_button():
#        print('Again')
#        counter = 0
#    if quitBtn.draw_button():
#        print('Quit')
#    if upBtn.draw_button():
#        print('Up')
#        counter += 1
#    if downBtn.draw_button():
#        print('Down')
#        counter -= 1
#    counter_img = font.render(str(counter), True, red)
#    myScreen.blit(counter_img, (280, 450))
#    for event in pygame.event.get():
#        if event.type == pygame.QUIT:
#            run = False    
#    pygame.display.update()
#pygame.quit()