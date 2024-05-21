import pygame, random, math, copy, boardClass
import pygame.gfxdraw
from formula import *

class Ships(): 
    def __init__(self, Name: str, chinese_name: str, HP: int, DAM: int, x: int, y: int, atktype: int, team: str, move_step: int, gadget_name: str, engine_name: str, exhibit: bool = False) -> None: 
        '''
        Name: ship name (str)
        HP: ship health (int)
        DAM: ship damage (int)
        x: ship x position (int)
        y: ship y position (int)
        atktype: ship atk type(int): 1: None, 2: Surounded enemy, 3: Enemy who on the front two blocks (row)
                                     4: Same column enemy, 5: Same row and the nearest enemy, 6: The nearest enemy
                                     7: Surounded ships, 8: Surounded friendly ships, 9: Front enemy
        team: ship's team (str: blue, red)
        effect: ship effect (list[str])
        shield: ship shield (int)
        move_step: ship move_step (int)
        gadget_name: gadget name (str)\n
            點火器(lighter)(0/1)每次攻擊為對手附加一層"燃燒"\n
            鋼鐵裝甲(steel_armor)(6/0)無特殊效果\n
            和平徽章(peace_badge)(2/0)每己方回合結束 為周圍有方回復2點血\n
            尖刺船頭(spiked_bow)(1/1)若移動被阻擋 對阻擋者造成2點傷害\n
            駭客插件(hacker_plugin)(0/1)戰艦被擊毀 使攻擊者陷入癱瘓一回合\n
        engine_name: engine name (str)\n
            帝國引擎(imperial_engine)(3/1)每次攻擊成功 自身+1護盾/+1攻擊(25$)\n
            熱燃引擎(combustion_engine)(3/0)每次攻擊為對手附加一層"燃燒"(30$)\n
            光閃引擎(flash_engine)(3/0)移動一次(30$)\n
            穩定引擎(stable_engine)(5/0)每己方回合結束 獲得2護盾(30$)\n
            老舊引擎(old_engine)(4/0)放置的前兩回合無法移動 若移動被阻擋 損失一半血量並對阻擋者造成損失血量之傷害(若為母艦 僅會損失1/5血量)(25$)\n
        wxhibit: Display or not (bool)
        ----------------------------------------------------------------
        Initialize ship.
        return -> None
        '''
        self.name = Name
        self.chinese_name = chinese_name
        self.hp = HP
        self.dam = DAM
        self.x = x
        self.y = y
        self.rx = 0
        self.ry = 0
        self.xv = 0
        self.yv = 0
        self.atktype = atktype
        self.team = team
        self.die_to: "Ships" = None
        self.bullets: list[bullets] = []
        self.shadow_ship = None
        self.exhibit = exhibit
        self.effect = []
        self.shield = 0
        self.parent: "Ships" = None
        self.move_step = move_step
        try: 
            self.engine_name = engine_name
            self.engine = equipments(engine_name=self.engine_name).engine
            self.chinese_engine_name = self.engine.chinese_name
            self.hp, self.dam = self.engine.basic(self.hp, self.dam)
            self.color = self.engine.color
            self.gadget_name = gadget_name
            self.gadget = equipments(gadget_name=self.gadget_name).gadget
            self.chinese_gadget_name = self.gadget.chinese_name
            self.hp, self.dam = self.gadget.basic(self.hp, self.dam)
        except Exception as e: 
            print(f"ship initalization failed -> {e}")
            self.color = (200, 200, 200)
            self.gadget = None
            self.engine = None
        
        self.maxhp = self.hp
        self.d_hp = self.hp
        self.d_dam = self.dam
        self.d_shield = self.shield
        self.update_values()
    
        if self.exhibit: 
            self.price = self.spawncheck(engine_name=self.engine_name)
    
    def start_turn(self, Shiplist: list["Ships"], event_counter: int, Board_size: int, money: tuple[int, int]) -> int: 
        '''
        Shiplist: list of ships (list[Ships])
        event_counter: how many moves are running (int)
        Board_size: board size (int)
        money: red and blue team's money (red, blue) (tuple[int, int])
        ----------------------------------------------------------------
        Call at start turn.
        return -> int
        '''
        if self.exhibit: return event_counter
        try: 
            self.gadget.ability("start_turn", self, Shiplist)
        except Exception as e: 
            print(f"failed to load gadget ability -> {e}")
        try: 
            self.engine.ability("start_turn", self, Shiplist)
        except Exception as e:
            print(f"failed to load engine ability -> {e}")
        
        if self.team == "red":
            if self.name == "Supply_ship":
                money[0] += 40
        if self.team == "blue":
            if self.name == "Supply_depot":
                money[1] += 40
        
        if "stun" not in self.effect: 
            self.affect(Shiplist)
            event_counter += self.move(Shiplist)
            if self.xv == 0 and self.yv == 0:
                temp1, temp2 = self.attack(Shiplist, Board_size, event_counter)
                event_counter = temp2
                if temp1:
                    print(f"{self.name} attack successful")
                    try: 
                        self.gadget.ability("atk_succeed", self, Shiplist)
                    except Exception as e: 
                        print(f"failed to load gadget ability -> {e}")
                    try: 
                        self.engine.ability("atk_succeed", self, Shiplist)
                    except Exception as e: 
                        print(f"failed to load engine ability -> {e}")
        else: 
            self.affect(Shiplist)
        
        return event_counter
    
    def end_turn(self, Shiplist: list["Ships"]) -> None: 
        '''
        Shiplist: list of ships (list[Ships])\n
        ----------------------------------------------------------------
        Call at end turn.
        return -> int
        '''
        if self.exhibit: return
        try:
            self.gadget.ability("end_turn", self, Shiplist)
        except Exception as e: 
            print(f"failed to load gadget ability -> {e}")
        try: 
            self.engine.ability("end_turn", self, Shiplist)
        except Exception as e: 
            print(f"failed to load engine ability -> {e}")
        
    def move_end(self, Shiplist: list["Ships"], Board_size: int, event_counter: int) -> int: 
        '''
        Shiplist: list of ships (list[Ships])
        Board_size: board size (int)
        event_counter: how many moves are running (int)
        ----------------------------------------------------------------
        Call when move ends.
        return -> int
        '''
        temp1, temp2 = self.attack(Shiplist, Board_size, event_counter)
        event_counter = temp2
        if temp1:
            print(f"{self.name} attack successful")
            try: 
                self.gadget.ability("atk_succeed", self, Shiplist)
            except Exception as e: 
                print(f"failed to load gadget ability -> {e}")
            try: 
                self.engine.ability("atk_succeed", self, Shiplist)
            except Exception as e: 
                print(f"failed to load engine ability -> {e}")
        return event_counter
    
    def update(self, screen: pygame.Surface, Shiplist: list["Ships"], lines_width: int, screen_width: int = 0, screen_height: int = 0, Board_size: int = 0, Board: list[boardClass.Boards] = [], font: tuple[pygame.font.Font] = (), mousepos: tuple[int, int] = (), event_counter: int = 0, click_mouse_pos: tuple[int, int] = None, money: tuple[int, int] = None, who: str = None) -> tuple[int, int]: 
        '''
        screen: surface to display on (pygame.Surface)
        Shiplist: list of ships (list[Ships])
        lines_width: width of ship's lines (int)
        screen_width: width of screen (int)
        screen_height: height of screen (int)
        Board_size: board size (int)
        Board: list of board (list[bC.Boards])
        font: text font (tuple[pygame.font.Font])
        mousepos: mouse position (tuple[int, int])
        event_counter: how many moves are running (int)
        click_mouse_pos: click mouse position (tuple[int, int])
        money: red and blue team's money (red, blue) (tuple[int, int])
        who: red or blue (str)
        ----------------------------------------------------------------
        Update ship status.
        return -> int
        '''
        for bullet in self.bullets:
            event_counter = bullet.update(screen, lines_width, screen_width, screen_height, Board_size, event_counter=event_counter)
            if not bullet.alive:
                self.bullets.remove(bullet)
                
        self.rx, self.ry = (screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.5), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.5)
        
        if self.shadow_ship == 1:
            self.x, self.y = ((mousepos[0]-(screen_width/2-Board_size*3))/Board_size), ((mousepos[1]-(screen_height/2-Board_size*2))/Board_size)
            print(self.x, self.y)
            for board in Board:
                if math.floor(self.x+0.5) == board.x and math.floor(self.y+0.5) == board.y:
                    if not board.able: break
                    if board.team == "red":
                        if self.team == "red":
                            if click_mouse_pos != None and self.x > -0.5 and self.x < 6.5 and self.y > -0.5 and self.y < 5.5:
                                self.shadow(Shiplist, mousepos, screen_width, screen_height, Board_size)
                    elif board.team == "blue":
                        if self.team == "blue":
                            if click_mouse_pos != None and self.x > -0.5 and self.x < 6.5 and self.y > -0.5 and self.y < 5.5:
                                self.shadow(Shiplist, mousepos, screen_width, screen_height, Board_size)
            
        self.shapes(screen_width, screen_height, Board_size)
        self.display(screen, lines_width, screen_width, screen_height, Board_size, font)
        if self.shadow_ship == 1: return event_counter, money
        
        if not self.check_die(Shiplist):
            event_counter += self.event_clear()

        temp = self.movement(Board_size)
        
        if temp == -1:
            event_counter += -1
            event_counter = self.move_end(Shiplist, Board_size, event_counter)
            
            
        if self.touch(mousepos, screen_width, screen_height, Board_size):
            if click_mouse_pos != None:
                if self.exhibit and self.touch(click_mouse_pos, screen_width, screen_height, Board_size):
                    for ship in Shiplist:
                        if ship.shadow_ship != None and ship.shadow_ship != 0:
                            return event_counter, money
                    if self.shadow_ship == None:
                        click_mouse_pos = None
                        if self.team == "red" and who == "red" and event_counter == 0:
                            if money[0] >= self.price:
                                money[0] -= self.price
                                self.shadow(Shiplist, mousepos, screen_width, screen_height, Board_size)
                        if self.team == "blue" and who == "blue" and event_counter == 0:
                            if money[1] >= self.price:
                                money[1] -= self.price
                                self.shadow(Shiplist, mousepos, screen_width, screen_height, Board_size)
                
        if self.shadow_ship != None and self.shadow_ship != 1 and self.shadow_ship!= 0:
            _, money = self.shadow_ship.update(screen, Shiplist, lines_width, screen_width, screen_height, Board_size, Board, font, mousepos, click_mouse_pos=click_mouse_pos, money=money)
        
        return event_counter, money
    
    def shadow(self, Shiplist: list["Ships"], mousepos: tuple[int, int], screen_width: int = 0, screen_height: int = 0, Board_size: int = 0) -> None:
        '''
        Shiplist: list of ships (list[Ships])
        mousepos: mouse position (tuple[int, int])
        screen_width: width of screen (int)
        screen_height: height of screen (int)
        Board_size: board size (int)
        ----------------------------------------------------------------
        deep copy self.
        return -> None
        '''
        if self.shadow_ship == None:
            self.shadow_ship = copy.deepcopy(self)
            self.shadow_ship.shadow_ship = 1
            self.shadow_ship.parent = self
        elif self.shadow_ship == 1:
            temp = copy.deepcopy(self)
            temp.shadow_ship = 0
            temp.exhibit = False
            temp.x, temp.y = math.floor((mousepos[0]-(screen_width/2-Board_size*3.5))/Board_size), math.floor((mousepos[1]-(screen_height/2-Board_size*2.5))/Board_size)
            Shiplist.append(temp)
            self.parent.shadow_ship = None
            self = 0
        
    def event_clear(self) -> int:
        '''
        Chack when you die how many event are on you.
        return -> int
        '''
        event_counter = 0
        if self.xv > 0 or self.yv > 0:
            event_counter -= 1
        event_counter -= len(self.bullets)

        return event_counter
        
    def shoot(self, target: "Ships", Board_size: int, dam: int) -> bool:
        '''
        target: target to shoot at (Ships)
        Board_size: board size (int)
        dam: how mant damage to shoot (int)
        ----------------------------------------------------------------
        Shoot a bullet to the target.
        return -> bool
        '''
        color = (255, 255, 255)
        if self.team == "red": color = (200, 50, 50)
        if self.team == "blue": color = (50, 50, 200)
        self.bullets.append(bullets(self.rx, self.ry, target, color, 0, random.randint(round(-Board_size*0.2), round(Board_size*0.2)), dam))

        
    def movement(self, Board_size: int) -> int: 
        '''
        Board_size: board size (int)\n
        ----------------------------------------------------------------
        Animate ship movement.
        return -> int
        '''
        if abs(self.xv)*Board_size > Board_size*0.05: 
            self.x += Board_size*0.0001
            self.xv -= Board_size*0.0001
        elif abs(self.yv)*Board_size > Board_size*0.05: 
            self.y += Board_size*0.0001
            self.yv -= Board_size*0.0001
        if abs(self.yv)*Board_size < Board_size*0.05 and self.yv != 0: 
            self.y = math.ceil(self.y)
            self.yv = 0
            if self.yv == 0 and self.xv == 0:
                return -1
        if abs(self.xv)*Board_size < Board_size*0.05 and self.xv != 0: 
            self.x = math.ceil(self.x)
            self.xv = 0
            if self.yv == 0 and self.xv == 0: 
                return -1
        return 0
        
    def touch(self, mousepos: tuple[int, int], screen_width: int = 0, screen_height: int = 0, Board_size: int = 0) -> bool: 
        '''
        mousepos: mouse position (tuple[int, int])
        screen_width: width of screen (int)
        screen_height: height of screen (int)
        Board_size: board size (int)
        ----------------------------------------------------------------
        Check whether mouse is on the ship's block.
        return -> bool
        '''
        return math.floor((mousepos[0]-(screen_width/2-Board_size*3.5))/Board_size) == self.x and math.floor((mousepos[1]-(screen_height/2-Board_size*2.5))/Board_size) == self.y
    
    def shapes(self, screen_width: int = 0, screen_height: int = 0, Board_size: int = 0): 
        '''
        screen_width: width of screen (int)
        screen_height: height of screen (int)
        Board_size: board size (int)
        ----------------------------------------------------------------
        Update ship shape.
        return -> None
        '''
        if self.name == "Mothership": 
            self.shape = (((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.3), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.2)),
                        ((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.15), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.35)),
                        ((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.15), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.65)),
                        ((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.3), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.8)),
                        ((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.75), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.6)),
                        ((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.75), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.4))
                        )
        elif self.name == "Hagird": 
            self.shape = "circle"
        elif self.name == "Rusher": 
            self.shape = (((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.75), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.5)),
                          ((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.3), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.75)),
                          ((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.3), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.25)),
                          )
        elif self.name == "Escort": 
            self.shape = (((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.7), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.2)),
                          ((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.3), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.2)),
                          ((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.3), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.8)),
                          ((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.7), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.8)),
                          )
        elif self.name == "Supply_ship": 
            self.shape = (((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.7), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.5)),
                          ((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.5), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.2)),
                          ((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.3), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.5)),
                          ((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.5), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.8))
                          )
        elif self.name == "Killer": 
            self.shape = (((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.7), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.4)),
                          ((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.3), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.25)),
                          ((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.3), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.75)),
                          ((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.7), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.6))
                          )
        elif self.name == "Tower": 
            self.shape = (((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.8), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.2)),
                          ((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.2), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.2)),
                          ((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.2), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.8)),
                          ((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.8), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.8))
                          )
        elif self.name == "Turret": 
            self.shape = "big_circle"
        elif self.name == "Fortress": 
            self.shape = (((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.5), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.25)),
                          ((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.2), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.75)),
                          ((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.8), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.75)),
                          )
        elif self.name == "Headquarters": 
            self.shape = (((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.5), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.2)),
                          ((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.175), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.45)),
                          ((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.325), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.8)),
                          ((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.675), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.8)),
                          ((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.825), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.45)),
                          )
        elif self.name == "Supply_depot": 
            self.shape = (((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.3), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.3)),
                          ((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.3), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.7)),
                          ((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.7), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.7)),
                          ((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.7), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.3)),
                          )
    
    def display(self, screen: pygame.Surface, lines_width: int, screen_width: int = 0, screen_height: int = 0, Board_size: int = 0, font: tuple[pygame.font.Font] = ()) -> None:
        '''
        screen: surface to display on (pygame.Surface)
        lines_width: width of ship's lines (int)
        screen_width: width of screen (int)
        screen_height: height of screen (int)
        Board_size: board size (int)
        font: text font (tuple[pygame.font.Font])
        ----------------------------------------------------------------
        Display ship.
        return -> None
        '''
        if type(self.shape) != str: 
            pygame.draw.lines(screen, self.color, True, self.shape, round(lines_width*1.5))
        if self.shape == "circle": 
            pygame.draw.circle(screen, self.color, ((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.5), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.5)), (Board_size*0.25), round(lines_width*1.5))
        elif self.shape == "big_circle": 
            pygame.draw.circle(screen, self.color, ((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.5), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.5)), (Board_size*0.35), round(lines_width*1.5))

        try: 
            if self.gadget != None: 
                self.gadget.display(screen, lines_width, screen_width, screen_height, Board_size, self.x, self.y, self.team)
        except Exception as e: 
            print(f"failed to display gaget -> {e}")
            
        if self.shadow_ship != 1:
            self.num_display(screen, font, screen_width, screen_height, Board_size)
        
    def num_display(self, screen: pygame.Surface, font: tuple[pygame.font.Font], screen_width: int = 0, screen_height: int = 0, Board_size: int = 0) -> None: 
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
        draw_text(screen, f"HP: {self.d_hp}", (200, 200, 200), font[0], ((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.1), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.07)))
        # draw_text(screen, f"RHP: {self.hp}", (200, 200, 200), font[0], ((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.1), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*-0.1)))
        draw_text(screen, f"DAM: {self.d_dam}", (200, 200, 200), font[0], ((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*(11-len(f"DAM: {self.d_dam}"))/10), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.07)))
        if self.d_shield > 0:
            draw_text(screen, f"SHIELD: {self.d_shield}", (200, 200, 200), font[0], ((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.1), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.17)))
        
        if "stun" in self.effect: 
            stun_count = self.effect.count("stun")
            draw_text(screen, f"stun*{stun_count}", (200, 200, 200), font[0], ((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.5), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.9)))
        
        if "fire" in self.effect: 
            fire_count = self.effect.count("fire")
            if fire_count > 5: fire_count = 5
            draw_text(screen, f"fire*{fire_count}", (200, 50, 50), font[0], ((screen_width/2-Board_size*3.5)+(self.x*Board_size)+(Board_size*0.5), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.75)))
        
        if self.exhibit: 
            draw_text(screen, f"${self.price}", (200, 200, 200), font[1], ((screen_width/2-Board_size*3.5)+((self.x-0.75)*Board_size)+(Board_size*0.1), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.05)))
            draw_text(screen, f"{self.chinese_name}", (200, 200, 200), font[1], ((screen_width/2-Board_size*3.5)+((self.x-0.75)*Board_size)+(Board_size*0.1), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.3)))
            draw_text(screen, f"{self.chinese_gadget_name}", (200, 200, 200), font[1], ((screen_width/2-Board_size*3.5)+((self.x-0.75)*Board_size)+(Board_size*0.1), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.5)))
            draw_text(screen, f"{self.chinese_engine_name}", (200, 200, 200), font[1], ((screen_width/2-Board_size*3.5)+((self.x-0.75)*Board_size)+(Board_size*0.1), (screen_height/2-Board_size*2.5)+(self.y*Board_size)+(Board_size*0.7)))
        
    
    def affect(self, Shiplist: list["Ships"]) -> None: 
        '''
        Shiplist: list of ships (list[Ships])\n
        ----------------------------------------------------------------
        Caculate the effect.
        return -> None
        '''
        fire_count = self.effect.count("fire")
        for i in range(5, fire_count): 
            self.effect.remove("fire")
            fire_count = 5
        if fire_count > 0:
            self.damage("fire", Shiplist, fire_count)
            self.update_values()
            if self.hp <= 0: self.die_to = self
            print(f"{self}, fire count: {fire_count}")
            if fire_count > 4:
                ships: list["Ships"] = self.detect(Shiplist, 7)
                print(f"ships: {self.detect(Shiplist, 7)}")
                for ship in ships:
                    ship.effect.append("fire")
                print("fire spread")
        if "stun" in self.effect: 
            self.effect.remove("stun")    
    
    def detect(self, Shiplist: list["Ships"], atktype: int = 1) -> list["Ships"]: 
        '''
        Shiplist: list of ships (list[Ships])
        atktype: ship atk type(int): 1: None, 2: Surounded enemy, 3: Enemy who on the front two blocks (row)
                                     4: Same column enemy, 5: Same row and the nearest enemy, 6: The nearest enemy
                                     7: Surounded ships, 8: Surounded friendly ships, 9: Front enemy
        ----------------------------------------------------------------
        Detect whether ships are in the self's attack area.
        return -> list[Ships]: a list of ships which are in the attack area. (if no, empty list is returned.
        '''
        if atktype == 1: atktype = self.atktype
        if atktype == 1: 
            attacklist = []
        elif atktype == 2: 
            attacklist = []
            for ship in Shiplist:
                if ship.exhibit: continue
                if ship.team != self.team: 
                    if abs(self.x-ship.x) < 2 and abs(self.y-ship.y) < 2:
                        attacklist.append(ship)
        elif atktype == 3:
            attacklist = []
            for ship in Shiplist:
                if ship.exhibit: continue
                if ship.team != self.team: 
                    if ship.x < self.x + 3 and ship.x > self.x and ship.y == self.y:
                        attacklist.append(ship)
        elif atktype == 4: 
            attacklist = []
            for ship in Shiplist: 
                if ship.exhibit: continue
                if ship.team != self.team: 
                    if ship.x == self.x: 
                        attacklist.append(ship)
        elif atktype == 5: 
            attacklist = []
            nearest = []
            for ship in Shiplist:
                if ship.exhibit: continue
                if ship.team != self.team: 
                    if len(nearest) == 0 and ship.y == self.y:
                        nearest = [ship]
                    elif len(nearest) > 0:
                        if abs(ship.x - self.x) < abs(nearest[0].x - self.x) and ship.y == self.y:
                            nearest = [ship]
                        elif abs(ship.x - self.x) == abs(nearest[0].x - self.x) and ship.y == self.y: 
                            nearest.append(ship)
            print(nearest)
            attacklist = nearest
        elif atktype == 6: 
            attacklist = []
            nearest = []
            for ship in Shiplist:
                if ship.exhibit: continue
                if ship.team != self.team: 
                    if len(nearest) == 0: 
                        nearest = [ship]
                    else: 
                        if abs(ship.x - self.x) + abs(ship.y - self.y) < abs(nearest[0].y - self.y) + abs(nearest[0].x - self.x): 
                            nearest[0] = ship
                        elif abs(ship.x - self.x) + abs(ship.y - self.y) == abs(nearest[0].y - self.y) + abs(nearest[0].x - self.x): 
                            nearest.append(ship)
            if len(nearest) != 0: attacklist.append(random.choice(nearest))
        elif atktype == 7: 
            print("surrounding")
            attacklist = []
            for ship in Shiplist:
                if ship.exhibit: continue
                if abs(self.x-ship.x) < 2 and abs(self.y-ship.y) < 2: 
                    attacklist.append(ship)
        elif atktype == 8: 
            attacklist = []
            for ship in Shiplist:
                if ship.exhibit: continue
                if ship.team == self.team: 
                    if abs(self.x-ship.x) < 2 and abs(self.y-ship.y) < 2: 
                        attacklist.append(ship)
        elif atktype == 9: 
            attacklist = []
            for ship in Shiplist:
                if ship.exhibit: continue
                if ship.team != self.team: 
                    if abs(self.x-ship.x) < 2 and abs(self.y-ship.y) < 2: 
                        attacklist.append(ship)
                        break
        return attacklist

    def beenattack(self, atker: "Ships") -> None: 
        pass
    
    def kill(self, who: "Ships") -> None: 
        pass
    
    def die(self, Shiplist: list["Ships"], who: "Ships") -> None: 
        '''
        Shiplist: list of ships (list[Ships])\n
        who: who killed self (Ships)\n
        ----------------------------------------------------------------
        The methods will remove the ship from the Shiplist list,
        and delete the ship it self.
        return -> None
        '''
        if who != None:
            try: 
                self.gadget.ability("been_killed", self, Shiplist, who)
            except Exception as e: 
                print(f"failed to load gadget ability -> {e}")
            try: 
                self.engine.ability("been_killed", self, Shiplist, who)
            except Exception as e: 
                print(f"failed to load engine ability -> {e}")
        Shiplist.remove(self)
        return None
        
    def heal(self, value: int = 0) -> bool:
        '''
        value: healing value (int)\n
        ----------------------------------------------------------------
        The methods will heal the ship.
        return -> bool
        '''
        if self.maxhp <= self.hp + value:
            self.hp = self.maxhp
            self.update_values()
            return True
        elif self.maxhp > self.hp + value: 
            self.hp += value
            self.update_values()
            return True
        return False

    def check_die(self, Shiplist: list["Ships"]) -> bool:
        '''
        Shiplist: list of ships (list[Ships])\n
        ----------------------------------------------------------------
        The methods will check whether the ship is die.
        return -> bool: True if ship is alive, False otherwise.
        '''
        if self.d_hp <= 0:
            if self.die_to != None and type(self.die_to) != str:
                self.die_to.kill(self)
            self.die(Shiplist, self.die_to)
            return False
        return True

    def update_values(self) -> None:
        '''
        Update the display values(d_hp, d_dam, d_shield).
        return -> None
        '''
        self.d_hp = self.hp
        self.d_dam = self.dam
        self.d_shield = self.shield
        

    def damage(self, atker: "Ships" = None, Shiplist: list["Ships"] = [], value: int = 0) -> bool: 
        '''
        atker: who deals damage to self (Ships)
        Shiplist: list of ships (list[Ships])
        value: damage value (int)
        ----------------------------------------------------------------
        Deal damage to self, value depends on the attacker's damage value,
        if self has shield, the damage will be calculated based on how many shield it has.
        return -> bool
        '''
        if value == 0 and atker == None: return False
        if value == 0: value = atker.dam
        if self.shield > 0: 
            print("have shield")
            self.shield -= value
            if self.shield < 0: 
                value = -self.shield
                self.shield = 0
            elif self.shield >= 0: 
                value = 0
        
        print(f"value:{value}")
        self.hp -= value
        print(f"self.hp= {self.hp}")
        if self.hp <= 0: 
            self.hp = 0
            self.die_to = atker
        return True
        
    def attack(self, Shiplist: list["Ships"], Board_size: int, event_counter: int) -> tuple[bool, int]: 
        '''
        Shiplist: list of ships (list[Ships])
        Board_size: board size (int)
        event_counter: how many moves are running (int)
        ----------------------------------------------------------------
        The methods will detect whether there are ships in it attack area and call damage methods to deal damage.
        return -> bool: if detect return a none empty list the attack will be calculated. (True)
                         Otherwise the attack will be ingored. (False)
        
        '''
        attacklist: list[Ships] = self.detect(Shiplist, self.atktype)
        if len(attacklist) == 0: return False, event_counter
        for index, ship in enumerate(reversed(attacklist)):
            
            if ship.damage(self, Shiplist):
                self.shoot(ship, Board_size, self.dam)
                event_counter += 1
                try: 
                    self.gadget.ability("atking_enemy", self, Shiplist, ship)
                except Exception as e: 
                    print(f"failed to load gadget ability -> {e}")
                try: 
                    self.engine.ability("atking_enemy", self, Shiplist, ship)
                except Exception as e:
                    print(f"failed to load engine ability -> {e}")
                attacklist.pop()
        if len(attacklist) == 0: return True, event_counter
        if len(attacklist) > 0: 
            print(f"Error: attachlist left from {self} -> {attacklist}")
            return False, event_counter

    def move(self, Shiplist: list["Ships"], step: int = 0) -> bool: 
        '''
        Shiplist: list of ships (list[Ships])\n
        ----------------------------------------------------------------
        move ship depends on ship's move_step.
        return -> bool: if move succesed. (True)
                         Otherwise move unsuccesed. (False)
        '''
        if self.move_step == 0: return False
        if step == 0: step = self.move_step
        if self.team == "red":
            if self.name == "Escort": 
                for ship in Shiplist: 
                    if ship.name == "Mothership": 
                        if self.x > ship.x: 
                            return False
            for step in range(step): 
                for ship in Shiplist: 
                    if (self.x + 1 == ship.x and self.y == ship.y) or self.x + 1 > 6: 
                        try: 
                            self.gadget.ability("failed_move", self, Shiplist, ship)
                        except Exception as e: 
                            print(f"failed to load gadget ability -> {e}")
                        try: 
                            self.engine.ability("failed_move", self, Shiplist, ship)
                        except Exception as e: 
                            print(f"failed to load engine ability -> {e}")
                        return False
                    elif self.x + self.xv + 1 == ship.x and self.y == ship.y: 
                        try:
                            self.gadget.ability("failed_move", self, Shiplist, ship)
                        except Exception as e: 
                            print(f"failed to load gadget ability -> {e}")
                        try: 
                            self.engine.ability("failed_move", self, Shiplist, ship)
                        except Exception as e: 
                            print(f"failed to load engine ability -> {e}")
                        return True
                    elif self.x + self.xv > 5:
                        return True
                self.xv += 1
        elif self.team == "blue":
            for step in range(step): 
                for ship in Shiplist: 
                    if (self.x + 1 == ship.x and self.y == ship.y) or self.x + 1 > 6: 
                        try: 
                            self.gadget.ability("failed_move", self, Shiplist, ship)
                        except Exception as e: 
                            print(f"failed to load gadget ability -> {e}")
                        try: 
                            self.engine.ability("failed_move", self, Shiplist, ship)
                        except Exception as e: 
                            print(f"failed to load engine ability -> {e}")
                        return False
                    elif self.x + self.xv + 1 == ship.x and self.y == ship.y: 
                        try:
                            self.gadget.ability("failed_move", self, Shiplist, ship)
                        except Exception as e: 
                            print(f"failed to load gadget ability -> {e}")
                        try: 
                            self.engine.ability("failed_move", self, Shiplist, ship)
                        except Exception as e: 
                            print(f"failed to load engine ability -> {e}")
                        return True
                    elif self.x + self.xv > 5:
                        return True
                self.xv -= 1
        return True
    
    def spawncheck(self, money: int = 0, engine_name: str = None) -> bool | int: 
        '''
        money: your money (int)
        engine_name: engine name (str)\n
            帝國引擎(imperial_engine)(3/1)每次攻擊成功 自身+1護盾/+1攻擊(25$)\n
            熱燃引擎(combustion_engine)(3/0)每次攻擊為對手附加一層"燃燒"(30$)\n
            光閃引擎(flash_engine)(3/0)移動一次(30$)\n
            穩定引擎(stable_engine)(5/0)每己方回合結束 獲得2護盾(30$)\n
            老舊引擎(old_engine)(4/0)放置的前兩回合無法移動 若移動被阻擋 損失一半血量並對阻擋者造成損失血量之傷害(若為母艦 僅會損失1/5血量)(25$)\n
        ----------------------------------------------------------------
        check if your money is enough to spawn the ship.
        return -> bool: by pass check. (True)
                         didn't by pass check. (False)
        '''
        try: 
            equipment = equipments(engine_name=engine_name)
            price = self.price + equipment.engine.price
            del equipment
        except Exception as e: 
            print(f"failed to calculate price -> {e}") 
            return False
        
        if self.exhibit: 
            return price
        return money >= price



