#!/usr/bin/python 

import socket               # Import socket module
import random
import sys
import threading
import msvcrt

#globals
WIDTH = 600
HEIGHT = 400       
BALL_RADIUS = 20
PAD_WIDTH = 8
PAD_HEIGHT = 80
HALF_PAD_WIDTH = PAD_WIDTH / 2
HALF_PAD_HEIGHT = PAD_HEIGHT / 2


class Session:

    ball_pos = [0,0]    # Ball position
    ball_vel = [0,0]    # Ball velocity
    paddle1_vel = 0     # Velocity of player one
    paddle2_vel = 0     # Velocity of player two
    l_score = 0         # Score of player one
    r_score = 0         # Score of player two
    c = ""              # Socket accept player one
    d = ""              # Socket accept player two
    addr = ""           # Adress of player one
    addr2 = ""          # Adress of player two
    playerOne = ""      # Data recived from player one
    playerTwo = ""      # Data recived from player two
    isActive = 0        # If session is still active
    closed = 0          # If session should be closed and deleted

    #Putting ball after getting score from players or at start of the game
    def ball_init(self,right):
        self.ball_pos = [WIDTH/2,HEIGHT/2]
        horz = random.randrange(2,4)
        vert = random.randrange(1,3)
        if right == False:
            horz = - horz
        self.ball_vel = [horz,-vert]

    #Starting settings
    def init(self):
        self.l_score = 0
        self.r_score = 0
        if random.randrange(0,2) == 0:
            self.ball_init(True)
        else:
            self.ball_init(False)

    #Checking all ball collisions
    def ballCheck(self):
        try:
           #ball collision check on top and bottom walls
            if int(self.ball_pos[1]) <= BALL_RADIUS:
                self.ball_vel[1] = - self.ball_vel[1]
            if int(self.ball_pos[1]) >= HEIGHT + 1 - BALL_RADIUS:
                self.ball_vel[1] = -self.ball_vel[1]
            
            #ball collison check on gutters or paddles
            if int(self.ball_pos[0]) <= BALL_RADIUS + PAD_WIDTH and int(self.ball_pos[1]) in range(self.paddle1_pos[1] - HALF_PAD_HEIGHT,self.paddle1_pos[1] + HALF_PAD_HEIGHT,1):
                self.ball_vel[0] = -self.ball_vel[0]
                self.ball_vel[0] *= 1.1
                self.ball_vel[1] *= 1.1
            elif int(self.ball_pos[0]) <= BALL_RADIUS + PAD_WIDTH:
                self.r_score += 1
                self.ball_init(True)
                
            if int(self.ball_pos[0]) >= WIDTH + 1 - BALL_RADIUS - PAD_WIDTH and int(self.ball_pos[1]) in range(self.paddle2_pos[1] - HALF_PAD_HEIGHT,self.paddle2_pos[1] + HALF_PAD_HEIGHT,1):
                self.ball_vel[0] = -self.ball_vel[0]
                self.ball_vel[0] *= 1.1
                self.ball_vel[1] *= 1.1
            elif int(self.ball_pos[0]) >= WIDTH + 1 - BALL_RADIUS - PAD_WIDTH:
                self.l_score += 1
                self.ball_init(False)
            #update ball
            self.ball_pos[0] += int(self.ball_vel[0])
            self.ball_pos[1] += int(self.ball_vel[1])
        except:
            self.isActive = 0
            self.CloseSession()


    #WAITNG TO GET TWO PLAYERS TWO ONE SESSION
    def GettingClients(self, socket):
        try:
            self.c, self.addr = socket.accept()
            self.d, self.addr2 = socket.accept()
            self.isActive = 1
        except:
            print "Waiting for players"


    #RECIVING POSITIONS OF PAD FROM CLIENTS
    def RecivePositions(self):
        try:
            self.playerOne = self.c.recv(1024)
            self.playerTwo = self.d.recv(1024)
        except:
            self.isActive = 0
            self.CloseSession()
        if self.playerOne == '':
            try:
                self.d.send("dc")
            except:
                self.isActive = 0
            self.CloseSession()
            self.isActive = 0
        elif self.playerTwo == '':
            try:
                self.c.send("dc")
            except:
                isActive = 0
            self.CloseSession()
            self.isActive = 0

    #SENDING PADS POSITIONS, BALL POSITION AND SCORE TO CLIENTS
    def SendPositions(self):
        try:
            self.paddle1_pos = [600 - int(self.playerOne.split(",")[0]),400 - int(self.playerOne.split(",")[1])]
            self.paddle2_pos = [int(self.playerTwo.split(",")[0]),int(self.playerTwo.split(",")[1])]
            self.c.send(str(600 - self.paddle2_pos[0]) + ',' + str(400 - self.paddle2_pos[1]) + ',' + str(600 - self.ball_pos[0]) + ',' + str(400 - self.ball_pos[1]) + ',' + str(self.r_score) + ',' + str(self.l_score))
            self.d.send(str(self.paddle1_pos[0]) + ',' + str(self.paddle1_pos[1]) + ',' + str(self.ball_pos[0]) + ',' + str(self.ball_pos[1]) + ',' + str(self.l_score) + ',' + str(self.r_score))
        except:
            self.CloseSession()
            self.isActive = 0

    #CLOSING SESSION. CLOSED SESSION WILL BE DELETED IN MAIN LOOP
    def CloseSession(self):
        self.closed = 1
        self.c.close()
        self.d.close()

    #UPDATING ALL POSITIONS AND MOVING BALL
    def Update(self):
        if self.isActive == 1:
            self.RecivePositions()
            self.ballCheck()
            self.SendPositions()



#SOCKET
s = socket.socket()         # Create a socket object
host = socket.gethostname() # Get local machine name
port = 12343                # Reserve a port for your service.
s.bind((host, port))        # Bind to the port
s.listen(5)

#SESSION
ses1 = Session()            # First session creating
ses1.GettingClients(s)
ses1.init()

#LIST
listS = []                  # List of all sessions
listS.append(ses1)


while True:
    #If list of session is empty, create new session
    if not listS:
        sesNew = Session()
        sesNew.init()
        threading.Thread(target = sesNew.GettingClients,args=(s,)).start()
        listS.append(sesNew)

    #If session is closed delete it , if its active update it
    for i in listS:
        if i.closed == 1:
            listS.remove(i)
        if i.isActive == 1:
            i.Update()

    #If last element is active, create new session
    if listS[-1].isActive == 1:
        sesNew = Session()
        sesNew.init()
        threading.Thread(target = sesNew.GettingClients,args=(s,)).start()
        listS.append(sesNew)

    if msvcrt.kbhit() and ord(msvcrt.getch()) == 27:
        print "Server closed"
        s.close()
        break
