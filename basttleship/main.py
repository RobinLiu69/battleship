import pygame, math
import shipClass as sC
import boardClass as bC
import windowClass as wC
from formula import *

def change_turn(who: str, Shiplist: list[sC.Ships], move_counter: int, Board_size: int, money: tuple[int, int]) -> tuple[str, int]: 
    '''
    who: red or blue (str)
    Shiplist: Ship list with ships in it (list)
    move_counter: how many events are running (int)
    Board_size: board size (int)
    money: red and blue team's money (red, blue) (tuple[int, int])
    ----------------------------------------------------------------
    End the turn.
    return -> str
    '''
    if who == "red": 
        for ship in Shiplist: 
            if ship.team == "red":
                ship.end_turn(Shiplist)
            elif ship.team == "blue": 
                move_counter = ship.start_turn(Shiplist, move_counter, Board_size, money)
        return "blue", move_counter
    elif who == "blue": 
        for ship in Shiplist: 
            if ship.team == "blue": 
                ship.end_turn(Shiplist)
            elif ship.team == "red": 
                move_counter = ship.start_turn(Shiplist, move_counter, Board_size, money)
        return "red", move_counter

def win_check(Board: list[bC.Boards], Shiplist: list[sC.Ships]) -> bool:
    '''
    Board: list of boards (list[Boards])
    Shiplist: list of ships (list[Ships])
    ----------------------------------------------------------------
    Check if ship is on the board.
    return -> bool
    '''
    counter = 0
    for index, board in enumerate(Board): 
        counter += board.check_win()
    if counter == 35:
        print(f"red win")
        return False
    
    for index, ship in enumerate(Shiplist):
        if ship.name == "Mothership":
            return True
    print(f"blue win")
    return False

def check_ship(self: bC.Boards, Shiplist: list[sC.Ships]) -> None:
    '''
    Shiplist: list of ships (list[Ships])
    ----------------------------------------------------------------
    Check if ship is on the board.
    return -> None
    '''
    for ship in Shiplist:
        if ship.name == "Mothership":
                if self.x <= ship.x:
                    self.team = "red"
                else:
                    self.team = "blue"
                    
    for ship in Shiplist:
        if ship.x >= 0 and ship.x == self.x and ship.y >= 0 and ship.y == self.y:
            self.able = False
            return
    self.able = True

def display_num(screen: pygame.Surface, font: tuple[pygame.font.Font], screen_width: int = 0, screen_height: int = 0, Board_size: int = 0, money: tuple[int, int] = ()) -> None:
    '''
    screen: surface to display on (pygame.Surface)
    font: text font (tuple[pygame.font.Font])
    screen_width: width of screen (int)
    screen_height: height of screen (int)
    Board_size: board size (int)
    ----------------------------------------------------------------
    Display text.
    return -> None
    '''
    draw_text(screen, f"Money red: {money[0]}", (200, 200, 50), font[1], ((screen_width/2-Board_size*3.5)+(-1.5*Board_size)+(Board_size*0.1), (screen_height/2-Board_size*2.5)+(5*Board_size)+(Board_size*0.5)))
    draw_text(screen, f"Money blue: {money[1]}", (200, 200, 50), font[1], ((screen_width/2-Board_size*3.5)+(7*Board_size)+(Board_size*0.1), (screen_height/2-Board_size*2.5)+(5*Board_size)+(Board_size*0.5)))
        



    