class bullets():
    def __init__(self, x: float, y: float, target: Ships, color: tuple[int, int, int], xv: int = 0, yv:int = 0, dam:int = 0) -> None:
        '''
        x: x position (float)
        y: y position (float)
        target: target to shoot at (Ships)
        color: bullet color (tuple[int, int, int])
        dam: how many damage this bullet wiil does (int)
        ----------------------------------------------------------------
        Initialize bullet.
        return -> None
        '''
        self.target = target
        self.color = color
        self.x = x
        self.y = y
        self.xv = xv
        self.yv = yv
        self.alive = True
        self.dam = dam
        self.d = distence(self.x, self.y, self.target.rx, self.target.ry)[0]
    
    def update(self, screen: pygame.Surface, lines_width: int, screen_width: int = 0, screen_height: int = 0, Board_size: int = 0, font: tuple[pygame.font.Font] = (), mousepos: tuple[int, int] = (), event_counter: int = 0) -> int: 
        '''
        screen: surface to display on (pygame.Surface)
        lines_width: width of ship's lines (int)
        screen_width: width of screen (int)
        screen_height: height of screen (int)
        Board_size: board size (int)
        font: text font (tuple[pygame.font.Font])
        mousepos: mouse position (tuple[int, int])
        event_counter: how many moves are running (int)
        ----------------------------------------------------------------
        move the bullet.
        return -> int
        '''
        self.display(screen, lines_width, screen_width, screen_height, Board_size)
        event_counter += self.move(Board_size)
        return event_counter
        
    def display(self, screen: pygame.Surface, lines_width: int, screen_width: int = 0, screen_height: int = 0, Board_size: int = 0) -> None: 
        '''
        screen: surface to display on (pygame.Surface)
        lines_width: width of ship's lines (int)
        screen_width: width of screen (int)
        screen_height: height of screen (int)
        Board_size: board size (int)
        font: text font (tuple[pygame.font.Font])
        ----------------------------------------------------------------
        Display ship.
        return -> None
        '''
        pygame.draw.circle(screen, self.color, (self.x, self.y), (Board_size*0.075), round(lines_width*20))
        
    def move(self, Board_size:int) -> int:
        '''
        Board_size: board size (int)
        ----------------------------------------------------------------
        Update bullet.
        return -> int
        '''
        d, r = distence(self.x, self.y, self.target.rx, self.target.ry)
        xv, yv = one_direction_velocity_to_xy_velocity(Board_size*0.2, r*1.1+math.pi)
        self.xv += xv
        self.yv += yv
        self.x += xv + self.xv
        self.y += yv + self.yv
        if round(abs(self.x-self.target.rx)) < Board_size*0.1 and round(abs(self.y-self.target.ry)) < Board_size*0.3:
            self.target.d_hp -= self.dam
            self.alive = False
            return -1
        return 0
    

