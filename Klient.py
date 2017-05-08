#PONG pygame

import socket
import random
import pygame, sys
from pygame.locals import *


#SOCKET
s = socket.socket()         # Create a socket object
host = socket.gethostname() # TUTAJ WPISAC IP komputera na ktorym serwer jest, jak na tym samym to mozna zostawic
port = 12343             # Reserve a port for your service.
s.connect((host, port))
pygame.init()
fps = pygame.time.Clock()

#colors
WHITE = (255,255,255)
RED = (255,255,255)
GREEN = (0,255,0)
BLACK = (0,0,0)

#globals
WIDTH = 600
HEIGHT = 400       
BALL_RADIUS = 20
PAD_WIDTH = 8
PAD_HEIGHT = 80
HALF_PAD_WIDTH = PAD_WIDTH / 2
HALF_PAD_HEIGHT = PAD_HEIGHT / 2


#Creating window
window = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
pygame.display.set_caption('Classic Pong')

class GameManager:
    ball_pos = [0,0]
    ball_vel = [0,0]
    paddle1_vel = 0
    paddle2_vel = 0
    l_score = 0
    r_score = 0
    paddle1_pos = [0,0]
    paddle2_pos = [0,0]
    once = 0
    variables = ""

    def init(self):
        self.paddle1_pos = [HALF_PAD_WIDTH - 1,HEIGHT/2]
        self.paddle2_pos = [WIDTH +1 - HALF_PAD_WIDTH,HEIGHT/2]

    def draw(self,canvas):      
        canvas.fill(BLACK)

        # update paddle's vertical position, keep paddle on the screen
        if self.paddle2_pos[1] > HALF_PAD_HEIGHT and self.paddle2_pos[1] < HEIGHT - HALF_PAD_HEIGHT:
            self.paddle2_pos[1] += self.paddle2_vel
        elif self.paddle2_pos[1] == HALF_PAD_HEIGHT and self.paddle2_vel > 0:
            self.paddle2_pos[1] += self.paddle2_vel
        elif self.paddle2_pos[1] == HEIGHT - HALF_PAD_HEIGHT and self.paddle2_vel < 0:
            self.paddle2_pos[1] += self.paddle2_vel

        #draw paddles and ball
        pygame.draw.circle(canvas, WHITE, self.ball_pos, 20, 0)
        pygame.draw.polygon(canvas, GREEN, [[self.paddle1_pos[0] - HALF_PAD_WIDTH, self.paddle1_pos[1] - HALF_PAD_HEIGHT], [self.paddle1_pos[0] - HALF_PAD_WIDTH, self.paddle1_pos[1] + HALF_PAD_HEIGHT], [self.paddle1_pos[0] + HALF_PAD_WIDTH, self.paddle1_pos[1] + HALF_PAD_HEIGHT], [self.paddle1_pos[0] + HALF_PAD_WIDTH, self.paddle1_pos[1] - HALF_PAD_HEIGHT]], 0)
        pygame.draw.polygon(canvas, GREEN, [[self.paddle2_pos[0] - HALF_PAD_WIDTH, self.paddle2_pos[1] - HALF_PAD_HEIGHT], [self.paddle2_pos[0] - HALF_PAD_WIDTH, self.paddle2_pos[1] + HALF_PAD_HEIGHT], [self.paddle2_pos[0] + HALF_PAD_WIDTH, self.paddle2_pos[1] + HALF_PAD_HEIGHT], [self.paddle2_pos[0] + HALF_PAD_WIDTH, self.paddle2_pos[1] - HALF_PAD_HEIGHT]], 0)

        #update scores
        myfont1 = pygame.font.SysFont("Comic Sans MS", 20)
        label1 = myfont1.render("Score "+str(self.l_score), 1, (255,255,0))
        canvas.blit(label1, (50,20))

        myfont2 = pygame.font.SysFont("Comic Sans MS", 20)
        label2 = myfont2.render("Score "+str(self.r_score), 1, (255,255,0))
        canvas.blit(label2, (470, 20))  

        #Pressing key
    def keydown(self,event):
        if event.key == K_UP:
            self.paddle2_vel = -8
        elif event.key == K_DOWN:
            self.paddle2_vel = 8

    #Not pressing key
    def keyup(self,event):
        if event.key in (K_UP, K_DOWN):
            self.paddle2_vel = 0
    
    def SendPositions(self):
        s.send(str(self.paddle2_pos[0])+','+str(self.paddle2_pos[1]))

    def DrawStartingMessage(self):
        if self.once == 0:
            myfont3 = pygame.font.SysFont("Comic Sans MS", 30)
            label3 = myfont3.render("Waiting for player", 1, (255,255,255))
            window.blit(label3, (200, 150)) 
            pygame.display.update()
            self.once = 1

    def RecivePositions(self):
        self.variables = s.recv(1024)

    def SetVariables(self):
        self.variables = self.variables.split(",")
        print self.variables
        #SETTING ALL
        self.paddle1_pos[0] = int(float(self.variables[0]))
        self.paddle1_pos[1] = int(float(self.variables[1]))
        self.ball_pos[0] = int(float(self.variables[2]))
        self.ball_pos[1] = int(float(self.variables[3]))
        self.l_score = int(float(self.variables[4]))
        self.r_score = int(float(self.variables[5]))


gameManager = GameManager()
gameManager.init()
#game loop
while True:
    gameManager.SendPositions()
    gameManager.DrawStartingMessage()
        
    gameManager.RecivePositions()
    if gameManager.variables == "dc":
        print "Player disconnected"
        pygame.quit()
        sys.exit()
    else:
        gameManager.SetVariables()
        gameManager.draw(window)

        for event in pygame.event.get():
        
            if event.type == KEYDOWN:
                gameManager.keydown(event)
            elif event.type == KEYUP:
                gameManager.keyup(event)
            elif event.type == QUIT:
                pygame.quit()
                sys.exit()
        
        pygame.display.update()
        fps.tick(60)