def main() -> int: 
    pygame.init()
    Board: list[bC.Boards] = []
    Shiplist: list[sC.Ships] = []
    screen = wC.Screen()
    Board_height = 5
    Board_width = 7
    Board_size = round(screen.width/12.5)
    move_counter = 0
    
    running = True
    clock = pygame.time.Clock()
    for i in range(Board_height): 
        for j in range(Board_width): 
            Board.append(bC.Boards(Board_size, Board_size, screen.width/2+(j-3.5)*Board_size, screen.height/2+(i-2.5)*Board_size, j, i, "None"))
    
    # Shiplist.append(sC.Rusher(x=1, engine_name="combustion_engine", gadget_name="lighter"))
    # Shiplist.append(sC.Hagird(x=2, engine_name="imperial_engine", gadget_name="peace_badge"))
    Shiplist.append(sC.Mothership(y=1, engine_name="old_engine", gadget_name="peace_badge"))
    # Shiplist.append(sC.Tower(x=5, engine_name="stable_engine", gadget_name="hacker_plugin"))
    # Shiplist.append(sC.Turret(x=6, engine_name="combustion_engine", gadget_name="lighter"))
    Shiplist.append(sC.Hagird(x=-1, engine_name="combustion_engine", gadget_name="lighter", exhibit=True))
    Shiplist.append(sC.Rusher(x=-1, y=1, engine_name="combustion_engine", gadget_name="lighter", exhibit=True))
    Shiplist.append(sC.Killer(x=-1, y=2, engine_name="imperial_engine", gadget_name="lighter", exhibit=True))
    Shiplist.append(sC.Supply_ship(x=-1, y=3, engine_name="stable_engine", gadget_name="peace_badge", exhibit=True))
    Shiplist.append(sC.Escort(x=-1, y=4, engine_name="combustion_engine", gadget_name="peace_badge", exhibit=True))
    Shiplist.append(sC.Tower(x=8, engine_name="stable_engine", gadget_name="peace_badge", exhibit=True))
    Shiplist.append(sC.Turret(x=8, y=1, engine_name="combustion_engine", gadget_name="lighter", exhibit=True))
    Shiplist.append(sC.Fortress(x=8, y=2, engine_name="stable_engine", gadget_name="lighter", exhibit=True))
    # Shiplist.append(sC.Headquarters(x=8, y=3, engine_name="stable_engine", gadget_name="spiked_bow", exhibit=True))
    Shiplist.append(sC.Supply_depot(x=8, y=4, engine_name="stable_engine", gadget_name="peace_badge", exhibit=True))
    
    pressing = 0
    who = "red"
    tick = 0
    click_mouse_pos = None
    money = [200, 200]
    
    while running:
        tick += 1
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT: 
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                click_mouse_pos = event.pos
                
            elif event.type == pygame.MOUSEBUTTONUP:
                click_mouse_pos = None
                    
                
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            running = False
        screen.window.fill((0, 0, 0))
        display_num(screen.window, screen.font, screen.width, screen.height, Board_size, money)
            
        if tick % 60 == 0:
            tick = 0
            print(f"move_counter {move_counter}")
        
        if keys[pygame.K_e] and pressing == 0 and move_counter == 0:
            print("end turn")
            who, move_counter = change_turn(who, Shiplist, move_counter, Board_size, money)
            pressing += 1
        elif pressing > 0 and not keys[pygame.K_e]: 
            pressing = 0
            
        mousepos = pygame.mouse.get_pos()
        Bx, By = math.floor((mousepos[0]-(screen.width/2-Board_size*3.5))/Board_size), math.floor((mousepos[1]-(screen.height/2-Board_size*2.5))/Board_size)
        
        if keys[pygame.K_s] and pressing == 0:
            Shiplist.append(sC.Rusher(x=Bx, y=By, engine_name="combustion_engine", gadget_name="lighter"))
        elif pressing > 0 and keys[pygame.K_s]:
            pressing = 0
        
        
        for index, board in enumerate(Board): 
            board.update(screen.window, screen.lines_width, None)
            check_ship(board, Shiplist)

        
        for index, ship in enumerate(Shiplist): 
            move_counter, money = ship.update(screen.window, Shiplist, screen.lines_width, screen.width, screen.height, Board_size, Board, screen.font, mousepos, move_counter, click_mouse_pos, money, who)    

        running = win_check(Board, Shiplist)
        
        pygame.display.flip()
        clock.tick(60)

    return 0



if __name__ == '__main__': 
    main()