class Mothership(Ships): 
    price = 0
    def __init__(self, HP: int=40, DAM: int = 0, x: int = 0, y: int = 0, atktype: int=1, team: str="red", move_step: int=1, gadget_name: str = None, engine_name: str = None, exhibit: bool = False) -> None: 
        super().__init__(self.__class__.__name__, "母艦", HP, DAM, x, y, atktype, team, move_step, gadget_name, engine_name, exhibit)
        self.dam = 0
        self.update_values()
        
        
class Hagird(Ships): 
    price = 40
    def __init__(self, HP: int=6, DAM: int=4, x: int = 0, y: int = 0, atktype: int=2, team: str="red", move_step: int=1, gadget_name: str = None, engine_name: str = None, exhibit: bool = False) -> None: 
        super().__init__(self.__class__.__name__, "海格", HP, DAM, x, y, atktype, team, move_step, gadget_name, engine_name, exhibit)
        
        
class Rusher(Ships): 
    price = 40
    def __init__(self, HP: int=4, DAM: int=3, x: int = 0, y: int = 0, atktype: int=3, team: str="red", move_step: int=7, gadget_name: str = None, engine_name: str = None, exhibit: bool = False) -> None: 
        super().__init__(self.__class__.__name__, "衝鋒者", HP, DAM, x, y, atktype, team, move_step, gadget_name, engine_name, exhibit)
        
        
