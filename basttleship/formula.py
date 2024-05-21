import math
import pygame

def draw_text(screen: pygame.Surface, text: str, textColor: tuple[int, int, int], font: pygame.font.Font, position: tuple[int, int]) -> bool: 
    '''
    screen: surface to display on (pygame.Surface)
    text: string to display on (str)
    textColor: text color (tuple[, int, int])
    font: text font (pygame.font.Font)
    position: text x and y position (tuple[int, int])
    ----------------------------------------------------------------
    Display text.
    return -> bool: True if display succeeded, False if display failed.
    '''
    
    try: 
        screen.blit(font.render(text, True, textColor), position)
        return True
    except Exception as e: 
        print(f"Failed to draw text -> {e}")
        return False


def xy_velocity_to_one_direction_velocity(xv: float, yv: float) -> tuple[float, float]: 
    '''
    xv: x velocity (float)
    yv: y velocity (float)
    ----------------------------------------------------------------
    Translate x and y velocity to one direction velocity.
    return -> tuple[float, float]: velocity and direction(radians).
    '''
    V = (xv**2+yv**2)**0.5
    d = math.atan2(yv, xv)
    return V,d

def direction_to_object2(x1: float, y1: float, x2: float, y2: float) -> float: 
    '''
    x1: x position (float)
    y1: y position (float)
    x2: x position (float)
    y2: y position (float)
    ----------------------------------------------------------------
    Calculate the angle between two objects' distence.
    From the prespective of object 1(x1, y1).
    return -> tuple[float, float]: derection(radians).
    '''
    radians = math.acos((x2-x1)/distence(x1, y1, x2, y2))
    return radians


def one_direction_velocity_to_xy_velocity(V: float, d: float) -> tuple[float, float]: 
    '''
    V: velociy (float)
    d: direction(radians) (float)
    ----------------------------------------------------------------
    Translate one direction velocity to x and y velocity.
    return -> tuple[float, float]: x and y velocity.
    '''
    xv = math.cos(d)*V
    yv = math.sin(d)*V
    return xv, yv

def distence(x1: float, y1: float, x2: float, y2: float) -> tuple[float, float]: 
    '''
    x1: x position (float)
    y1: y position (float)
    x2: x position (float)
    y2: y position (float)
    ----------------------------------------------------------------
    Calculate the distence between two objects.
    return -> tuple[float, float]: distance, radians
    '''
    dx = x1 - x2
    dy = y1 - y2
    return (dx**2 + dy**2)**0.5, math.atan2(dy,dx)