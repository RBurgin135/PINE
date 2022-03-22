import pygame
from pygame import FULLSCREEN
import random
import copy
import math


#window setup
import ctypes
user32 = ctypes.windll.user32
global scr_width
global scr_height
scr_width = user32.GetSystemMetrics(0)
scr_height = user32.GetSystemMetrics(1)
window = pygame.display.set_mode((scr_width,scr_height),FULLSCREEN)
pygame.display.set_caption("PINE")
pygame.font.init()
from pygame.locals import *
pygame.init()

class Board:
    def __init__(self):
        self.RUN = True

        #dim
        self.width = 20
        self.height = 15
        self.thickness = 50
        self.coord = [scr_width//2-(self.width*self.thickness//2), scr_height//2-(self.height*self.thickness//2)]

    def Show(self):
        #outer border
        pygame.draw.rect(window, (221,223,220), (self.coord[0], self.coord[1], self.width*self.thickness, self.height * self.thickness), 3)

        #inner lines
        for i in range(1, self.height):
            pygame.draw.line(window, (221,223,220), (self.coord[0], self.coord[1]+i*self.thickness), (self.coord[0] + self.width* self.thickness, self.coord[1]+i*self.thickness))

        for i in range(1, self.width):
            pygame.draw.line(window, (221,223,220), (self.coord[0]+i*self.thickness, self.coord[1]), (self.coord[0]+i*self.thickness, self.coord[1] + self.height* self.thickness))

        #nodes
        for x in range(self.width):
            for y in range(self.height):
                i = self.grid[x][y]
                dim = (i.coord[0]-self.thickness//2+1.5, i.coord[1]-self.thickness//2+1.5, self.thickness-1.5, self.thickness-1.5)
                if i.revealed:
                    if i.number != 0:
                        Font = pygame.font.SysFont('', 30)
                        Text = Font.render(str(i.number), False, (201,115,81))
                        window.blit(Text,(i.coord[0], i.coord[1]))
                
                else:
                    #bombs
                    if self.lose or self.win:
                        if i.bomb:
                            pygame.draw.rect(window, (242,44,36), dim)
                    else:
                        pygame.draw.rect(window, (116,116,116), dim)

                #flagged
                if i.flagged:
                    pygame.draw.rect(window, (66,166,112), dim, 3)

        #titles
        Font = pygame.font.SysFont('', 70)
        if self.lose or self.win:
            if self.win:
                Text = Font.render("WIN", False, (66,166,112))
            else:
                Text = Font.render("LOSE", False, (242,44,36))
            window.blit(Text,(self.coord[0], 50))

            #sub
            sub = pygame.font.SysFont('', 30)
            Text = sub.render("PRESS ENTER TO RETRY", False, (201,115,81))
            window.blit(Text,(self.coord[0], 200))
        
        else:
            #remaining bombs 
            Text = Font.render("BMBS: "+str(self.bombno), False, (201,115,81))
            window.blit(Text,(self.coord[0]-100, 50))
                
    def Setup(self):
        self.lose = False
        self.win = False

        self.grid = []
        for x in range(self.width):
            self.grid.append([])
            for y in range(self.height):
                coord = []
                coord.append(x*self.thickness + self.coord[0] + self.thickness//2)
                coord.append(y*self.thickness + self.coord[1] + self.thickness//2)
                self.grid[x].append(Node([x,y], coord))

        #bombs

        self.bombno = 50
        for i in range(self.bombno):
            x = random.randint(0, self.width-1)
            y = random.randint(0, self.height-1)
            self.grid[x][y].bomb = True

        #number
        for x in range(self.width):
            for y in range(self.height):
                i = self.grid[x][y]
                if not i.bomb:
                    i.FindNumber()

    def Resetnodes(self):
        for x in range(self.width):
            for y in range(self.height):
                self.grid[x][y].exhausted = False
    
    def WinCheck(self):
        win = True
        for x in range(self.width):
            for y in range(self.height):
                i = self.grid[x][y]
                if not i.bomb and not i.revealed:
                    win = False
        
        if win:
            self.win = True

class Node:
    def __init__(self, pycoord, coord):
        self.pycoord = pycoord
        self.coord = coord

        #gameplay
        self.flagged = False
        self.bomb = False
        self.revealed = False
        self.number = False
        self.exhausted = False

    def FindNumber(self):
        x, y = self.pycoord

        self.number = 0
        ticker = [[-1,1],[0,1],[1,1],[1,0],[1,-1],[0,-1],[-1,-1],[-1,0]]
        if x == 0:
            ticker.remove([-1,1])
            ticker.remove([-1,-1])
            ticker.remove([-1,0])
        
            if y == 0:
                ticker.remove([0,-1])
                ticker.remove([1,-1])

        elif y == 0:
            ticker.remove([0,-1])
            ticker.remove([1,-1])
            ticker.remove([-1,-1])

        for i in ticker:
            try :
                if B.grid[x+i[0]][y+i[1]].bomb:
                    self.number += 1
            except:
                IndexError

    def Crackdown(self):
        #find neighbours
        x,y = self.pycoord
        neighbours = []
        ticker = [[-1,1],[0,1],[1,1],[1,0],[1,-1],[0,-1],[-1,-1],[-1,0]]
        if x == 0:
            ticker.remove([-1,1])
            ticker.remove([-1,-1])
            ticker.remove([-1,0])
        
            if y == 0:
                ticker.remove([0,-1])
                ticker.remove([1,-1])

        elif y == 0:
            ticker.remove([0,-1])
            ticker.remove([1,-1])
            ticker.remove([-1,-1])

        for i in ticker:
            try:
                node = B.grid[x+i[0]][y+i[1]]
                neighbours.append(node)
            except:
                IndexError

        #examine neighbours
        for i in neighbours:
            if not i.exhausted:
                i.revealed = True
                i.exhausted = True
                if i.number == 0:
                    i.Crackdown()

class Mouse:
    def __init__(self):
        self.coord = ["",""]
        self.coord[0], self.coord[1] = pygame.mouse.get_pos()

    def Input(self):
        for event in pygame.event.get():
            #mouse
            if event.type == pygame.MOUSEMOTION:
                self.coord[0], self.coord[1] = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    self.LClickDOWN()
                elif pygame.mouse.get_pressed()[2]:
                    self.RClickDOWN()

    def RetryInput(self):
        for event in pygame.event.get():
            #mouse
            if event.type == pygame.MOUSEMOTION:
                self.coord[0], self.coord[1] = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    #exit
                    if self.coord[0] > scr_width-50 and self.coord[0] < scr_width and self.coord[1] < scr_height and self.coord[1] > scr_height-50:
                        B.RUN = False
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_RETURN]:
                    B.Setup()

    def LClickDOWN(self):
        #exit
        if self.coord[0] > scr_width-50 and self.coord[0] < scr_width and self.coord[1] < scr_height and self.coord[1] > scr_height-50:
            B.RUN = False
        else:
            if B.coord[0] < self.coord[0] < B.coord[0]+B.width * B.thickness:
                if B.coord[1] < self.coord[1] < B.coord[1]+B.height * B.thickness:
                    #reveal
                    x, y = Coordfinder(self.coord)
                    i = B.grid[x][y]
                    if not i.flagged:
                        if i.bomb:
                            B.lose = True
                        else:
                            i.revealed = True
                            if i.number == 0:
                                i.exhausted = True
                                i.Crackdown()
                                B.Resetnodes()
                    
                    B.WinCheck()
  
    def RClickDOWN(self):
        #flag
        x, y = Coordfinder(self.coord)
        i = B.grid[x][y]
        if i.flagged:
            B.bombno += 1
            i.flagged = False
        else:
            B.bombno -= 1
            i.flagged = True

#functions
def Coordfinder(coord):
    #finds coords on board
    xFound = False
    yFound = False
    X = 0
    Y = 0
    for x in range(0, B.width):
        if (xFound == False) and (coord[0] >= (B.coord[0] + B.thickness*x)) and (coord[0] <= (B.coord[0] + B.thickness*(x+1))):
            X = x
            xFound = True
        for y in range(0, B.height):
            if (yFound == False) and (coord[1] >= B.coord[1] + B.thickness*y) and (coord[1] <= B.coord[1] + B.thickness*(y+1)):
                Y = y
                yFound = True

    if xFound and yFound:
        pycoord = [X, Y]
        return pycoord
    else:
        return False

if __name__ == '__main__':
    B = Board()
    M = Mouse()

    B.Setup()
    while B.RUN:
        pygame.time.delay(1)
        window.fill((241,243,240))
        #input
        if B.lose or B.win:
            M.RetryInput()
        else:
            M.Input()

        #show
        B.Show()
        
        pygame.display.update()