class Escort(Ships): 
    price = 40
    def __init__(self, HP: int=6, DAM: int=3, x: int = 0, y: int = 0, atktype: int=4, team: str="red", move_step: int=1, gadget_name: str = None, engine_name: str = None, exhibit: bool = False) -> None: 
        super().__init__(self.__class__.__name__, "護航艦", HP, DAM, x, y, atktype, team, move_step, gadget_name, engine_name, exhibit)
        
        
class Supply_ship(Ships): 
    price = 20
    def __init__(self, HP: int=5, DAM: int = 0, x: int = 0, y: int = 0, atktype: int=1, team: str="red", move_step: int = 0, gadget_name: str = None, engine_name: str = None, exhibit: bool = False) -> None: 
        super().__init__(self.__class__.__name__, "補給船", HP, DAM, x, y, atktype, team, move_step, gadget_name, engine_name, exhibit)
        
        
class Killer(Ships): 
    price = 40
    def __init__(self, HP: int=3, DAM: int=4, x: int = 0, y: int = 0, atktype: int=5, team: str="red", move_step: int = 0, gadget_name: str = None, engine_name: str = None, exhibit: bool = False) -> None: 
        super().__init__(self.__class__.__name__, "殺手", HP, DAM, x, y, atktype, team, move_step, gadget_name, engine_name, exhibit)
        
        
