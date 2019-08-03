import time
import serial
from math import pi
import numpy
import socket

import kg_robot as kgr


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



### -----------------------------------------------------###
### -----------------Defining Functions------------------###

# Function to communicate with arduino
def gripperAction(arduino, command, msg = 0):
    arduino.write(bytes(str(command), 'utf-8'))

    # not sure if this works esp on the arduino side
    if msg != 0:
        arduino.write(bytes(str(msg), 'utf-8')

    while 1:
        msgFromArduino = arduino.readline().decode('utf-8')
        if "Complete" in msgFromArduino:
            print("correct message")
            return 0
        else if "Error" in msgFromArduino:
            print("Error with gripper!!")
            return 1
        else:
            print("Something wrong with communication")
            return 2

def gripperActiongripperActionExperiment(command, msg = 0):
    arduino.write(bytes(str(command), 'utf-8'))

    # not sure if this works esp on the arduino side
    if msg != 0:
        arduino.write(bytes(str(msg), 'utf-8')

    while 1:
        msgFromArduino = arduino.readline().decode('utf-8')
        if "Complete" in msgFromArduino:
            print("correct message")
            return 0
        else if "Error" in msgFromArduino:
            print("Error with gripper!!")
            return 1
        else:
            print("Something wrong with communication")
            return 2




def main():
    print("------------Configuring Arthur-------------\r\n")
    arthur = kgr.kg_robot(port=30010, db_host="169.254.178.100")
    print("----------------Hi Arthur!-----------------\r\n\r\n")
    #arduino = serial.Serial('COM4', 115200)


    gripperActionExperiment(normalGrip)

    #gripperAction(arduino, normalGrip)
    #time.sleep(1);
    #gripperAction(arduino, normalGrip)
    arthur.close()


if __name__ == '__main__': 
    arduino = serial.Serial('COM4', 115200)
    main()
    
