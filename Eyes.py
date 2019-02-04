"""
#This program is built on Raspian operating system.  Version Jessie.
#Tested on a Raspberry Pi3 and Raspberry Pi Display.

#Version 1.0 Released 2018-07-18
"""

#imports
from Tkinter import *               # for graphics
from time import sleep              # to pause program
from datetime import datetime       # for blinking timing
from datetime import timedelta      # for blinking timing
from random import randint          # for pseudo random number generator
import RPi.GPIO as GPIO             # necessary for reading GPIO
import sys, select                  # necessary for exiting wait loop with a
                                    # keyboard event

"""
We use 3x GPIO to get requested eye location from Intel Euclid module...
...(With Adafruit Trinket M0 inbetween the two.)
"""

GPIO.setmode(GPIO.BCM)              
GPIO.setup(14, GPIO.IN)             
GPIO.setup(15, GPIO.IN)
GPIO.setup(18, GPIO.IN)

"""
We use the folowing conventions.
All axis given from the robot's point of view.

Display Screen Axis:

The Origine (0,0,0) is at top right of screen (from robot's perspective)
X axis points Left
Y is not used
Z axis points Down (this is the opposite of the general robot's axis that has...
... Z axis pointing up)

Location Codes for the eyes
000: look straight ahead *note1
001: look up
010: look down
011: look left
100: look right
101: not used
110: not used
111: exit to command prompt

*note1:According to Boardcom BCM2835 Arm peripherals document, page 102, GPIO 7
to 27 default to 0V.
It is assumed that Adafruit Trinket M0 pins default to 0V also.
Therefore, we make 000 associated with looling straight ahead, as default.
"""

#parameters
DistanceRi2Li=400 #Distance Right Eye to Left Eye (units are Pixels)
MinTimeBtweenBlink=1
MaxTimeBtweenBlink=4

#eye_location "000" refers to looking straight ahead  
eye_location_bit_1="0"
eye_location_bit_2="0"
eye_location_bit_3="0"
eye_location=eye_location_bit_3+eye_location_bit_2+eye_location_bit_1

#eye_r_location refers to eye_request_location
eye_r_location_bit_1="0"
eye_r_location_bit_2="0"
eye_r_location_bit_3="0"
eye_r_location=eye_r_location_bit_3+eye_r_location_bit_2+eye_r_location_bit_1

#print(eye_location)             #un-comment for debugging purposes
#print(eye_request_location)     #un-comment for debugging purposes

#***We set up locations that each mini-drawing will start (St) and finish (Fi)***

#IBB I=invisible B=black b=box
#IBB acts as eyelid when moved in front of eyes. For blinking annimation.
IBBStXCoor=50                       #Invisible BB X coordinate start
IBBStZCoor=-150
IBBDeltaX=800                       #lenght of invisible box
IBBDeltaZ=250                       #height of invisible box
IBBFiXCoor=IBBStXCoor+IBBDeltaX     #Finish X coordinate
IBBFiZCoor=IBBStZCoor+IBBDeltaZ     #Finish Z coordinate

#R1:R=Right, 1=Back of Eye, typically white
R1iStXCoor=50
R1iStZCoor=100
R1iDeltaX=300
R1iDeltaZ=150
R1iFiXCoor=R1iStXCoor+R1iDeltaX
R1iFiZCoor=R1iStZCoor+R1iDeltaZ

#R2: R=Right 2=MidEye, typically blue,green,etc.
R2iDeltaX=100
R2iDeltaZ=100
R2StXCoor=R1iStXCoor+(R1iDeltaX/2)-(R2iDeltaX/2)
R2StZCoor=R1iStZCoor+(R1iDeltaZ/2)-(R2iDeltaZ/2)
R2FiXCoor=R1iStXCoor+(R1iDeltaX/2)+(R2iDeltaX/2)
R2FiZCoor=R1iStZCoor+(R1iDeltaZ/2)+(R2iDeltaZ/2)