class Tower(Ships): 
    price = 40
    def __init__(self, HP: int=8, DAM: int = 0, x: int = 0, y: int = 0, atktype: int=1, team: str="blue", move_step: int = 0, gadget_name: str = None, engine_name: str = None, exhibit: bool = False) -> None: 
        super().__init__(self.__class__.__name__, "消撞塔", HP, DAM, x, y, atktype, team, move_step, gadget_name, engine_name, exhibit)


class Turret(Ships): 
    price = 40
    def __init__(self, HP: int=5, DAM: int=5, x: int = 0, y: int = 0, atktype: int=6, team: str="blue", move_step: int = 0, gadget_name: str = None, engine_name: str = None, exhibit: bool = False) -> None: 
        super().__init__(self.__class__.__name__, "炮塔", HP, DAM, x, y, atktype, team, move_step, gadget_name, engine_name, exhibit)


class Fortress(Ships): 
    price = 40
    def __init__(self, HP: int=7, DAM: int=4, x: int = 0, y: int = 0, atktype: int=2, team: str="blue", move_step: int = 0, gadget_name: str = None, engine_name: str = None, exhibit: bool = False) -> None: 
        super().__init__(self.__class__.__name__, "反擊堡壘", HP, DAM, x, y, atktype, team, move_step, gadget_name, engine_name, exhibit)
        

class Headquarters(Ships): 
    price = 40
    def __init__(self, HP: int=7, DAM: int = 0, x: int = 0, y: int = 0, atktype: int=1, team: str="blue", move_step: int = 0, gadget_name: str = None, engine_name: str = None, exhibit: bool = False) -> None: 
        super().__init__(self.__class__.__name__, "司令部", HP, DAM, x, y, atktype, team, move_step, gadget_name, engine_name, exhibit)


class Supply_depot(Ships): 
    price = 20
    def __init__(self, HP: int=7, DAM: int=0, x: int = 0, y: int = 0, atktype: int=1, team: str="blue", move_step: int = 0, gadget_name: str = None, engine_name: str = None, exhibit: bool = False) -> None: 
        super().__init__(self.__class__.__name__, "補給站", HP, DAM, x, y, atktype, team, move_step, gadget_name, engine_name, exhibit)
        
        
        










