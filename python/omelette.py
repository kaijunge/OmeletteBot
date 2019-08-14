import time
import datetime
import serial
from math import pi, sqrt, sin, cos
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
restart = 0
normalGrip = 1
mediumGrip = 2
hardGrip = 3
openMM = 4
closeMM = 5
gripInCentre = 6
openGripper = 7
lightGrip = 8
fastArmOnlyGrip = 9

timeToHeat_offset = 24.088
timeToLiftPan_offset = 8


### -----------------------------------------------------###
### ------------ -Defining Global Varialbles-------------###
disableGripper = False
cookingTimer = 0
dishTimer = 0


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
            print(msgFromArduino)
            if "Complete" in msgFromArduino:
                print("Arduino Command Complete")
                return 0
            if "Error" in msgFromArduino:
                print("Error with gripper!!")
                return 1

def translatel_rel(arthur, x, y, z, velocity = 0.5, accel = 0.5, linear = True):
    currpos = arthur.getl()

    if linear:
        arthur.translatel([currpos[0]+x, currpos[1]+y, currpos[2]+z], vel=velocity, acc=accel)
    else:
        arthur.translatejl([currpos[0] + x, currpos[1] + y, currpos[2] + z], vel=velocity, acc=accel)

# move the TCP in an eliptical path in the xy plane
def move_elipse(arthur, x_amplitude = 0.05, y_amplitude = 0.05, min_timestep = 0.05, number_of_turns = 1):
    global cookingTimer
    startpos = arthur.getl()

    max_step = 200
    pos = [[0] * 6 for i in range(max_step)]
    sine = []
    cosine = []
    for i in range(0, max_step):
        sine.append(sin(i * (2 * pi / max_step)) * x_amplitude)
        cosine.append(cos(i * (2 * pi / max_step)) * y_amplitude)

        for j in range(2, 6):
            pos[i][j] = startpos[j]
        pos[i][0] = sine[i] + startpos[0]
        pos[i][1] = cosine[i] + startpos[1]
        # print(pos[i][0])

    arthur.movejl(pos[0], vel=1, acc=2)

    factor = 100 / max_step
    dt_initial = 0.6 * factor
    dt_minimum = min_timestep * factor
    timeGain = 0.03 * factor

    for j in range(0, number_of_turns):

        newtime = time.time()

        for i in range(0, max_step):
            global cookingTimer
            if i < max_step / 2:
                if j == 0:
                    dt = dt_initial - (i * timeGain) ** 0.4
                else:
                    dt = dt_minimum
            else:

                if j == number_of_turns - 1:
                    dt = dt_initial - ((max_step - i) * timeGain) ** 0.5
                else:
                    dt = dt_minimum


            if dt < dt_minimum:
                dt = dt_minimum

            arthur.servoj(pos[i], control_time=dt, lookahead_time=0.008, gain=300)


    arthur.movejl(startpos, vel= 0.1)



# Opening the egg
def open_egg(arthur, eggs = 2, debug = False):
    if debug:
        input()


    arthur.movej_rel([0, 0, 0, 0, -pi, 0], vel=3, acc=3)
    arthur.set_tcp([0, 0, -0.17, 0, 0, 0])
    # arthur.movel_tool([0, 0, 0, -pi / 16, 0, 0])
    arthur.translatejl([-0.03, -0.4, 0.17], vel = 1, acc = 2)

    for i in range(eggs):
        arthur.translatel([-0.055, -0.56, 0.17], vel=0.3)

        time.sleep(1)
        if debug:
            input()

        arthur.translatel([-0.055, -0.5, 0.17], vel=1)
        arthur.translatel([-0.11, -0.5, 0.17], vel=1)
        arthur.translatel([-0.11, -0.60, 0.17], vel=0.1)

        time.sleep(1)

        arthur.translatel([-0.03, -0.4, 0.17], vel=1)

        if i != eggs-1:
            input()

    if debug:
        input()

    arthur.home(vel = 2, acc = 2)