#R3: R=Right 3=SmallEye, typically black
R3iDeltaX=50
R3iDeltaZ=50
R3iStXCoor=R1iStXCoor+(R1iDeltaX/2)-(R3iDeltaX/2)
R3iStZCoor=R1iStZCoor+(R1iDeltaZ/2)-(R3iDeltaZ/2)
R3iFiXCoor=R1iStXCoor+(R1iDeltaX/2)+(R3iDeltaX/2)
R3iFiZCoor=R1iStZCoor+(R1iDeltaZ/2)+(R3iDeltaZ/2)

#L1: L=Left, 1=Back of Eye, typically white
L1iStXCoor=R1iStXCoor+DistanceRi2Li
L1iStZCoor=R1iStZCoor
L1iDeltaX=R1iDeltaX
L1iDeltaZ=R1iDeltaZ
L1iFiXCoor=R1iStXCoor+R1iDeltaX+DistanceRi2Li
L1iFiZCoor=R1iStZCoor+R1iDeltaZ

#L2: L=Left, 2=MidEye, typically blue,green,etc.
L2iDeltaX=100
L2iDeltaZ=100
L2iStXCoor=R2StXCoor+DistanceRi2Li
L2iStZCoor=R2StZCoor
L2iFiXCoor=R2FiXCoor+DistanceRi2Li
L2iFiZCoor=R2FiZCoor

#L3: L=Left, 3=SmallEye, typically black
L3iDeltaX=50
L3iDeltaZ=50
L3iStXCoor=R1iStXCoor+(R1iDeltaX/2)-(L3iDeltaX/2)+DistanceRi2Li
L3iStZCoor=R1iStZCoor+(R1iDeltaZ/2)-(L3iDeltaZ/2)
L3iFiXCoor=R1iStXCoor+(R1iDeltaX/2)+(L3iDeltaX/2)+DistanceRi2Li
L3iFiZCoor=R1iStZCoor+(R1iDeltaZ/2)+(L3iDeltaZ/2)

def Move_eyes_up(Iterations):
    """
    Iterations variable is passed as an input.
    Executes moving the blue and black of the eye upwards.
    It does this for both eyes simoultaniously.
    One "level" moves 3 animation frames.
    It will do this once or twice depending if passed variable Iterations is equal to 1 or 2.
    Function does not return any values
    """
    
    for i in range (0,Iterations):
        for j in range(1,3):
            Fond.move(RightEyeBlue,0,-10)
            Fond.move(RightEyeBlack,0,-10)
            Fond.move(LeftEyeBlue,0,-10)
            Fond.move(LeftEyeBlack,0,-10)
            fenetre.update()
            sleep(0.05)
    

def Move_eyes_down(Iterations):
    """
    Iterations variable is passed as an input.
    Executes moving the blue and black of the eye downwards.
    It does this for both eyes simoultaniously.
    One "level" moves 3 animation frames.
    It will do this once or twice depending if passed variable Iterations is equal to 1 or 2.
    Function does not return any values
    """
    for i in range (0,Iterations):
        for j in range(1,3):
            Fond.move(RightEyeBlue,0,10)
            Fond.move(RightEyeBlack,0,10)
            Fond.move(LeftEyeBlue,0,10)
            Fond.move(LeftEyeBlack,0,10)
            fenetre.update()
            sleep(0.05)
    
def Move_eyes_left(Iterations):
    """
    Iterations variable is passed as an input.
    Executes moving the blue and black of the eye towards the left (robot's point of view).
    It does this for both eyes simoultaniously.
    One "level" moves 3 animation frames.
    It will do this once or twice depending if passed variable Iterations is equal to 1 or 2.
    Function does not return any values
    """

    for i in range (0,Iterations):
        for j in range(1,7):
            Fond.move(RightEyeBlue,10,0)
            Fond.move(RightEyeBlack,10,0)
            Fond.move(LeftEyeBlue,10,0)
            Fond.move(LeftEyeBlack,10,-0)
            fenetre.update()
            sleep(0.05)
    