class equipments(): 
    def __init__(self, gadget_name: str = None, engine_name: str = None) -> None: 
        '''
        gadget_name: gadget name (str)\n
            點火器(lighter)(0/1)每次攻擊為對手附加一層"燃燒"\n
            鋼鐵裝甲(steel_armor)(6/0)無特殊效果\n
            和平徽章(peace_badge)(2/0)每己方回合結束 為周圍友方回復2點血\n
            尖刺船頭(spiked_bow)(1/1)若移動被阻擋 對阻擋者造成2點傷害\n
            駭客插件(hacker_plugin)(0/1)戰艦被擊毀 使攻擊者陷入癱瘓一回合\n
        engine_name: engine name (str)\n
            帝國引擎(imperial_engine)(3/1)每次攻擊成功 自身+1護盾/+1攻擊(25$)\n
            熱燃引擎(combustion_engine)(3/0)每次攻擊為對手附加一層"燃燒"(30$)\n
            光閃引擎(flash_engine)(3/0)移動一次(30$)\n
            穩定引擎(stable_engine)(5/0)每己方回合結束 獲得2護盾(30$)\n
            老舊引擎(old_engine)(4/0)放置的前兩回合無法移動 若移動被阻擋 損失一半(相對)血量並對阻擋者造成損失血量之傷害(若為母艦 僅會損失1/5血量)(25$)\n
        ----------------------------------------------------------------
        Initialize gadget.
        return -> None
        '''
        if gadget_name is not None: 
            self.gadget_name = gadget_name
            if self.gadget_name == "lighter": 
                self.gadget = lighter()
            elif self.gadget_name == "steel_armor": 
                self.gadget = steel_armor()
            elif self.gadget_name == "peace_badge": 
                self.gadget = peace_badge()
            elif self.gadget_name == "spiked_bow": 
                self.gadget = spiked_bow()
            elif self.gadget_name == "hacker_plugin": 
                self.gadget = hacker_plugin()
        
        elif engine_name is not None: 
            self.engine_name = engine_name
            if self.engine_name == "imperial_engine": 
                self.engine = imperial_engine()
            elif self.engine_name == "combustion_engine": 
                self.engine = combustion_engine()
            elif self.engine_name == "flash_engine": 
                self.engine = flash_engine()
            elif self.engine_name == "stable_engine": 
                self.engine = stable_engine()
            elif self.engine_name == "old_engine": 
                self.engine = old_engine()
        
class lighter(): 
    def __init__(self): 
        self.color = (150, 50, 50)
        self.chinese_name  ="點火器"
        
    def ability(self, state: str, selfship: "Ships", Shiplist: list["Ships"], enemy: "Ships" = None) -> list[str]: 
        '''
        state: calling state (str)\n 
            (sort by calling order)\n
            1.start_turn\n
            2.failed_move\n
            3.atking_enemy\n
            4.been_killed\n
            5.atk_succeed\n
            6.end_turn\n
        selfship: self ship (Ships)
        Shiplist: list of ships (list[Ships])
        enemy: enemy ship(Ships)
        ----------------------------------------------------------------
        Gadget ability.
        return -> list[str]
        '''
        if state == "atking_enemy": 
            enemy.effect.append("fire")
        return []
    
    def display(self, screen: pygame.Surface, lines_width: int, screen_width: int = 0, screen_height: int = 0, Board_size: int = 0, x: int = 0, y: int = 0, team: str= ""): 
        '''
        screen: surface to display on (pygame.Surface)
        lines_width: width of ship's lines (int)
        screen_width: width of screen (int)
        screen_height: height of screen (int)
        Board_size: board size (int)
        x: x position (int)
        y: y position (int)
        ----------------------------------------------------------------
        Display gadget.
        return -> None
        '''
        if team == "red": 
            pygame.draw.rect(screen, self.color, ((screen_width/2-Board_size*3.5)+(x*Board_size)+(Board_size*0.25), (screen_height/2-Board_size*2.5)+(y*Board_size)+(Board_size*0.57)\
                , Board_size*0.15, Board_size*0.1), lines_width*200)
        elif team == "blue": 
            pygame.draw.rect(screen, self.color, ((screen_width/2-Board_size*3.5)+(x*Board_size)+(Board_size*0.25), (screen_height/2-Board_size*2.5)+(y*Board_size)+(Board_size*0.57)\
                , Board_size*0.15, Board_size*0.1), lines_width*200)
            
    def basic(self, hp: int, dam: int) -> tuple[int, int]: 
        '''
        hp: ship hp (int)
        dam: ship dam (int)
        ----------------------------------------------------------------
        Return the new ship's hp and dam.
        return -> tuple[int, int]
        '''
        return hp+0, dam+1
    
    
class steel_armor(): 
    def __init__(self): 
        self.color = (200, 200, 200)
        self.chinese_name  ="鋼鐵裝甲"
    
    def ability(self, state: str, selfship: "Ships", Shiplist: list["Ships"], enemy: "Ships" = None) -> list[str]: 
        '''
        state: calling state (str)\n 
            (sort by calling order)\n
            1.start_turn\n
            2.failed_move\n
            3.atking_enemy\n
            4.been_killed\n
            5.atk_succeed\n
            6.end_turn\n
        selfship: self ship (Ships)
        Shiplist: list of ships (list[Ships])
        enemy: enemy ship(Ships)
        ----------------------------------------------------------------
        Gadget ability.
        return -> list[str]
        '''
        return []
    
    def display(self, screen: pygame.Surface, lines_width: int, screen_width: int = 0, screen_height: int = 0, Board_size: int = 0, x: int = 0, y: int = 0, team: str= ""): 
        '''
        screen: surface to display on (pygame.Surface)
        lines_width: width of ship's lines (int)
        screen_width: width of screen (int)
        screen_height: height of screen (int)
        Board_size: board size (int)
        x: x position (int)
        y: y position (int)
        ----------------------------------------------------------------
        Display gadget.
        return -> None
        '''
        if team == "red": 
            pygame.draw.rect(screen, self.color, ((screen_width/2-Board_size*3.5)+(x*Board_size)+(Board_size*0.25), (screen_height/2-Board_size*2.5)+(y*Board_size)+(Board_size*0.57)\
                , Board_size*0.15, Board_size*0.15), lines_width*200)
        elif team == "blue": 
            pygame.draw.rect(screen, self.color, ((screen_width/2-Board_size*3.5)+(x*Board_size)+(Board_size*0.6), (screen_height/2-Board_size*2.5)+(y*Board_size)+(Board_size*0.57)\
                , Board_size*0.15, Board_size*0.15), lines_width*200)
        
    def basic(self, hp: int, dam: int) -> tuple[int, int]: 
        '''
        hp: ship hp (int)
        dam: ship dam (int)
        ----------------------------------------------------------------
        Return the new ship's hp and dam.
        return -> tuple[int, int]
        '''
        return hp+6, dam+0
    
    