'''
#Getting the egg opener
#### NOT DONE!!!
def take_out_shell(arthur, debug = False):
    arthur.home(acc=1, vel=2)
    arthur.set_tcp([0, 0, 0.163, 0, 0, 0])
    currpos = arthur.getl()
    arthur.movejl([currpos[0],currpos[1], currpos[2], pi / 2, 0, 0], vel=0.5, acc = 2)
    arthur.translatejl([currpos[0] - 0.15, -0.66, currpos[2]], vel=2, acc =1)
    translatel_rel(arthur, 0,0,-0.255)
    arthur.movel_tool([0,0,0,0,0,pi/2])
    translatel_rel(arthur, 0, -0.07, 0)

    if debug:
        input()
    translatel_rel(arthur, 0,0,0.11, velocity = 0.3)

    arthur.movel_tool([0, 0, 0, 0, 0, -pi / 11], vel = 0.1)

    gripperAction(hardGrip)

    if debug:
        input()
    arthur.movel_tool([0, 0, 0, 0, 0, pi / 11], vel=0.05)
    if debug:
        input()
'''

def pour_egg(arthur, waiTime = 30, continous = True, debug = False):
    global cookingTimer, dishTimer
    gripperAction(openGripper)

    realWaitTime = waiTime - timeToHeat_offset

    if time.time() - realWaitTime > 0:
        time.sleep(realWaitTime)

    if debug:
        input()

    arthur.set_tcp([0, 0, 0.163, 0, 0, 0])

    ### ----------- GO TO BOWL GRASPING POSITION
    arthur.movejl([-0.02, -0.5, 0.15, 0, pi, 0], vel=2, acc=2)
    arthur.movel_tool([0, 0, 0, 0, 0, pi / 2], vel=1)
    arthur.movel_tool([0, 0, 0, 0, -pi / 12, 0], vel=1)

    ### ----------- LOWER DOWN THE GRIPPER AND GRASP
    translatel_rel(arthur, 0, -0.03, -0.11, velocity=0.1)

    if debug:
        input()

    gripperAction(fastArmOnlyGrip)
    gripperAction(normalGrip)

    ### ----------- GET BOWL OUT OF HOLDER TO MID AIR
    translatel_rel(arthur, 0, 0.1, 0, velocity=1)
    gripperAction(mediumGrip)
    translatel_rel(arthur, 0, 0.1, 0.2, velocity=1)

    ### ----------- MOVE TO POURING POSITION
    arthur.movel_tool([0, 0, 0, 0, pi / 12, 0], vel=2)

    if debug:
        input()

    arthur.movel_tool([0, 0, 0, 0, 0, 3*pi / 4], vel=1)
    arthur.translatejl([0.47, -0.45, 0.22], vel=0.5, acc = 1.5)

    if debug:
        input()

    arthur.movej_rel([0,0,0,pi/4, 0,0], vel=0.2, acc= 2)
    #arthur.movel_tool([0,0,0,0,10*pi/20, 0], vel=0.3)

    translatel_rel(arthur, 0.05, -0.04, -0.11, velocity=1, accel=2)
    if debug:
        input()

    arthur.movej_rel([0, 0, 0, pi / 6, 0, 0], vel=3, acc=2)
    translatel_rel(arthur, 0,0,-0.1, velocity=2,  accel=2)

    arthur.movej_rel([0, 0, 0, pi / 6, 0, 0], vel=3, acc=2)

    dishTimer = time.time()
    time.sleep(1)

    arthur.movej_rel([0, 0, 0, -pi / 4, 0, 0], vel=4, acc=4)

    translatel_rel(arthur, 0,0,0.16, velocity=1, accel=2)

    arthur.movej_rel([0, 0, 0, -pi / 4, 0, 0], vel=4, acc=4)
    #arthur.movel_tool([0, 0, 0, 0, -10*pi/20, 0], vel=0.4)
    #arthur.movel_tool([0, 0, 0, 0, 0, - pi / 2], vel=0.2, acc=3)

    if debug:
        input()

    translatel_rel(arthur, 0, 0.05, 0, velocity=1)
    arthur.movejl([-0.02, -0.3, 0.15, (sqrt(0.5) * pi), (sqrt(0.5) * pi), 0], vel=3, acc=2)

    ### ----------- ALIGNED WITH BOWL RETURN SITE, ABOUT TO MOVE FORWARDS
    if debug:
        input()

    translatel_rel(arthur, 0, -0.18, -0.06, velocity=1)
    gripperAction(openGripper)

    if debug:
        input()

    translatel_rel(arthur, 0, 0, -0.045, velocity=1)
    translatel_rel(arthur, 0, -0.045, 0, velocity=1)

    ### ----------- GET GRIPPER OUT OF THE BOWL
    translatel_rel(arthur, 0, 0.01, 0, velocity=0.3)
    arthur.movel_tool([0, 0, 0, 0, -pi / 16, 0], vel=1)
    translatel_rel(arthur, 0, 0.01, 0.1, velocity=1)

    if continous:
        currpos = arthur.getl()
        arthur.movejl([currpos[0], currpos[1], currpos[2], 0, pi, 0], vel= 3, acc=4)

    else:
        arthur.home(vel=2, acc=2)