def Move_eyes_right(Iterations):  
    """
    Iterations variable is passed as an input.
    Executes moving the blue and black of the eye towards the right (robot's point of view).
    It does this for both eyes simoultaniously.
    One "level" moves 3 animation frames.
    It will do this once or twice depending if passed variable Iterations is equal to 1 or 2.
    Function does not return any values
    """
    for i in range (0,Iterations):
        for j in range(1,7):
            Fond.move(RightEyeBlue,-10,0)
            Fond.move(RightEyeBlack,-10,0)
            Fond.move(LeftEyeBlue,-10,0)
            Fond.move(LeftEyeBlack,-10,-0)
            fenetre.update()
            sleep(0.05)
    
def Blink():
    """
    No values are passed as an input to this function.
    Function moves "Invisible Black Box" " down in front of" eyes.
    Once eyes are fully covered, movement goes upward, reveiling the eyes fully once again. 
    (Before the function is called, the IBB is invisible because it is black located infront
    of a black background.)
    Because IBB is at a higher layer than the eyes, they are "over" the eyes.
    Therefore, when box lowers to cover the eyes and then rises to un-cover the eyes, it
    gives yeilds a blinking annimation.
    The function returns no values. 

    """
    for i in range(1,20):
        Fond.move(IBB,0,10)
        fenetre.update()
        sleep(0.005)
    sleep(0.1)
    for i in range(1,20):
        Fond.move(IBB,0,-10)
        fenetre.update()
        sleep(0.005)

#***main program****

print("You have 10 seconds press any key and enter to interrupt face program and reach command prompts")

#We wait for an input for a given amount of time. If none received, continue program.
#select.select is used to accomplish this.
#last argument is the duration that will "wait for input".  Need to do testing and/or look
#at documentation because value does not seem to correspond to number of seconds. 
i,o,e = select.select([sys.stdin],[],[],3) 
if (i):
    x=sys.stdin.readline().strip()      
    sys.exit(0)