class peace_badge(): 
    def __init__(self): 
        self.color = (200, 200, 10)
        self.chinese_name  ="和平徽章"
    
    def ability(self, state: str, selfship: "Ships", Shiplist: list["Ships"], enemy: "Ships" = None) -> list[str]: 
        '''
        state: calling state (str)\n 
            (sort by calling order)\n
            1.start_turn\n
            2.failed_move\n
            3.atking_enemy\n
            4.been_killed\n
            5.atk_succeed\n
            6.end_turn\n
        selfship: self ship (Ships)
        Shiplist: list of ships (list[Ships])
        enemy: enemy ship(Ships)
        ----------------------------------------------------------------
        Gadget ability.
        return -> list[str]
        '''
        if state == "end_turn": 
            shiplist: list["Ships"] = selfship.detect(Shiplist, 8)
            for ship in shiplist:
                ship.heal(2)
        return []
    
    def display(self, screen: pygame.Surface, lines_width: int, screen_width: int = 0, screen_height: int = 0, Board_size: int = 0, x: int = 0, y: int = 0, team: str= ""): 
        '''
        screen: surface to display on (pygame.Surface)
        lines_width: width of ship's lines (int)
        screen_width: width of screen (int)
        screen_height: height of screen (int)
        Board_size: board size (int)
        x: x position (int)
        y: y position (int)
        ----------------------------------------------------------------
        Display gadget.
        return -> None
        '''
        if team == "red": 
            self.shape = (((screen_width/2-Board_size*3.5)+(x*Board_size)+(Board_size*0.44), (screen_height/2-Board_size*2.5)+(y*Board_size)+(Board_size*0.675)),
                        ((screen_width/2-Board_size*3.5)+(x*Board_size)+(Board_size*0.3), (screen_height/2-Board_size*2.5)+(y*Board_size)+(Board_size*0.6)),
                        ((screen_width/2-Board_size*3.5)+(x*Board_size)+(Board_size*0.175), (screen_height/2-Board_size*2.5)+(y*Board_size)+(Board_size*0.675)), 
                        ((screen_width/2-Board_size*3.5)+(x*Board_size)+(Board_size*0.3), (screen_height/2-Board_size*2.5)+(y*Board_size)+(Board_size*0.75))     
                        )
        elif team == "blue": 
            self.shape = (((screen_width/2-Board_size*3.5)+(x*Board_size)+(Board_size*0.56), (screen_height/2-Board_size*2.5)+(y*Board_size)+(Board_size*0.675)),
                        ((screen_width/2-Board_size*3.5)+(x*Board_size)+(Board_size*0.7), (screen_height/2-Board_size*2.5)+(y*Board_size)+(Board_size*0.6)),
                        ((screen_width/2-Board_size*3.5)+(x*Board_size)+(Board_size*0.825), (screen_height/2-Board_size*2.5)+(y*Board_size)+(Board_size*0.675)), 
                        ((screen_width/2-Board_size*3.5)+(x*Board_size)+(Board_size*0.7), (screen_height/2-Board_size*2.5)+(y*Board_size)+(Board_size*0.75))     
                        )
        pygame.gfxdraw.filled_polygon(screen, self.shape, self.color)
    
    def basic(self, hp: int, dam: int) -> tuple[int, int]: 
        '''
        hp: ship hp (int)
        dam: ship dam (int)
        ----------------------------------------------------------------
        Return the new ship's hp and dam.
        return -> tuple[int, int]
        '''
        return hp+2, dam+0
    
    
class spiked_bow(): 
    def __init__(self): 
        self.color = (139, 69, 19)
        self.chinese_name  ="尖刺船頭"
        
    def ability(self, state: str, selfship: "Ships", Shiplist: list["Ships"], enemy: "Ships" = None) -> list[str]: 
        '''
        state: calling state (str)\n 
            (sort by calling order)\n
            1.start_turn\n
            2.failed_move\n
            3.atking_enemy\n
            4.been_killed\n
            5.atk_succeed\n
            6.end_turn\n
        selfship: self ship (Ships)
        Shiplist: list of ships (list[Ships])
        enemy: enemy ship(Ships)
        ----------------------------------------------------------------
        Gadget ability.
        return -> list[str]
        '''
        if state == "failed_move":
            print("failed_move")
            enemy.damage(selfship, Shiplist, 2)
        return []

    def display(self, screen: pygame.Surface, lines_width: int, screen_width: int = 0, screen_height: int = 0, Board_size: int = 0, x: int = 0, y: int = 0, team: str= ""): 
        '''
        screen: surface to display on (pygame.Surface)
        lines_width: width of ship's lines (int)
        screen_width: width of screen (int)
        screen_height: height of screen (int)
        Board_size: board size (int)
        x: x position (int)
        y: y position (int)
        ----------------------------------------------------------------
        Display gadget.
        return -> None
        '''
        if team == "red": 
            self.shape = (((screen_width/2-Board_size*3.5)+(x*Board_size)+(Board_size*0.3), (screen_height/2-Board_size*2.5)+(y*Board_size)+(Board_size*0.6)),
                        ((screen_width/2-Board_size*3.5)+(x*Board_size)+(Board_size*0.3), (screen_height/2-Board_size*2.5)+(y*Board_size)+(Board_size*0.7)),
                        ((screen_width/2-Board_size*3.5)+(x*Board_size)+(Board_size*0.4), (screen_height/2-Board_size*2.5)+(y*Board_size)+(Board_size*0.65))
                        )
        elif team == "blue": 
            self.shape = (((screen_width/2-Board_size*3.5)+(x*Board_size)+(Board_size*0.7), (screen_height/2-Board_size*2.5)+(y*Board_size)+(Board_size*0.6)),
                        ((screen_width/2-Board_size*3.5)+(x*Board_size)+(Board_size*0.7), (screen_height/2-Board_size*2.5)+(y*Board_size)+(Board_size*0.7)),
                        ((screen_width/2-Board_size*3.5)+(x*Board_size)+(Board_size*0.6), (screen_height/2-Board_size*2.5)+(y*Board_size)+(Board_size*0.65))
                        )
        pygame.gfxdraw.filled_polygon(screen, self.shape, self.color)

        if team == "red": 
            self.shape = (((screen_width/2-Board_size*3.5)+(x*Board_size)+(Board_size*0.4), (screen_height/2-Board_size*2.5)+(y*Board_size)+(Board_size*0.6)),
                        ((screen_width/2-Board_size*3.5)+(x*Board_size)+(Board_size*0.4), (screen_height/2-Board_size*2.5)+(y*Board_size)+(Board_size*0.7)),
                        ((screen_width/2-Board_size*3.5)+(x*Board_size)+(Board_size*0.5), (screen_height/2-Board_size*2.5)+(y*Board_size)+(Board_size*0.65))
                        )
        elif team == "blue": 
            self.shape = (((screen_width/2-Board_size*3.5)+(x*Board_size)+(Board_size*0.6), (screen_height/2-Board_size*2.5)+(y*Board_size)+(Board_size*0.6)),
                        ((screen_width/2-Board_size*3.5)+(x*Board_size)+(Board_size*0.6), (screen_height/2-Board_size*2.5)+(y*Board_size)+(Board_size*0.7)),
                        ((screen_width/2-Board_size*3.5)+(x*Board_size)+(Board_size*0.5), (screen_height/2-Board_size*2.5)+(y*Board_size)+(Board_size*0.65))
                        )
        pygame.gfxdraw.filled_polygon(screen, self.shape, self.color)
    
    def basic(self, hp: int, dam: int) -> tuple[int, int]: 
        '''
        hp: ship hp (int)
        dam: ship dam (int)
        ----------------------------------------------------------------
        Return the new ship's hp and dam.
        return -> tuple[int, int]
        '''
        return hp+1, dam+1
    
    