def move_pan_to_hob(arthur, continous = False, debug = False):
    global cookingTimer
    arthur.set_tcp([0, 0, 0, 0, 0, 0])

    if debug:
        input()

    arthur.translatejl([0.17, -0.4, 0.25], vel =2, acc = 2)
    translatel_rel(arthur, 0,0,-0.13, velocity = 0.05)

    if debug:
        input()

    gripperAction(hardGrip)

    liftheight = 0.12
    intiallift = 0.03
    translatel_rel(arthur, 0, 0, intiallift, velocity=0.05)
    arthur.movej_rel([0, 0, 0, 0, 0, pi / 4], vel=1, acc = 2)
    translatel_rel(arthur, 0, 0, liftheight - intiallift, velocity=0.05)
    arthur.movej_rel([0, 0, 0, 0, 0, pi / 2], vel=1, acc = 2)
    if debug:
        input()
    arthur.translatejl([0.43, -0.395, 0.13 + liftheight], vel=1, acc = 1)
    translatel_rel(arthur, 0, 0, -1*liftheight + 0.01, velocity=0.05)

    cookingTimer = time.time()
    if debug:
        input()

    gripperAction(openGripper)

    translatel_rel(arthur, 0, 0, 0.10, velocity=0.5)
    arthur.movej_rel([0, 0, 0, 0, 0, -3*pi / 4], vel=2, acc = 2)

    print(arthur.getl())

    if continous == False:
        arthur.translatejl([0.3, -0.3, 0.3], vel = 1)
        arthur.home()

    print(time.time() - cookingTimer)

