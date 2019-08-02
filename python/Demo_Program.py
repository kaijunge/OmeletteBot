import time
import serial
from math import pi
import numpy
import socket

import kg_robot as kgr


def print_cartesian_location(pos):
    pos = [round(elem, 2) for elem in pos]
    print("x,y,z: ", pos[0], pos[1], pos[2])
    print("rx, ry, rz: ", round(pos[3] * (180 / pi), 2), round(pos[4] * (180 / pi), 2), round(pos[5] * (180 / pi), 2))


def move_wrt_world(ur, pos):
    print("We are currently at:")
    print_cartesian_location(ur.getl())
    print("We want to get to:")
    print_cartesian_location(pos)
    print("press key")
    input()
    ur.movejl(pos)


def rotate_wrt_world(ur, rot):
    position = ur.getl()
    print("We are currently at:")
    print_cartesian_location(position)
    for i in range(0, 3):
        position[i + 3] = rot[i]
    print("We want to get to:")
    print_cartesian_location(position)
    print("press key")
    input()
    ur.movejl(position)


def move_tool_wrt_end(ur, pos):
    print("we want to move the tool to: ")
    print_cartesian_location(pos)
    print("press key")
    input()
    ur.movel_tool(pos)

def calibrate(ur):
    print("Begin calibration sequence?")

    if input() == "y":
        print("Calibration started")
        while 1:
            ur.movejl([0.395, -0.21, 0.04, 0, pi, 0])
            input()
            ur.movejl([0.395, -0.21, 0.4, 0, pi, 0])
            ur.movejl([0.1, -0.74, 0.3475, 0, pi, 0])
            print("End calibration?")
            if input() == "y":
                print("Calibration terminated")
                time.sleep(0.5)
                ur.home()
                break
            else:
                print("Calibration continued")
                time.sleep(0.5)
                ur.movejl([0.395, -0.21, 0.4, 0, pi, 0])

def egg_cracking(ur):
    ur.movej_rel([0,0,0,0,pi,0], vel=2, acc= 1)
    ur.set_tcp([0,0,-0.17,0,0,0])
    ur.movel_tool([0,0,0,-pi/16,0,0])
    ur.translatejl([-0.1, -0.4, 0.17])
    ur.translatel([-0.09, -0.638, 0.17], vel = 0.1)
    time.sleep(1)
    ur.translatel([-0.1, -0.55, 0.17])
    for i in range(0, 3):
        ur.translatejl([-0.14, -0.55, 0.17])
        ur.translatejl([-0.14, -0.645, 0.17], vel = 0.1)
        time.sleep(0.5)
    ur.translatejl([-0.14, -0.66, 0.17], vel=0.1)
    ur.movejl([-0.15, -0.3, 0.21, 0, 0, 0])
    ur.movej_rel([0, 0, 0, 0, -pi, 0], vel=2, acc = 1)

def get_whisk(arduino):
    arduino.write(bytes('2', 'utf-8'))
    while 1:
        msg = arduino.readline().decode('utf-8')
        print(msg)
        if "5" in msg:
            print("correct message")
            break

    print("got whisk")

def get_bowl(arduino):
    arduino.write(bytes('3', 'utf-8'))
    while 1:
        msg = arduino.readline().decode('utf-8')
        print(msg)
        if "5" in msg:
            print("correct message")
            break

    print("got bowl")

def open_a_bit(arduino):
    arduino.write(bytes('4', 'utf-8'))
    while 1:
        msg = arduino.readline().decode('utf-8')
        print(msg)
        if "5" in msg:
            print("correct message")
            break

    print("Opened a bit")

def close_a_bit(arduino):
    arduino.write(bytes('7', 'utf-8'))
    while 1:
        msg = arduino.readline().decode('utf-8')
        print(msg)
        if "5" in msg:
            print("correct message")
            break

    print("Opened a bit")

