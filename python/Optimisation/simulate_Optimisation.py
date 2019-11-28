'''
The python script use as a method to sanity check and debug the BO system

A number of simulated functions mapping the input to the output was used to
see if the optimiser is performing reasonably. 


Edited by Kai Junge
'''


from bayes_opt import BayesianOptimization, UtilityFunction
from bayes_opt.observer import JSONLogger
from bayes_opt.event import Events
from bayes_opt.util import load_logs
import numpy as np 
import matplotlib.pyplot as plt
import json
from scipy.stats import multivariate_normal
from mpl_toolkits.mplot3d import Axes3D
import random
import math


experiments = 2
simulation = False
AT_noise = 0.2

# ----------------------------------------------------------------------------------
# ---------------  DEFINE FUNCTIONS HERE -------------------------------------------
# ----------------------------------------------------------------------------------

# 1 dimensional gaussian function
def one_dim_gaussian(pos, mu, var, amplitude):
    return amplitude * np.exp(-np.power(pos - mu, 2.) / (2 * var))

# 2 dimensional gaussian function
# Example: two_dim_gaussian(pos = [3,4], mu_x=0, mu_y0, var_x=20, var_y=20, amplitude=1)
def two_dim_gaussian(pos, mu_x, mu_y, var_x, var_y, amplitude):
    raw_value = multivariate_normal([mu_x, mu_y], [[var_x, 0], [0, var_y]])
    scaling = 1/raw_value.pdf([mu_x,mu_y])
    return amplitude * scaling * raw_value.pdf([pos[0], pos[1]])

# Simple saturating function. Const is the characteristic constant: 1-exp(-x/const)
def saturating_function(pos, const, amplitude):
    return amplitude*(1-math.exp(-1*pos/const))

# Time varying random noise (A* exp(t/iteration - 1) )
def noise(t, iteration, amplitude):
    return amplitude*math.exp((t/iteration)-1)


# Function for Appearence and Texture value
def appearance_and_texture(whisking, mixing, cooktime, iteration, simulation = simulation):

    # function if simulation is being used
    if simulation:

        print("cooktime", cooktime)

        #Make all the variables so their ranges are 0~1
        mixing = mixing/10
        whisking = whisking/12
        cooktime = cooktime/10

        print(cooktime)
        # Find amplitude of noise
        random_amplitude = noise(iteration, 10, AT_noise)

        # Calculate the output for T and A
        cooktime_result = one_dim_gaussian(cooktime, 0.2, 0.2, 1.5) + one_dim_gaussian(cooktime, 0.5, 0.4, 0.5)
        whisking_result = saturating_function(whisking, 0.5, 0.5)  + saturating_function(whisking, 0.5, 1.5)
        mixing_result = one_dim_gaussian(mixing, 0.9, 0.5, 0.5) + one_dim_gaussian(mixing, 0.7, 0.4, 0.5)


        print(round(cooktime_result,3), round(whisking_result, 3), round(mixing_result, 3))

        total = cooktime_result + mixing_result + whisking_result

        return total + random_amplitude*2*(random.random()-0.5), total

    # if input from person
    else:
        print("Enter result for APPEARANCE + TEXTURE")
        while 1:
            try: 
                A_and_T = int(input())
                break
            except:
                print("please enter integer")
        
        print("Wait until search is compelte\n")
        return A_and_T


# Bounded region of parameter space
ATBound = {'whisking': (0, 12), 'cooktime': (0, 10), 'mixing': (2, 4) }

dataStore = {'mixing': [], 'whisking': [], 'cooktime': []}

def omelette_optimisation():
    global dataStore

    AT_optimiser = BayesianOptimization(
        f=appearance_and_texture,
        pbounds=ATBound,
        verbose=2, # verbose = 1 prints only when a maximum is observed, verbose = 0 is silent
        random_state=random.randint(0,10000),
    )


    AT_optimiser.set_gp_params(alpha = 10)
    AT_optimiser.set_gp_params(normalize_y = False)

    load_logs(AT_optimiser, logs=["./ATlogs.json"])

    print(print(AT_optimiser.max))

    input()

    ATutility = UtilityFunction(kind="ucb", kappa=1, xi=1e-4)

    ATlogger = JSONLogger(path="./ATLogs_second.json")
    AT_optimiser.subscribe(Events.OPTMIZATION_STEP, ATlogger)

    print("------------------ STARTING SEARCH -------------------")
    print("\n\n\n")
    for i in range(experiments):

        AT_next_point = AT_optimiser.suggest(ATutility)

        dataStore['mixing'].append(AT_next_point['mixing'])
        dataStore['whisking'].append(AT_next_point['whisking'])
        dataStore['cooktime'].append(AT_next_point['cooktime'])

        print("Iteration Number: ", i+1)
        print(AT_next_point)

        for item in AT_next_point:
            AT_next_point[item] += random.randint(0,1000) * 0.00001
            if item == "cooktime":
                print(item, "  ", round(AT_next_point[item]*30 + 210))
            else:
                print(item, "  ", round(AT_next_point[item]))
        
        plot_current_status(i+1)

        AT_target = appearance_and_texture(**AT_next_point, iteration= i+1)

        if simulation == False:
            AT_optimiser.register(params=AT_next_point, target=AT_target)
        else:
            AT_optimiser.register(params=AT_next_point, target=AT_target[0])
        
        print("\n")

def plot_current_status(iteration):
    global dataStore

    print("live plotting")
    print(iteration)
    x_axis = np.linspace(1, iteration, iteration)

    for i, item in enumerate(dataStore, 321):
        plt.subplot(i)
        plt.ylabel(item)
        plt.scatter(x_axis, dataStore[item], s = 20, c = 'blue', marker = ".")
        plt.yticks(np.arange(0, 12, step=2))

    plt.suptitle("Experiment 2 - Optimise Appearance and Texture")
    plt.show()

    #print(flavour_optimiser.max)

    

if __name__ == "__main__":
    omelette_optimisation()