def move_in_pan(arthur, continous = False, turns = 10, twoTunrsAsSet = True, debug = False):
    global cookingTimer
    arthur.set_tcp([0, 0, 0, 0, 0, 0])
    if debug:
        input()


    arthur.movejl([0.27, -0.495, 0.35, -0, pi, 0], vel = 3, acc=3)
    translatel_rel(arthur, 0, -0.10, -0.15, velocity=2, accel=2)

    translatel_rel(arthur, 0, 0, -0.065, velocity=0.5)

    gripperAction(mediumGrip)

    translatel_rel(arthur, 0,0,0.1, velocity=1)

    if debug:
        input()

    arthur.movejl([0.43, -0.395, 0.35, -0, pi, 0], vel=1, acc= 2)


    if debug:
        input()

    arthur.movej_rel([0,0,0,-pi/2, -3*pi/4, 3*pi/4], vel = 3, acc = 3)
    currpos = arthur.getl()
    arthur.movejl([currpos[0], currpos[1], currpos[2], 0, (sqrt(0.5) * pi), -sqrt(0.5) * pi], vel=2, acc=2)


    translatel_rel(arthur, 0.21, -0.01, -0.14)
    arthur.force_move([0, 0, -0.1], force=13, vel=0.05)
    translatel_rel(arthur, 0 , 0, 0.003)

    print(time.time() - dishTimer)
    if debug:
        input()

    speed = 0.03
    amplitude = 0.06
    # move_elipse(arthur, x_amplitude=amplitude/3, y_amplitude=amplitude, min_timestep=speed, number_of_turns=1)
    # move_elipse(arthur, x_amplitude=amplitude, y_amplitude=amplitude/3, min_timestep=speed, number_of_turns=1)

    singleCount = 0
    setCount = 0
    while 1:
        move_elipse(arthur, x_amplitude=amplitude, y_amplitude=amplitude, min_timestep=speed, number_of_turns=1)
        singleCount += 1
        if not twoTunrsAsSet and singleCount == turns:
            break
        move_elipse(arthur, x_amplitude=amplitude / 2, y_amplitude=amplitude / 2, min_timestep=speed, number_of_turns=1)
        singleCount += 1;
        setCount += 1
        if (not twoTunrsAsSet and singleCount == turns) or twoTunrsAsSet and setCount == turns:
            break

    translatel_rel(arthur, 0, 0, 0.1)


    if debug:
        input()

    currpos = arthur.getl()
    arthur.movejl([currpos[0], currpos[1], currpos[2], 0, pi, 0], vel=2, acc=2)

    arthur.movejl([0.27, -0.495, 0.35, -0, pi, 0], vel=0.1)
    translatel_rel(arthur, 0, -0.104, -0.16, velocity=0.1)


    gripperAction(openGripper)

    translatel_rel(arthur, 0, 0.10, 0.15, velocity=0.1)

    if not continous:
        arthur.home(vel= 2, acc = 2)

def serve_dish(arthur, waitForDish = 1, debug = False):
    global dishTimer
    arthur.set_tcp([0, 0, 0, 0, 0, 0])
    if debug:
        input()


    arthur.movej_rel([0, 0, 0, 0, 0, 3 * pi / 4], vel=3, acc = 3)
    if debug:
        input()

    arthur.translatejl([0.43, -0.395, 0.45], vel=0.3, acc=1)


    realWaitTime = waitForDish - timeToLiftPan_offset
    while 1:
        remainingTime = realWaitTime - (time.time() - dishTimer)
        print(remainingTime)
        if remainingTime <= 0:
            break

    translatel_rel(arthur, 0, 0, -0.309, velocity=0.1)

    gripperAction(hardGrip)

    print(time.time() - cookingTimer)
    if debug:
        input()

    translatel_rel(arthur, 0, 0, 0.25, velocity=0.1)

    translatel_rel(arthur, 0, 0.2, 0, velocity=0.1)

    translatel_rel(arthur, 0,0,-0.25, velocity=0.1)

    '''
    arthur.movej_rel([0, 0, 0, 0, 0, -pi / 4], vel=2, acc = 2)

    translatel_rel(arthur, -0.8, 0, 0, velocity=0.5, accel = 1.5)

    translatel_rel(arthur, 0, 0.1, 0, velocity=0.1)

    if debug:
        input()

    translatel_rel(arthur, 0, 0.1, -0.15, velocity=0.1)
    arthur.set_tcp([0, 0, 0.13, 0, 0, 0])
    arthur.movel_tool([0,0,0, 0,7*pi/12,0], vel=0.1)

    time.sleep(1)

    arthur.movel_tool([0, 0, 0, 0, -7 * pi / 12, 0], vel=0.2)

    translatel_rel(arthur, 0,0,0.13, velocity=1)

    arthur.set_tcp([0, 0, 0, 0, 0, 0])

    translatel_rel(arthur, 0.8, 0,0, velocity=0.5)

    arthur.movej_rel([0, 0, 0, 0, 0, pi / 4], vel=2, acc=2)

    translatel_rel(arthur, 0, 0, -0.23, velocity=0.1)
    '''

    gripperAction(openGripper)

    translatel_rel(arthur, 0, 0, 0.2, velocity=0.1)

    arthur.home()


    #arthur.movej_rel([0, 0, 0, 0, 3*pi / 4, 0], vel=1)

