# OmeletteBot

### Operating the robot
####UR5:
`/python/omelette.py` is the main script used to control the UR5 arm for this experiment. It contains the instructions for the UR5 arm as well as communication between the Arduino UNO to time the gripper. 

The interfacing program between this script and the UR5 control box is provided thorugh `<link>` : <https://github.com/kg398/Generic_ur5_controller>, a python interface to a general purpose UR5 controller, using the APIs provided by Universal Robotics. 

The sequence of movements can be manipulated in the main() function, with various input parameters to controll each sequence. Some of these input parameters correspond to those used in the optimisation process. 



####Arduino:
`/Arduino/Gripper_2_handler/Gripper_2_handler.ino` provides the arduino controller for the gripper. The controller handles, 1) collision between the "fingers" with the outer walls and itself through a position feedback from a linear potentiometer, 2) various gripping methods dependent on applied force, and 3) error handling for debugging the gripper. 


### Performing the optimisation
####Sequential BO:
For sequential BO, the two python scripts can be found in `/python/Optimisation`. `Sequential_BayesianOptimisation_Appearance.py` performs sequential BO for the Appearance and Texture outupt based on the inputs: whisking, mixing, and cooktime. It can load logs of previous optimisation data to base the subsequent iterations on that. A similar script  `Sequential_BayesianOptimisation_Flavour.py`is used to perform sequential BO for the Flavour output based on the inputs: salt, pepper, and mixing. 

Both scripts have the ability to sanity check/debug the optimiser by using a simulated function mapping the inputs to the output. 
####Batch BO:
For batch BO, the python script to generate the random input data and to record the values during the experiment thcan be found in `/python/Optimisation/bulk_BayesianOptimisation.py`. To perform the optimisation process, which is the guassian curve fitting, this matlab script is used `/matlab/opts.m`
