import pygame
import time
import os
import random
import pygame.camera
from pygame.locals import *

DEVICE = '/dev/video0'
FONT_PATH = '/home/temp/Documents/PhotoBoothEsisar-main/font.ttf'
WATERMARK_PATH = '/home/temp/Documents/PhotoBoothEsisar-main/contour.png'
SAVE_CAPTURE_PATH = '/home/temp/Documents/PhotoBoothEsisar-main/captures/'
#CAMERA_RESOLUTION = (1280, 720)
CAMERA_RESOLUTION = (1600, 896)
#CAMERA_RESOLUTION = (1920, 1080)
SCREEN_RESOLUTION = (1600, 900)
#SCREEN_RESOLUTION = (1280, 1024)
#SCREEN_RESOLUTION = (1920, 1080)


CAMERA_Y_POSTION_OFFSET = 0#150
FONT_SIZE = 70
FONT_TIMER_SIZE = 200
TEXT_COLOR = (0,0,0)
TEXT_POSITION = (SCREEN_RESOLUTION[0] / 2, SCREEN_RESOLUTION[1] / 2)
COUNTDOWN_BEFORE_CAPTURE_IN_SECONDS = 3
DELAY_BEFORE_CONFIRMATION_TEXT_IN_MILLIS = 1000
CONFIRMATION_TEXT = "CONFIRMER"
CONFIRMATION_TEXT_COLOR = (255,255,0)
CONFIRMATION_TEXT_POSTION = (SCREEN_RESOLUTION[0]* 1  / 3, SCREEN_RESOLUTION[1]* 1  / 15)

CANCELATION_TEXT = "ANNULER "
CANCELATION_TEXT_COLOR = (255,0,0)
CANCELATION_TEXT_POSTION = ( SCREEN_RESOLUTION[0] *2 / 3, SCREEN_RESOLUTION[1]* 1  / 15)
CONFIRMATION_TIMEOUT_IN_MILLIS = 10000
TIME_BEFORE_SLIDESHOW_IN_MILLIS = 30000
TIME_BETWEEN_PICTURE_ON_SLIDESHOW_IN_MILLIS = 3000

_COUNTDOWN_EVENT = pygame.USEREVENT
_SLIDESHOW_EVENT = pygame.USEREVENT + 1

def take_picture(display, cameraSurface, waterMarkImg):
    cameraSurface = pygame.transform.flip(cameraSurface, True, False)
    display.blit(cameraSurface, (0,CAMERA_Y_POSTION_OFFSET))
    display.blit(waterMarkImg, (0,0))
    pygame.display.update()
    #display = pygame.transform.flip(display, True, False)
    filename = SAVE_CAPTURE_PATH + time.asctime() + '.bmp'
    pygame.image.save(display, filename)
    return filename
   

def confirm_picture(display, joystick,  font, filename):
    pygame.time.wait(DELAY_BEFORE_CONFIRMATION_TEXT_IN_MILLIS)
    text = font.render(CONFIRMATION_TEXT, True, CONFIRMATION_TEXT_COLOR)
    textRect = text.get_rect()
    textRect.center = CONFIRMATION_TEXT_POSTION
    display.blit(text, textRect)
    text = font.render(CANCELATION_TEXT, True, CANCELATION_TEXT_COLOR)
    textRect = text.get_rect()
    textRect.center = CANCELATION_TEXT_POSTION
    display.blit(text, textRect)
    pygame.display.update()
    pygame.event.clear()
    event = pygame.event.wait(CONFIRMATION_TIMEOUT_IN_MILLIS)
    if event.type == pygame.JOYBUTTONDOWN and joystick.get_button(1) or event.type == pygame.NOEVENT:
        os.remove(filename)

def show_photobooth(display, camera, cameraSurface, font, textStr, waterMarkImg):
    CameraSurface = camera.get_image(cameraSurface)
    cameraSurface = pygame.transform.flip(CameraSurface, True, False)
    text = font.render(textStr, True, TEXT_COLOR)
    textRect = text.get_rect()
    textRect.center = TEXT_POSITION

    display.blit(cameraSurface, (0,CAMERA_Y_POSTION_OFFSET))
    display.blit(waterMarkImg, (0,0))
    display.blit(text, textRect)
    pygame.display.update()

def show_slideshow(display):
    fileList = os.listdir(SAVE_CAPTURE_PATH)
    if fileList != []:
        filename = random.choice(fileList)
        filePath = os.path.join(SAVE_CAPTURE_PATH ,filename)
        slideShow = pygame.image.load(filePath)
        display.blit(slideShow, (0,0))
        pygame.display.update()
    

def photobooth():
    os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"
    #init Section
    slideshowTime = False
    textStr = ""
    countdown = COUNTDOWN_BEFORE_CAPTURE_IN_SECONDS
    pygame.init()
    pygame.camera.init()
    pygame.joystick.init()
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    pygame.event.set_blocked((pygame.JOYAXISMOTION))
    display = pygame.display.set_mode(SCREEN_RESOLUTION, pygame.FULLSCREEN )
    camera = pygame.camera.Camera(DEVICE, CAMERA_RESOLUTION)
    camera.start()
    
    cameraSurface = pygame.surface.Surface(CAMERA_RESOLUTION, 0, display)
    waterMarkImg = pygame.image.load(WATERMARK_PATH)
    waterMarkImg = pygame.transform.scale(waterMarkImg, SCREEN_RESOLUTION)
    font = pygame.font.Font(FONT_PATH,FONT_SIZE)
    font_timer = pygame.font.Font(FONT_PATH,FONT_TIMER_SIZE)

    pygame.time.set_timer(_SLIDESHOW_EVENT, TIME_BEFORE_SLIDESHOW_IN_MILLIS)

    if not os.path.isdir(SAVE_CAPTURE_PATH):
        os.mkdir(SAVE_CAPTURE_PATH)

    #clock = pygame.time.Clock()  	
    # Loop Section
    run = True
    while run:
        if not slideshowTime:
            show_photobooth(display, camera, cameraSurface, font_timer, textStr, waterMarkImg)

        for event in pygame.event.get():
            if event.type == QUIT:
                run = False

            elif event.type == pygame.JOYBUTTONDOWN:
                pygame.time.set_timer(_SLIDESHOW_EVENT, TIME_BEFORE_SLIDESHOW_IN_MILLIS)
                if slideshowTime:
                    slideshowTime = False
                else:
                    countdown = COUNTDOWN_BEFORE_CAPTURE_IN_SECONDS
                    textStr = str(countdown)
                    pygame.time.set_timer(_COUNTDOWN_EVENT, 1000)
                
            elif event.type == _COUNTDOWN_EVENT:
                countdown = countdown - 1
                if countdown == 0:
                    pygame.time.set_timer(_COUNTDOWN_EVENT, 0)
                    textStr = ""
                    filename = take_picture(display, cameraSurface, waterMarkImg)
                    confirm_picture(display, joystick, font, filename)
                    
                else :
                    textStr = str(countdown)

            elif event.type == _SLIDESHOW_EVENT:
                slideshowTime = True
                pygame.time.set_timer(_SLIDESHOW_EVENT, TIME_BETWEEN_PICTURE_ON_SLIDESHOW_IN_MILLIS)
                show_slideshow(display)
                    
        #clock.tick(30)

    camera.stop()
    pygame.quit()
    return

if __name__ == '__main__':
    photobooth()