def operate_hob(arthur, debug = False):
    arthur.set_tcp([0, 0, 0.163, 0, 0, 0])

    if debug:
        input()

    arthur.translatejl([0.6, -0.3, 0.2], vel=1)
    arthur.movej_rel([0,0,0,0,-pi/2,pi], vel = 1)
    arthur.movej([0, -4*pi/6, -pi/2, -5*pi/6, 0, 3*pi/2], vel = 1)

    arthur.set_tcp([-0.09, -0.013, 0.01, 0, 0, 0])

    if debug:
        input()

    translatel_rel(arthur, 0.185, 0, -0.02, velocity=0.05)
    translatel_rel(arthur, 0, 0, -0.065, velocity=0.05)
    #currpos = arthur.getl()
    #arthur.translatel([currpos[0], currpos[1], currpos[2] - 0.02], vel = 0.05)

    arthur.home(vel = 0.2)


def move_cracker_away(arthur, debug = False):

    if debug:
        input()

    arthur.home(acc=1, vel=2)
    arthur.set_tcp([0, 0, 0.163, 0, 0, 0])


    arthur.movej_rel([0,0,0,0,-pi,0], vel = 2, acc = 2)
    currpos = arthur.getl()
    arthur.movejl([currpos[0]+0.035, currpos[1]-0.35, currpos[2]-0.65, pi / 2, 0, 0], vel=2)

    if debug:
        input()

    translatel_rel(arthur, 0,-0.1, 0, velocity=0.05)
    gripperAction(mediumGrip)
    translatel_rel(arthur, 0, 0, 0.15, velocity=0.4)
    translatel_rel(arthur, 0.05, -0.13, 0, velocity=0.4)
    translatel_rel(arthur, 0, 0, -0.065, velocity=0.1)

    gripperAction(openGripper)

    print(arthur.getl())

    translatel_rel(arthur, 0, 0.2, 0, velocity=2)
    arthur.home(vel=2, acc=2)


def retreive_cracker(arthur, debug = False):
    arthur.set_tcp([0, 0, 0.163, 0, 0, 0])

    if debug:
        input()

    arthur.movej_rel([0, 0, 0, 0, -pi, 0], vel=2, acc=2)
    arthur.movejl([-0.01, -0.8, 0.415, pi / 2, 0, 0], vel=2)
    translatel_rel(arthur, 0,-0.09, 0, velocity=0.01)

    if debug:
        input()

    gripperAction(mediumGrip)
    translatel_rel(arthur, 0, 0, 0.065, velocity=0.1)
    translatel_rel(arthur, -0.05, 0.14, 0, velocity=0.1)
    arthur.movej_rel([0,0,0,0,0,-pi/12], vel=1)
    translatel_rel(arthur, 0, 0, -0.07, velocity=0.05)
    gripperAction(openGripper)
    arthur.movej_rel([0, 0, 0, 0, 0, pi / 12], vel=1)
    translatel_rel(arthur, 0, 0, -0.03, velocity=0.05)
    translatel_rel(arthur, -0.035, 0, 0, velocity=0.05)
    translatel_rel(arthur, 0.1, 0.2, 0, velocity=0.05)

    arthur.home(vel = 2, acc = 2)

