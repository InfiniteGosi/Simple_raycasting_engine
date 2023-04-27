import pygame as pg
import math
import sys

SCREEN_HEIGHT = 480
SCREEN_WIDTH = SCREEN_HEIGHT * 2
MAP_SIZE = 8
TILE_SIZE = (SCREEN_WIDTH / 2) / MAP_SIZE
MAX_DEPTH = int(SCREEN_HEIGHT)
FOV = math.pi / 3
HALF_FOV = FOV / 2
CASTED_RAYS = 120
STEP_ANGLE = FOV / CASTED_RAYS
SCALE = (SCREEN_WIDTH / 2) / CASTED_RAYS

player_x = (SCREEN_WIDTH / 2) / 2
player_y = SCREEN_HEIGHT / 2
player_angle = math.pi
vel = 10
# moving direction
forward = True

# init pg
pg.init()

font = pg.font.SysFont('Monospace Regular', 30)

MAP = (
    '########'
    '#  #   #'
    '#  #   #'
    '#    ###'
    '#      #'
    '#  ##  #'
    '#  #   #'
    '########'
)
            
# create a window
win = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
caption = pg.display.set_caption('Simple pygame ray casting engine by Khang Ho')

# init timer
clock = pg.time.Clock()

def drawMap():
    for row in range(MAP_SIZE):
        for col in range(MAP_SIZE):
            square = row * MAP_SIZE + col
            pg.draw.rect(win,
                         (200, 200, 200) if MAP[square] == '#' else (128, 128, 128), 
                         (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE - 2, TILE_SIZE - 2))
    
    # draw player
    pg.draw.circle(win, (255, 0, 0), (player_x, player_y), 10)

    #draw player direction
    pg.draw.line(win, (0, 255, 0), (player_x, player_y), 
                                   (player_x - math.sin(player_angle) * 50,
                                    player_y + math.cos(player_angle) * 50), 3)
    #draw player FOV
    pg.draw.line(win, (0, 255, 0), (player_x, player_y), 
                                   (player_x - math.sin(player_angle + HALF_FOV) * 50,
                                    player_y + math.cos(player_angle + HALF_FOV) * 50), 3)
    pg.draw.line(win, (0, 255, 0), (player_x, player_y), 
                                   (player_x - math.sin(player_angle - HALF_FOV) * 50,
                                    player_y + math.cos(player_angle - HALF_FOV) * 50), 3)

# ray casting algorithm
def castRay():
    # leftmost angle of FOV
    start_angle = player_angle - HALF_FOV

    # loop over casted rays
    for ray in range(CASTED_RAYS):
        # cast ray in step by step
        for depth in range(MAX_DEPTH):
            # get ray target coordinates
            target_x = player_x - math.sin(start_angle) * depth
            target_y = player_y + math.cos(start_angle) * depth

            # convert target x, y to map col, row
            col = int(target_x / TILE_SIZE)
            row = int(target_y / TILE_SIZE)

            # calculate square index
            square = row * MAP_SIZE + col

            # ray collision
            if MAP[square] == '#':
                pg.draw.rect(win, (0, 255, 0), (col * TILE_SIZE,
                                                row * TILE_SIZE,
                                                TILE_SIZE - 2,
                                                TILE_SIZE-2))
                # draw casted rays
                pg.draw.line(win, (255, 255, 0), (player_x, player_y), (target_x, target_y))

                # wall shading
                color = 255 / (1 + depth * depth * 0.0001)

                # fix fishbowl effect
                depth *= math.cos(player_angle - start_angle)

                # calculate wall height
                wall_height = 21000 / (depth + 0.0001)

                # fix stuck at the wall
                if wall_height > SCREEN_HEIGHT: 
                    wall_height = SCREEN_HEIGHT

                # draw 3D projection (rectangle by rectangle)
                pg.draw.rect(win, (color, color, color), (SCREEN_HEIGHT + ray * SCALE, (SCREEN_HEIGHT / 2) -  wall_height / 2, SCALE, wall_height))
                break

        # increment angle by a single step
        start_angle += STEP_ANGLE

def draw3DBackground():
    # floor
    pg.draw.rect(win, (150, 75, 0), (480, SCREEN_HEIGHT / 2, SCREEN_HEIGHT, SCREEN_HEIGHT))
    # ceiling
    pg.draw.rect(win, (0, 0, 230), (480, -SCREEN_HEIGHT / 2, SCREEN_HEIGHT, SCREEN_HEIGHT))


def displayFPS():
    fps = str(int(clock.get_fps()))
    fps_surf = font.render(f'FPS: {fps}', False, (255, 255, 255))
    fps_rect = fps_surf.get_rect(center = (35, 10))
    win.blit(fps_surf, fps_rect)

def displayPlayerStat():
    pos_x = str(round(player_x, 2))
    posx_surf = font.render(f'x: {pos_x}', False, (255, 255, 255))
    posx_rect = posx_surf.get_rect(center = (45, 30))
    win.blit(posx_surf, posx_rect)

    pos_y = str(round(player_y, 2))
    posy_surf = font.render(f'y: {pos_y}', False, (255, 255, 255))
    posy_rect = posy_surf.get_rect(center = (45, 50))
    win.blit(posy_surf, posy_rect)

    angle = str(round(player_angle * 180 / math.pi, 2))
    posy_surf = font.render(f'angle: {angle}', False, (255, 255, 255))
    posy_rect = posy_surf.get_rect(center = (70, 70))
    win.blit(posy_surf, posy_rect)

    
while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit(0)

        col = int(player_x / TILE_SIZE)
        row = int(player_y / TILE_SIZE)

        # calculate square index
        square = row * MAP_SIZE + col

        # player collision
        if MAP[square] == '#':
            if forward:
                player_x -= -math.sin(player_angle) * vel
                player_y -= math.cos(player_angle) * vel
            else:
                player_x += -math.sin(player_angle) * vel
                player_y += math.cos(player_angle) * vel

        # update 2D background
        pg.draw.rect(win, (0, 0, 0), (0, 0, SCREEN_HEIGHT, SCREEN_WIDTH))

        # update 3D background
        draw3DBackground()
        
        # draw map to window
        drawMap()

        # apply raycasting
        castRay()

        # get user input
        keys = pg.key.get_pressed()
        
        # rotating and movement
        if keys[pg.K_LEFT]: player_angle -= 0.2
        if keys[pg.K_RIGHT]: player_angle += 0.2
        if keys[pg.K_UP]:
            forward = True
            player_x += -math.sin(player_angle) * vel
            player_y += math.cos(player_angle) * vel
        if keys[pg.K_DOWN]:
            forward = False
            player_x -= -math.sin(player_angle) * vel
            player_y -= math.cos(player_angle) * vel
        
        # set fps
        dt = clock.tick(30)

        # display fps
        displayFPS()

        # display player position
        displayPlayerStat()

        # draw half the window
        pg.display.flip()

        

        