def open_gripper(arduino):
    arduino.write(bytes('6', 'utf-8'))
    while 1:
        msg = arduino.readline().decode('utf-8')
        print(msg)
        if "5" in msg:
            print("correct message")
            break

    print("Gripper opened")

def close_pan(arduino):
    arduino.write(bytes('8', 'utf-8'))
    while 1:
        msg = arduino.readline().decode('utf-8')
        print(msg)
        if "5" in msg:
            print("correct message")
            break

    print("Gripper opened")


def main():
    print("------------Configuring Burt-------------\r\n")
    ur = kgr.kg_robot(port=30010, db_host="169.254.178.100")
    # burt = kgr.kg_robot(port=30010,ee_port="COM32",db_host="192.168.1.51")
    print("----------------Hi Burt!-----------------\r\n\r\n")
    arduino = serial.Serial('COM4', 9600)

    print("homed")


    while 1:
        arduino.write(bytes('1', 'utf-8'))
        msg = arduino.readline().decode('utf-8')
        print(msg)
        if "10" in msg:
            print("correct message")
            break



    #get_whisk(arduino)

    #set TCP point
    ur.set_tcp([0,0,0.163,0,0,0])
    calibrate(ur)

    egg_cracking(ur)


    ur.set_tcp([0, 0, 0.163, 0, 0, 0])
    ur.movejl([0, -0.3, 0.21, 0, pi, 0])
    ur.movel_tool([0,0,0,0,0,-pi/4])
    ur.translatejl([-0.03,-0.49, 0.12])
    ur.translatel([-0.03,-0.49, 0.06], vel=0.05)
    ur.translatel([-0.03, -0.31, 0.06], vel=0.05)
    ur.translatel([-0.03, -0.31, 0.2], vel=0.05)
 

    ur.set_tcp([0, 0, 0.163, 0, 0, 0])
    ur.movejl([-0.15, -0.3, 0.21, 0, pi, 0], vel = 1, acc=2)
    ur.movejl([-0.15, -0.3, 0.21, 0, 3*pi/2, 0], vel = 1, acc=2)
    ur.movel_tool([0,0,0,0,0,-pi/4], vel = 1, acc=2)

  
    ur.translatejl([-0.45,-0.47,0.37], vel = 1, acc=2)
    ur.translatejl([-0.45, -0.47, 0.32])

    print("confirm that you are about to move down")
    while 1:
        answer = input()
        if answer == "y":
            break
        else:
            print("not confirmed")

    ur.translatel([-0.46,-0.47,0.245], vel=0.05)
    get_whisk(arduino)
    ur.translatejl([-0.45, -0.47, 0.45])
    ur.translatejl([-0.03, -0.47, 0.45])
    ur.translatel([-0.03, -0.47, 0.225])
    ang = pi/10
    ur.movel_tool([0, 0, 0, 0, 0,ang], vel=2, acc=2)
    for i in range(0,6): #6 in reality
        ur.movel_tool([0, 0, 0, 0, pi/12, -2*ang], vel=2, acc=2)
        ur.movel_tool([0, 0, 0, 0, -pi/12, 2*ang], vel=2, acc=2)

    ur.movel_tool([0, 0, 0, 0, 0, -ang], vel=0.5, acc=1)
    ur.translatejl([-0.03, -0.47, 0.45])
    ur.translatejl([-0.46, -0.47, 0.45])
    open_a_bit(arduino)
    ur.translatel([-0.46, -0.47, 0.27], vel=0.05)

    open_gripper(arduino)

    # goto end of leaving whisk
    ur.translatejl([-0.46, -0.47, 0.27], vel=1)
    ur.translatel([-0.46, -0.47, 0.4], vel=1)


    # MOVE TO GETTING BOWL INITIAL POSITION
    ur.movejl([-0.03,-0.2,0.4,0,pi,0])
    ur.movel_tool([0, 0, 0, 0, 0, pi / 4])
    ur.translatejl([-0.03,-0.25,0.07])
    ur.translatel([-0.03, -0.38, 0.07], vel=0.05)
    ur.translatel([-0.03, -0.33, 0.15])
    ur.movel_tool([0, 0, 0, 0, 0, -pi / 4])
    ur.movel_tool([0,0,0,pi/7,0,0])
    ur.movel_tool([0, 0, 0, 0, 0, -pi / 4])
    ur.translatel([-0.03, -0.41, 0.15], vel=0.05)
    ur.translatel([-0.03, -0.45, 0.06], vel=0.05)
    ur.translatel([-0.03, -0.46, 0.05], vel=0.05)
    get_bowl(arduino)
    ur.translatejl([-0.03, -0.35, 0.1])
    ur.translatejl([0.4, -0.35, 0.15])


    # MOVE BOWL TO ABOVE PAN
    ur.movejl([0.5,-0.4,0.2,0,pi,0])
    ur.movej_rel([0,0,0,pi/4,0,0])
    ur.translatejl([0.6, -0.4, 0.21])
    ur.translatel([0.7, -0.5, 0.21])
    ur.movej_rel([0, 0, 0, pi / 5, 0, 0])
    currpos = ur.getl()
    ur.translatejl([currpos[0], currpos[1], currpos[2]-0.06])
    ur.movej_rel([0, 0, 0, pi / 6, 0, 0])
    currpos = ur.getl()
    ur.translatejl([currpos[0], currpos[1], currpos[2] - 0.06])
    ur.movej_rel([0, 0, 0, pi / 8, 0, 0])
    #time.sleep(2) # NEED THIS TO GET THE EGG OUT
    ur.movej_rel([0, 0, 0, -pi / 8, 0, 0])
    currpos = ur.getl()
    ur.translatejl([currpos[0], currpos[1], currpos[2] + 0.1])
    ur.movej_rel([0, 0, 0, -pi / 4, 0, 0])

    ur.movejl([0.5,-0.3,0.4,0,pi,0], vel=0.6)
    ur.movejl([0, -0.3, 0.2, 0, pi, 0], vel=0.6)
    ur.movejl([0, -0.3, 0.14, 0, pi, 0], vel=0.6)

    for i in range(0,5):
        open_a_bit(arduino)
    
    
    ur.movejl([0, -0.3, 0.07, 0, pi, 0], vel=0.6)
    open_gripper(arduino)
    ur.translatel([0.02, -0.28, 0.3])

    #WE ARE DONE WITH PUTTING THE BOWL DOWN


    ur.set_tcp([0, 0, 0.163, 0, 0, 0])

    ur.movej([-pi/2,-pi/3,-pi/2,-pi/2,0,5*pi/4], vel=1)
    ur.movej_rel([pi/2,0,0,0,0,0])
    ur.movej_rel([0, 0, -pi/4, 0, 0, 0])

    ur.translatejl([0.2,-0.5,0.2])
    ur.movel_tool([0,0,0,0,0,-pi + 0.2])
    ur.translatejl([0.2, -0.58, 0.06])
    print("confirm that you are about to move accross")
    while 1:
        answer = input()
        if answer == "y":
            break
        else:
            print("not confirmed")

    ur.translatel([0.4, -0.58, 0.07], vel=0.4)
    close_pan(arduino)
    ur.movel_tool([0,0,0,0,0,pi/5], vel=0.1)
    ur.translatejl([0.3,-0.58, 0.2], vel =0.1)

    time.sleep(1)
    ur.translatejl([0.1,-0.58, 0.07])
    ur.translatejl([0.1, -0.45, 0.07])

    ur.movel_tool([0, 0, 0, 0, 0, -pi / 5], vel=0.1)
    open_gripper(arduino)
    ur.translatejl([0, -0.45, 0.07], vel = 0.1)

    ur.close()


if __name__ == '__main__': main()