def whisking(arthur, waitTime = 1, debug = False):
    print("Whisking with new whisking device")
    arthur.set_tcp([0, 0, 0, 0, 0, 0])
    if debug:
        input()

    arthur.translatejl([-0.29,-0.58,0.25], vel = 2.5, acc=2)
    if debug:
        input()
    translatel_rel(arthur, 0.009, -0.02, -0.106, velocity=0.2 )


    if debug:
        input()

    arthur.force_move([0, -0.1, 0], force=40, vel=0.1)
    translatel_rel(arthur, 0, 0.01, -0.008, velocity=0.2)

    if debug:
        input()

    gripperAction(hardGrip)

    translatel_rel(arthur, 0, 0, 0.05, velocity=0.2)

    arthur.translatejl([-0.3,-0.5, 0.5], vel = 2, acc = 2)

    arthur.movej_rel([0,0,0,-pi/2,-pi, pi], vel =2, acc = 2)


    currpos = arthur.getl()
    arthur.movejl([currpos[0],currpos[1], currpos[2], 0, (sqrt(0.5)*pi), -sqrt(0.5)*pi], vel =2, acc = 2)

    arthur.translatejl([-0.01,-0.4,0.35], vel = 2, acc = 2)

    translatel_rel(arthur, 0, -0.105, 0, velocity= 1)

    if debug:
        input()

    heightdrop = 0.165 #0.15
    translatel_rel(arthur, 0, 0, -1*heightdrop, velocity=0.1, accel = 2)



    ##### WHISKING ACTION HEREE!!!!
    #move_elipse(arthur, x_amplitude=0.03, y_amplitude=0.03, min_timestep=0.0075, number_of_turns=10)

    time.sleep(waitTime)


    translatel_rel(arthur, 0, 0, heightdrop, velocity=2, accel=2)
    translatel_rel(arthur, 0, 0.13, 0, velocity=1)

    arthur.movej_rel([0,0,0,pi/2,5*pi/6,-pi], vel = 2, acc = 2)

    currpos = arthur.getl()
    arthur.movejl([currpos[0]-0.2, currpos[1]+0.05, currpos[2], 0, pi, 0], vel=2, acc = 2)
    ## PLACE TO switch on/off GRIPPER


    arthur.translatejl([-0.283, -0.608, 0.25], vel=1)

    if debug:
        input()

    translatel_rel(arthur, 0, 0, -0.09, velocity=0.1)


    if debug:
        input()

    arthur.force_move([0, -0.1, 0], force=40, vel=0.1)
    translatel_rel(arthur, 0, 0.01, 0, velocity=0.2)
    translatel_rel(arthur, 0, 0, 0.01, velocity=0.2)
    translatel_rel(arthur, 0, 0, -0.02, velocity=0.2)

    if debug:
        input()

    gripperAction(openGripper)

    if debug:
        input()
    translatel_rel(arthur, -0.008, 0, 0, velocity=0.1)
    translatel_rel(arthur, 0, 0.02, 0, velocity=0.2)
    translatel_rel(arthur, 0.0, 0, 0.15, velocity=0.1)
    arthur.home()

def seasoning_motion(arthur, debug = False, shakes=3, pepper = True):
    if debug:
        input()
    translatel_rel(arthur, 0,-0.07, 0, velocity=0.05)
    # CLOSE GRIPPER HERE
    gripperAction(mediumGrip)
    translatel_rel(arthur, 0, 0, 0.02, velocity=0.05)
    translatel_rel(arthur, 0, 0.12, 0, velocity=1)
    arthur.translatejl([-0.03, -0.4, 0.45], vel=2, acc=2)

    if debug:
        input()

    arthur.movej_rel([0,0,0,0,0,pi/2], vel = 2, acc = 3)
    translatel_rel(arthur,0.05,-0.1, -0.12, velocity = 3, accel = 3)
    if debug:
        input()

    if pepper:
        arthur.movej_rel([0, 0, 0, 0, 0, pi / 2], vel=2, acc=4)
        ### PEPPER MOTION HEERE!!!
        for i in range(shakes-1):
            arthur.movej_rel([0,0,0,0,0,-pi], vel = 6, acc = 6)
            time.sleep(0.5)
            arthur.movej_rel([0, 0, 0, 0, 0, pi], vel=6, acc=6)
            time.sleep(0.5)

        arthur.movej_rel([0, 0, 0, 0, 0, -pi], vel=2, acc=4)

    else:
        arthur.movej_rel([0, 0, 0, 0, 0, pi / 4], vel=2, acc=5)
        ### SALT MOTION HEERE!!!
        for i in range(shakes-1):
            arthur.movej_rel([0, 0, 0, 0, 0, -pi/2], vel=5, acc=5)
            arthur.movej_rel([0, 0, 0, 0, 0, pi/2], vel=5, acc=5)
            time.sleep(0.5)

        arthur.movej_rel([0, 0, 0, 0, 0, -3*pi/4], vel=2, acc=4)



    arthur.translatejl([-0.03, -0.5, 0.45], vel=2, acc = 3)

    if debug:
        input()

