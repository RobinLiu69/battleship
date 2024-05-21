import pygame


class Boards(): 
    def __init__(self, width: int, height: int, rx: int, ry: int, x: int, y: int, team: str) -> None: 
        '''
        width: board width (int)
        height: board height (int)
        rx: x position (int)
        ry: y position (int)
        x: board x position (int)
        y: board y position (int)
        team: board team (str: blue, red)
        ----------------------------------------------------------------
        Initialize board.
        return -> None
        '''
        self.width = width
        self.height = height
        self.rx = rx
        self.ry = ry
        self.x = x
        self.y = y
        self.team = team
        self.color = ()
        self.able = True
        if self.team == "red": self.color = (40, 10, 10)
        elif self.team == "blue": self.color = (10, 10, 40)
        else: self.color = (25, 25, 25)

    def display(self, screen: pygame.Surface, width: int, team: str=None) -> None: 
        '''
        screen: surface to display on (pygame.Surface)
        width: width of board lines (int)
        team: board team (str: blue, red)
        ----------------------------------------------------------------
        display board.
        return -> None
        '''
        if self.team == "red": self.color = (100, 10, 10)
        elif self.team == "blue": self.color = (10, 10, 100)
        pygame.draw.rect(screen, self.color, (self.rx, self.ry, self.width, self.height), width)
        return None
    
    def update(self, screen: pygame.Surface, lineswidth: int, team: str = None) -> None: 
        '''
        screen: surface to display on (pygame.Surface)
        lineswidth: width of ship's lines (int)
        team: board team (str: blue, red)
        ----------------------------------------------------------------
        update board.
        return -> None
        '''
        if team != None: self.team = team
        self.display(screen, lineswidth)
        # self.check_ship(Shiplist)
        return None
        

        
    def check_win(self) -> int:
        '''
        Check if the red team win.
        return -> int: if self team is red return 1, if blue return 0
        '''
        if self.team == "red": return 1
        elif self.team == "blue": return 0