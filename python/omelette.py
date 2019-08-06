import time
import serial
from math import pi, sqrt
import numpy
import socket

import kg_robot as kgr


### -----------------------------------------------------###
### ----------------------- Notes -----------------------###

'''
-0.02 in x direction is the centre of tools


'''

### -----------------------------------------------------###
### -----------------Defining Constants------------------###
restart = '0'
normalGrip = '1'
mediumGrip = '2'
hardGrip = '3'
openMM = '4'
closeMM = '5'
gripInCentre = '6'
openGripper = '7'
lightGrip = '8'
fastArmOnlyGrip = '9'


### -----------------------------------------------------###
### ------------ -Defining Global Varialbles-------------###
disableGripper = False


### -----------------------------------------------------###
### -----------------Defining Functions------------------###

# Function to communicate with arduino
def gripperAction(command, msg = 0):

    if disableGripper:
        print("gripper disabled")

    else:
        arduino.write(bytes(str(command), 'utf-8'))

        # not sure if this works esp on the arduino side
        if msg != 0:
            arduino.write(bytes(str(msg), 'utf-8'))

        while 1:
            msgFromArduino = arduino.readline().decode('utf-8')
            if "Complete" in msgFromArduino:
                print("Arduino Command Complete")
                return 0
            if "Error" in msgFromArduino:
                print("Error with gripper!!")
                return 1

# Opening the egg
def open_egg(arthur, debug = False):
    if debug:
        input()


    arthur.movej_rel([0, 0, 0, 0, -pi, 0], vel=2, acc=1)
    arthur.set_tcp([0, 0, -0.17, 0, 0, 0])
    # arthur.movel_tool([0, 0, 0, -pi / 16, 0, 0])
    arthur.translatejl([-0.03, -0.4, 0.17])
    arthur.translatel([-0.055, -0.565, 0.17], vel=0.3)

    time.sleep(1)
    if debug:
        input()

    arthur.translatel([-0.055, -0.5, 0.17], vel=0.1)
    arthur.translatel([-0.11, -0.5, 0.17], vel=0.1)
    arthur.translatel([-0.11, -0.59, 0.17], vel=0.1)

    time.sleep(1)

    arthur.translatel([-0.03, -0.4, 0.17], vel=0.1)

    if debug:
        input()


#Getting the egg opener
def take_out_shell(arthur, debug = False):
    arthur.home(acc=1, vel=2)
    arthur.set_tcp([0, 0, 0.163, 0, 0, 0])
    currpos = arthur.getl()
    arthur.movejl([currpos[0], currpos[1], currpos[2], pi / 2, 0, 0], vel=2)
    arthur.translatejl([currpos[0] - 0.15, -0.66, currpos[2]], vel=0.1)



def pour_egg(arthur, debug = False):
    if debug:
        input()

    arthur.set_tcp([0, 0, 0.163, 0, 0, 0])

    arthur.movejl([-0.02, -0.5, 0.15, 0, pi, 0], vel=2, acc=2)

    arthur.movel_tool([0, 0, 0, 0, 0, pi / 2], vel=1)
    arthur.movel_tool([0, 0, 0, 0, -pi / 12, 0], vel=1)
    currpos = arthur.getl()

    arthur.translatel([currpos[0], currpos[1] - 0.03, currpos[2] - 0.11], vel=0.1)

    if debug:
        input()
    gripperAction(fastArmOnlyGrip)

    currpos = arthur.getl()
    arthur.translatel([currpos[0], currpos[1] + 0.2, currpos[2]], vel=1)
    gripperAction(mediumGrip)
    if debug:
        input()

    currpos = arthur.getl()
    arthur.translatel([currpos[0], currpos[1], currpos[2] + 0.2], vel=1)
    arthur.movel_tool([0, 0, 0, 0, pi / 12, 0], vel=1)

    if debug:
        input()
    arthur.movel_tool([0, 0, 0, 0, 0, pi / 2], vel=3)
    arthur.translatejl([0.3, -0.25, 0.3], vel=0.4)

    arthur.movel_tool([0, 0, 0, 0, 0, pi / 7], vel=3)

    arthur.movej_rel([0, 0, 0, pi / 6, 0, 0], vel=1)

    currpos = arthur.getl()
    arthur.translatejl([currpos[0] - 0.07, currpos[1] + 0.05, currpos[2] - 0.17], vel=1)

    arthur.movej_rel([0, 0, 0, pi / 5, 0, 0], vel=1)
    currpos = arthur.getl()
    arthur.translatejl([currpos[0] - 0.05, currpos[1] + 0.01, currpos[2] - 0.12], vel=1)
    arthur.movej_rel([0, 0, 0, pi / 4, 0, 0], vel=1)
    currpos = arthur.getl()
    arthur.translatejl([currpos[0], currpos[1], currpos[2] + 0.2], vel=0.2)


def main():
    print("------------Configuring Arthur-------------\r\n")
    arthur = kgr.kg_robot(port=30010, db_host="169.254.50.100")
    print("----------------Hi Arthur!-----------------\r\n\r\n")

    gripperAction(restart)
    #open_egg(arthur, debug = False)
    #pour_egg(arthur, debug = False)

    arthur.close()


if __name__ == '__main__': 
    arduino = serial.Serial('COM4', 115200)
    main()