def get_salt_and_pepper(arthur, salt = 1, pepper = 1, debug = False):
    arthur.set_tcp([0, 0, 0, 0, 0, 0])

    if debug:
        input()

    arthur.movej_rel([0,0,0,pi/2, 0,0], vel = 3, acc = 2)
    currpos = arthur.getl()
    ## GET CLOSER ONE
    arthur.movejl([0.29, -0.57, 0.355, 0, (sqrt(0.5) * pi), -sqrt(0.5) * pi], vel=2, acc = 2)

    if debug:
        input()
    seasoning_motion(arthur, shakes = pepper, debug=False, pepper=True)

    if debug:
        input()

    arthur.translatejl([0.305, -0.65, 0.365], vel = 2)
    arthur.force_move([0, 0, -0.1], force=30, vel=0.05)

    # OPEN GRIPPER HERE
    gripperAction(openGripper)

    if debug:
        input()

    ## NOW MOVING TO GET THE FURTHER SEASONING
    translatel_rel(arthur, 0, 0, 0.01, velocity=0.05)
    translatel_rel(arthur, 0,0.1, 0.02, velocity=0.05)
    currpos = arthur.getl()
    arthur.movejl([0.39, -0.57, 0.355, 0, (sqrt(0.5) * pi), -sqrt(0.5) * pi], vel=2, acc=2)

    seasoning_motion(arthur, shakes = salt, debug=False, pepper=False)

    arthur.translatejl([0.39, -0.57, 0.365], vel=2, acc = 1.5)
    arthur.translatejl([0.405, -0.65, 0.365], vel=1)
    arthur.force_move([0, 0, -0.1], force=30, vel=0.05)

    #OPEN GRIPPER HERE!!
    gripperAction(openGripper)

    translatel_rel(arthur, 0, 0, 0.01, velocity=0.05)
    translatel_rel(arthur, 0, 0.1, 0.02, velocity=0.05)
    translatel_rel(arthur, -0.1, 0.2, 0.02, velocity=2)
    arthur.home(vel = 2, acc = 2)

def push_oil(arthur, pushes = 2, debug = True):
    arthur.set_tcp([0, 0, 0.163, 0, 0, 0])

    if debug:
        input()

    arthur.translatejl([0.21, -0.06, 0.15], vel = 3, acc = 2)

    for i in range(pushes):
        translatel_rel(arthur, 0,0,-0.037, velocity = 0.05)
        time.sleep(0.2)
        translatel_rel(arthur, 0, 0, 0.037, velocity=0.05)
        time.sleep(0.2)

    arthur.home(vel = 2, acc = 2)

def main():
    global cookingTimer
    print("------------Configuring Arthur-------------\r\n")
    arthur = kgr.kg_robot(port=30010, db_host="169.254.50.100")
    print("----------------Hi Arthur!-----------------\r\n\r\n")


    gripperAction(restart)
    push_oil(arthur, pushes = 4, debug=False)
    open_egg(arthur, eggs = 2)
    move_cracker_away(arthur, debug = False)
    get_salt_and_pepper(arthur, salt = 4, pepper = 5, debug=False)
    whisking(arthur, waitTime=4, debug=False)
    move_pan_to_hob(arthur, continous=True, debug=False)
    pour_egg(arthur, waiTime=45, continous=True, debug=False)
    move_in_pan(arthur, continous=True, turns=8,twoTunrsAsSet = False, debug=False)
    serve_dish(arthur,waitForDish=360, debug=False)


    arthur.close()

if __name__ == '__main__': 
    arduino = serial.Serial('COM4', 115200)
    main()