class hacker_plugin(): 
    def __init__(self): 
        self.color = (200, 25, 200)
        self.chinese_name  ="駭客插件"
        
    def ability(self, state: str, selfship: "Ships", Shiplist: list["Ships"], enemy: "Ships" = None) -> list[str]: 
        '''
        state: calling state (str)\n 
            (sort by calling order)\n
            1.start_turn\n
            2.failed_move\n
            3.atking_enemy\n
            4.been_killed\n
            5.atk_succeed\n
            6.end_turn\n
        selfship: self ship (Ships)
        Shiplist: list of ships (list[Ships])
        enemy: enemy ship(Ships)
        ----------------------------------------------------------------
        Gadget ability.
        return -> list[str]
        '''
        if state == "been_killed": 
            enemy.effect.append("stun")
        return []
    
    def display(self, screen: pygame.Surface, lines_width: int, screen_width: int = 0, screen_height: int = 0, Board_size: int = 0, x: int = 0, y: int = 0, team: str= ""): 
        '''
        screen: surface to display on (pygame.Surface)
        lines_width: width of ship's lines (int)
        screen_width: width of screen (int)
        screen_height: height of screen (int)
        Board_size: board size (int)
        x: x position (int)
        y: y position (int)
        ----------------------------------------------------------------
        Display gadget.
        return -> None
        '''
        if team == "red": 
            self.shape = (((screen_width/2-Board_size*3.5)+(x*Board_size)+(Board_size*0.4), (screen_height/2-Board_size*2.5)+(y*Board_size)+(Board_size*0.6)),
                        ((screen_width/2-Board_size*3.5)+(x*Board_size)+(Board_size*0.3), (screen_height/2-Board_size*2.5)+(y*Board_size)+(Board_size*0.55)),
                        ((screen_width/2-Board_size*3.5)+(x*Board_size)+(Board_size*0.3), (screen_height/2-Board_size*2.5)+(y*Board_size)+(Board_size*0.75)),
                        ((screen_width/2-Board_size*3.5)+(x*Board_size)+(Board_size*0.4), (screen_height/2-Board_size*2.5)+(y*Board_size)+(Board_size*0.7)),
                        )
        elif team == "blue": 
            self.shape = (((screen_width/2-Board_size*3.5)+(x*Board_size)+(Board_size*0.6), (screen_height/2-Board_size*2.5)+(y*Board_size)+(Board_size*0.6)),
                        ((screen_width/2-Board_size*3.5)+(x*Board_size)+(Board_size*0.7), (screen_height/2-Board_size*2.5)+(y*Board_size)+(Board_size*0.55)),
                        ((screen_width/2-Board_size*3.5)+(x*Board_size)+(Board_size*0.7), (screen_height/2-Board_size*2.5)+(y*Board_size)+(Board_size*0.75)),
                        ((screen_width/2-Board_size*3.5)+(x*Board_size)+(Board_size*0.6), (screen_height/2-Board_size*2.5)+(y*Board_size)+(Board_size*0.7)),
                        )
        pygame.gfxdraw.filled_polygon(screen, self.shape, self.color)
    
    def basic(self, hp: int, dam: int) -> tuple[int, int]: 
        '''
        hp: ship hp (int)
        dam: ship dam (int)
        ----------------------------------------------------------------
        Return the new ship's hp and dam.
        return -> tuple[int, int]
        '''
        return hp+0, dam+1
    
    
class imperial_engine(): 
    price = 25
    def __init__(self): 
        self.color = (100, 100, 100)
        self.chinese_name  ="帝國引擎"
    
    def ability(self, state: str, selfship: "Ships", Shiplist: list["Ships"], enemy: "Ships" = None) -> list[str]: 
        '''
        state: calling state (str)\n 
            (sort by calling order)\n
            1.start_turn\n
            2.failed_move\n
            3.atking_enemy\n
            4.been_killed\n
            5.atk_succeed\n
            6.end_turn\n
        selfship: self ship (Ships)
        Shiplist: list of ships (list[Ships])
        enemy: enemy ship(Ships)
        ----------------------------------------------------------------
        Engine ability.
        return -> list[str]
        '''
        if state == "atk_succeed":
            selfship.dam += 1
            selfship.update_values()
            selfship.maxhp += 1
            selfship.heal(1)
        return []
    
    def basic(self, hp: int, dam: int) -> tuple[int, int]: 
        '''
        hp: ship hp (int)
        dam: ship dam (int)
        ----------------------------------------------------------------
        Return the new ship's hp and dam.
        return -> tuple[int, int]
        '''
        return hp+3, dam+1


class combustion_engine(): 
    price = 30
    def __init__(self): 
        self.color = (250, 10, 10)
        self.chinese_name  ="熱燃引擎"
        
    def ability(self, state: str, selfship: "Ships", Shiplist: list["Ships"], enemy: "Ships" = None) -> list[str]: 
        '''
        state: calling state (str)\n 
            (sort by calling order)\n
            1.start_turn\n
            2.failed_move\n
            3.atking_enemy\n
            4.been_killed\n
            5.atk_succeed\n
            6.end_turn\n
        selfship: self ship (Ships)
        Shiplist: list of ships (list[Ships])
        enemy: enemy ship(Ships)
        ----------------------------------------------------------------
        Engine ability.
        return -> list[str]
        '''
        if state == "atking_enemy": 
            enemy.effect.append("fire")
        return []
    
    def basic(self, hp: int, dam: int) -> tuple[int, int]: 
        '''
        hp: ship hp (int)
        dam: ship dam (int)
        ----------------------------------------------------------------
        Return the new ship's hp and dam.
        return -> tuple[int, int]
        '''
        return hp+3, dam+0


class flash_engine(): 
    price = 30
    def __init__(self): 
        self.color = (250, 200, 10)
        self.chinese_name  ="光閃引擎"
        
    def ability(self, state: str, selfship: "Ships", Shiplist: list["Ships"], enemy: "Ships" = None) -> list[str]: 
        '''
        state: calling state (str)\n 
            (sort by calling order)\n
            1.start_turn\n
            2.failed_move\n
            3.atking_enemy\n
            4.been_killed\n
            5.atk_succeed\n
            6.end_turn\n
        selfship: self ship (Ships)
        Shiplist: list of ships (list[Ships])
        enemy: enemy ship(Ships)
        ----------------------------------------------------------------
        Engine ability.
        return -> list[str]
        '''
        if state == "start_turn": 
            selfship.move(Shiplist, 1)
        return []
    
    def basic(self, hp: int, dam: int) -> tuple[int, int]: 
        '''
        hp: ship hp (int)
        dam: ship dam (int)
        ----------------------------------------------------------------
        Return the new ship's hp and dam.
        return -> tuple[int, int]
        '''
        return hp+3, dam+0


class stable_engine(): 
    price = 30
    def __init__(self): 
        self.color = (50, 50, 200)
        self.chinese_name  ="穩定引擎"
        
    def ability(self, state: str, selfship: "Ships", Shiplist: list["Ships"], enemy: "Ships" = None) -> list[str]: 
        '''
        state: calling state (str)\n 
            (sort by calling order)\n
            1.start_turn\n
            2.failed_move\n
            3.atking_enemy\n
            4.been_killed\n
            5.atk_succeed\n
            6.end_turn\n
        selfship: self ship (Ships)
        Shiplist: list of ships (list[Ships])
        enemy: enemy ship(Ships)
        ----------------------------------------------------------------
        Engine ability.
        return -> list[str]
        '''
        if state == "end_turn": 
            selfship.shield += 2
            selfship.update_values()
        return []
    
    def basic(self, hp: int, dam: int) -> tuple[int, int]: 
        '''
        hp: ship hp (int)
        dam: ship dam (int)
        ----------------------------------------------------------------
        Return the new ship's hp and dam.
        return -> tuple[int, int]
        '''
        return hp+5, dam+0


class old_engine(): 
    price = 25
    def __init__(self): 
        self.color = (160, 82, 45)
        self.chinese_name  ="老舊引擎"
        self.once = 0
        
    def ability(self, state: str, selfship: "Ships", Shiplist: list["Ships"], enemy: "Ships" = None) -> list[str]: 
        '''
        state: calling state (str)\n 
            (sort by calling order)\n
            1.start_turn\n
            2.failed_move\n
            3.atking_enemy\n
            4.been_killed\n
            5.atk_succeed\n
            6.end_turn\n
        selfship: self ship (Ships)
        Shiplist: list of ships (list[Ships])
        enemy: enemy ship(Ships)
        ----------------------------------------------------------------
        Engine ability.
        return -> list[str]
        '''
        if state == "start_turn" and self.once == 0:
            selfship.effect.append("stun")
            self.once = 1
        
        if state == "failed_move" and self.once > 0:
            if selfship.team != enemy.team:
                value = math.floor(selfship.hp/2)
                if selfship.name == "Mothership": value = math.floor(selfship.hp/5)
                selfship.damage("old and rust", Shiplist, value)
                enemy.damage("old and rust", Shiplist, value)
                selfship.update_values()
                enemy.update_values()
        return []
    
    def basic(self, hp: int, dam: int) -> tuple[int, int]: 
        '''
        hp: ship hp (int)
        dam: ship dam (int)
        ----------------------------------------------------------------
        Return the new ship's hp and dam.
        return -> tuple[int, int]
        '''
        return hp+4, dam+0