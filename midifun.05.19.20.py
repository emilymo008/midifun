# starting over...trying to control automation for recording. deleting rtimidi stuff

import pygame
import pygame.midi
import pygame.mouse
import pygame.font
import os
from AppKit import NSScreen
import pyautogui

#### ref ####
# key ref: https://www.pygame.org/docs/ref/key.html

winw = NSScreen.mainScreen().frame().size.width
winh = NSScreen.mainScreen().frame().size.height

mx = pyautogui.position()[0]
my = pyautogui.position()[1]

pygame.init()
pygame.midi.init()
pygame.font.init()

dim = (200, int(winh))  # dimensions of window
startpos = int(winw - dim[0]), 0
os.environ['SDL_VIDEO_WINDOW_POS'] = str(startpos[0]) + "," + str(startpos[1])

#### set up text ####
font = pygame.font.SysFont('Courier', 24, bold = False)
scrolldir_title = font.render('scroll:', True, (0, 0, 0))
scrollspd_title = font.render('speed:', True, (0, 0, 0))
chan_title = font.render('channel:', True, (0, 0, 0))

window = pygame.display.set_mode(dim)
white = (255, 255, 255)
blue = (61, 121, 219)

# TODO: get window to follow mouse (restrict to a certain rectangle on the right side of the screen) since I can't make window transparent
#   https://stackoverflow.com/questions/44520491/can-i-move-the-pygame-game-window-around-the-screen-pygame
# TODO: change window color with volume level



##########################################################################################
#### pygame

# find and connect to IAC Bus 2
for i in range(pygame.midi.get_count()):
    d = pygame.midi.get_device_info(i)
    s = str(d[1])  # device name
    o = str(d[3])  # output status
    if s == "b'IAC Driver IAC Bus 2'" and o == '1':
        daw = pygame.midi.Output(i)
        device = str(i)
        print('device index: ' + device)


alive = True  # start pygame process

vol_init = 100  # is there seriously no way to get current volume??? might come in handy

scrolldir = True  # set initial scroll direction (adjust if using scrollreverser / mouse or not)
scrolldir_val = font.render(str(int(scrolldir) + 1), True, (0, 0, 0))  # make the value into a mode number that can be printed
if scrolldir:  # code the direction of the scroll
    up = 5
    down = 4
else:
    up = 4
    down = 5

scrollspd = 3  # set initial scroll increment
scrollspd_val = font.render(str(scrollspd), True, (0, 0, 0))
remainder_hi = (127 - vol_init) % scrollspd
remainder_lo = vol_init % scrollspd

downind = vol_init  # current volume position
print('position ' + str(downind))

chan = 7  # current channel, defaulted to volume
chan_val = font.render(str(chan), True, (0, 0, 0))

while alive:
    mx = pyautogui.position()[0]
    my = pyautogui.position()[1]

    if mx > startpos[0] and my > startpos[1]:  # show blue when cursor is in app window
        window.fill(blue)
    else:
        window.fill(white)

    # render text for parameter titles
    window.blit(scrolldir_title, (10, 10))
    window.blit(scrolldir_val, (120, 10))
    window.blit(scrollspd_title, (10, 34))
    window.blit(scrollspd_val, (120, 34))
    window.blit(chan_title, (10, 58))
    window.blit(chan_val, (120, 58))
    pygame.display.update()

    for e in pygame.event.get():

        if e.type == pygame.MOUSEBUTTONDOWN:  # for mouse events:

            ## mouse left click
            if e.button == 1:  # if mouse clicked...
                scrolldir = bool(1 - scrolldir)
                if scrolldir:  # code the direction of the scroll
                    up = 5
                    down = 4
                else:
                    up = 4
                    down = 5
                scrolldir_val = font.render(str(int(scrolldir) + 1), True, (0, 0, 0))  # make the value into a mode number that can be printed

            ## mouse right click
            if e.button == 3:
                if chan == 7:
                    chan = 1  # TODO: not sure if this is the right channel to choose
                elif chan == 1:
                    chan = 7
                print(chan)
                chan_val = font.render(str(chan), True, (0, 0, 0))  # TODO: figure out where automation is going to and why it isn't showing on screen


            ## mouse scroll
            # traditionally 4 means scroll down, 5 means up
            if 0 < downind < 127:  # if haven't reached the limits yet...
                if e.button == up:  # if mouse scrolled up
                    if downind + scrollspd > 127:  # if about to hit the upper limit...
                        downind += remainder_hi  # just scroll to the limit
                    else:  # or else just scroll the specified increment
                        downind += scrollspd
                if e.button == down:
                    if downind - scrollspd < 0:  # if about to hit the lower limit...
                        downind = 0  # just scroll to the limit
                    else:  # or else just scroll the specified increment
                        downind -= scrollspd
            print('position ' + str(downind) + ' channel ' + str(chan))
            daw.write_short(0xb0, chan, downind)  # set level to downind

            if downind == 0:  # if at the lower limit...
                if e.button == up:
                    if remainder_lo != 0:
                        downind += remainder_lo
                    else:
                        downind += scrollspd
                    print('position ' + str(downind) + ' channel ' + str(chan))
                    daw.write_short(0xb0, chan, downind)  # set level to downind
            if downind == 127:  # if at the upper limit...
                if e.button == down:
                    if remainder_hi != 0:
                        downind -= remainder_hi
                    else:
                        downind -= scrollspd
                    print('position ' + str(downind) + ' channel ' + str(chan))
                    daw.write_short(0xb0, chan, downind)  # set level to downind


            # TODO: the scroll only works when I'm in the window but I can't make the window transparent! think of a workaround
            # TODO: is there a way to override the built in scroll acceleration?

        if e.type == pygame.KEYDOWN:  # for keyboard events:

            ## key up or down to control scroll granularity
            if e.key == pygame.K_UP:
                if scrollspd == 4:  # limit highest speed
                    scrollspd = 4
                else:
                    scrollspd += 1
            if e.key == pygame.K_DOWN:
                if scrollspd == 1:
                    scrollspd = 1
                else:
                    scrollspd -= 1
            scrollspd_val = font.render(str(scrollspd), True, (0, 0, 0))

            ## to quit app
            if e.key == pygame.K_x:  # https://www.pygame.org/docs/ref/key.html
                print('hey that hurt')
                daw.close()
                pygame.midi.quit()
                exit()