else:
    
    #***We draw the eyes looking straight ahead as initial set up***
    fenetre=Tk()
    fenetre.title("eyes")
    fenetre.geometry("800x400")
    fenetre.overrideredirect(True)
    fenetre.attributes("-fullscreen",False) #When debugging, set to false to be able to close
                                            #animation window.
                                            #When robot in front of potential investor, set to
                                            #True for maximum "Wow effect" 

    fenetre.overrideredirect(False)
    Fond=Canvas(fenetre,width=800,height=600,bg="black") #set background to black
    Fond.place(x=0,y=0)

    #Create right eye with 3 "oval" functions
    RightEyeWhite=Fond.create_oval(R1iStXCoor,R1iStZCoor,R1iFiXCoor,R1iFiZCoor,fill="white")
    RightEyeBlue=Fond.create_oval(R2StXCoor,R2StZCoor,R2FiXCoor,R2FiZCoor,fill="blue")
    RightEyeBlack=Fond.create_oval(R3iStXCoor,R3iStZCoor,R3iFiXCoor,R3iFiZCoor,fill="black")

    #Create left eye with 3 "oval" functions
    LeftEyeWhite=Fond.create_oval(L1iStXCoor,L1iStZCoor,L1iFiXCoor,L1iFiZCoor,fill="white")
    LeftEyeBlue=Fond.create_oval(L2iStXCoor,L2iStZCoor,L2iFiXCoor,L2iFiZCoor,fill="blue")
    LeftEyeBlack=Fond.create_oval(L3iStXCoor,L3iStZCoor,L3iFiXCoor,L3iFiZCoor,fill="black")

    #Create IBB last so that it will be the "top layer". 
    IBB=Fond.create_rectangle(IBBStXCoor,IBBStZCoor,IBBFiXCoor,IBBFiZCoor,fill="black")

    #*****
    #We enter infinite loop that will move eye location to correspond with requested location
    #based on GPIO inputs.
    #A blink animation will also be initiated at pseudo random number of seconds
    #*****
    while True:
        TimeB4Blink = datetime.now()
        Time_2_B_added=randint(MinTimeBtweenBlink,MaxTimeBtweenBlink)
        Time2Blink=TimeB4Blink+timedelta(seconds=Time_2_B_added)
        
        #****
        #We enter loop that will only break away when random time of not blinking has expired.
        #When expired, blinking function will be called, timers updated and re-enter this loop.
        #When in function, it is continously looking at GPIO status in order to asses if new
        #location of eyes has been requested.  If so, appropriate annimation function is called.
        while (TimeB4Blink<Time2Blink):
            #We look at status of GPIO to see if requested location is different than EyeLocation
            if (GPIO.input(14)==1): eye_r_location_bit_1="1"
            if (GPIO.input(15)==1): eye_r_location_bit_2="1"
            if (GPIO.input(18)==1): eye_r_location_bit_3="1"


            if (GPIO.input(14)==0): eye_r_location_bit_1="0"
            if (GPIO.input(15)==0): eye_r_location_bit_2="0"
            if (GPIO.input(18)==0): eye_r_location_bit_3="0"
            eye_r_location=eye_r_location_bit_3+eye_r_location_bit_2+eye_r_location_bit_1

            print("1:")
            print(eye_location)
            print (eye_r_location)
            
            if ((eye_location=="000") and (eye_r_location=="001")):
                Move_eyes_up(Iterations=1)
                eye_location="001"
            if ((eye_location=="000") and (eye_r_location=="010")):
                Move_eyes_down(Iterations=1)
                eye_location="010"
            if ((eye_location=="000") and (eye_r_location=="011")):
                Move_eyes_left(Iterations=1)
                eye_location="011"
            if ((eye_location=="000") and (eye_r_location=="100")):
                Move_eyes_right(Iterations=1)
                eye_location="100"
            
            if ((eye_location=="001") and (eye_r_location=="000")):
                Move_eyes_down(Iterations=1)
                eye_location="000"
            if ((eye_location=="001") and (eye_r_location=="010")):
                Move_eyes_down(Iterations=2)
                eye_location="010"
            if ((eye_location=="001") and (eye_r_location=="011")):
                Move_eyes_down(Iterations=1)
                Move_eyes_left(Iterations=1)
                eye_location="011"
            if ((eye_location=="001") and (eye_r_location=="100")):
                Move_eyes_right(Iterations=1)
                eye_location="100"
            
            if ((eye_location=="010") and (eye_r_location=="000")): 
                Move_eyes_up(Iterations=1)
                eye_location="000"
            if ((eye_location=="010") and (eye_r_location=="001")):
                Move_eyes_up(Iterations=2)
                eye_location="001"
            if ((eye_location=="010") and (eye_r_location=="011")): 
                Move_eyes_up(Iterations=1)
                Move_eyes_left(Iterations=1)
                eye_location="011"
            if ((eye_location=="010") and (eye_r_location=="100")):
                Move_eyes_up(Iterations=1)
                Move_eyes_right(Iterations=1)
                eye_location="100"

            if ((eye_location=="011") and (eye_r_location=="000")): 
                Move_eyes_right(Iterations=1)
                eye_location="000"
            if ((eye_location=="011") and (eye_r_location=="001")):
                Move_eyes_right(Iterations=2)
                eye_location="001"
            if ((eye_location=="011") and (eye_r_location=="010")): 
                Move_eyes_right(Iterations=1)
                Move_eyes_down(Iterations=1)
                eye_location="010"
            if ((eye_location=="011") and (eye_r_location=="100")):
                Move_eyes_right(Iterations=2)
                eye_location="100"

            if ((eye_location=="100") and (eye_r_location=="000")): 
                Move_eyes_left(Iterations=1)
                eye_location="000"
            if ((eye_location=="100") and (eye_r_location=="001")):
                Move_eyes_left(Iterations=1)
                Move_eyes_up(Iterations=1)
                eye_location="001"
            if ((eye_location=="100") and (eye_r_location=="010")): 
                Move_eyes_left(Iterations=1)
                Move_eyes_down(Iterations=1)
                eye_location="010"
            if ((eye_location=="100") and (eye_r_location=="011")):
                Move_eyes_left(Iterations=2)
                eye_location="011"

            if (eye_r_location=='111'): #code of exit program request
                sys.exit(0)             #exit program command
            
            TimeB4Blink = datetime.now() #update TimeB4Blink variable
            #print(TimeB4Blink) #un-comment for debugging purposes
            print(Time2Blink)   #un-comment for debugging purposes
            sleep(2)
               
        print("second loop")    #debbuging 
        Blink()
    fenetre.mainloop()
    
