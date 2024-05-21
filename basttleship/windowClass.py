import pygame, os
pygame.init()

class Screen():
    def __init__(self) -> None:
        ''' 
        Initialize game screen.
        return -> None
        '''        
        display_info= pygame.display.get_desktop_sizes()
        self.width = display_info[0][0]
        self.height = display_info[0][1]
        
        # self.width = 1960
        # self.height = 1200
            
        
        print(self.width, self.height)
        if self.width/self.height == 1.6:
            self.window = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)
        else:
            maxvalue = [0, 0]
            for H in range(self.height, 0, -1):
                for W in range(self.width, 0, -1):
                    if W/H == 1.6:
                        maxvalue = [W, H]
                        break
                if maxvalue != [0, 0]:
                    break
            self.width = maxvalue[0]
            self.height = maxvalue[1]
            self.window = pygame.display.set_mode((self.width, self.height))
        print(self.width, self.height)
        self.lines_width = round(self.width/600)
        
        
        code_path = os.getcwd()
        font_path = os.path.join(code_path,'text_font/aaweilaihei75.ttf')
        bold_text_font = pygame.font.Font(font_path, int(self.width/1500*33*1.2))
        normal_text_font = pygame.font.Font(font_path, int(self.width/1500*16.5*1.2))
        small_text_font = pygame.font.Font(font_path, int(self.width/1500*16.5*0.7*1.2))
        self.font = [small_text_font, normal_text_font, bold_text_font]