#!/usr/bin/python3
#
# coding=UTF-8


# Imports
import pygame


if __name__ == '__main__':
    # Main init
    # Init. the lib.
    try:
        rets = pygame.init()
    except:
        print("PYGame initialization error - You should have to reinstall PYGame")
        exit(1)

    # Basic vars
    s_width = 1000
    s_height = 600
    run = True


    # Making display screen. Don't forget the last tag!
    screen = pygame.display.set_mode((s_width, s_height), pygame.RESIZABLE)
    pygame.display.set_caption("Test")

    screen.fill((255,255,255))
    pygame.display.update()

    # Main loop
    while run:
        # event detection
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            # The part which matters for our purposes
            if event.type == pygame.WINDOWRESIZED:
                s_width, s_height = screen.get_width(), screen.get_height()
                print(f"Width : {s_width} x Height : {s_height}")
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
        # Test line to see if the window resizing works properly
        #pygame.draw.line(screen, (255, 255, 255), (int(0.3*s_width), int(0.25*s_height)), (int(0.8*s_width), int(0.25*s_height)))
        screen.fill((255,0,0))
        pygame.display.update()

        # Final flip
        #pygame.display.flip()

    # Quit
    pygame.quit()
