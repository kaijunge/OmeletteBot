'''
The python script used when performing bulk bayesian optimsaion. 

The curvefitting functions as well as simulation functions are under development. 
For the experiment, two simple functions were used: 
produceRandom() -> to produce the semi-random input data scattering farily uniformly in the input searchspace
bulkBayesian() -> a method or recording the outputs of the subjects

The matlab code, opts.m in the same github directory was used to essentially curve fit the data 

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
from scipy.spatial.distance import euclidean
from scipy.optimize import curve_fit

# ----------------------------------------------------------------------------------
# ---------------  DEFINE VARIABLES HERE -------------------------------------------
# ----------------------------------------------------------------------------------

experiments = 10
simulation = False
cosntantNoise = False
timeVaryingNoise = False
discrete = True
output_Amplitude = 10
flavourNoise = output_Amplitude*0.15
AT_noise = output_Amplitude*0.15
const_noise = output_Amplitude*0.1
MixingWithFlavour = True
sequentialRandom = False


# Bounded region of parameter space
FBound = {'salt': (0, 10), 'pepper': (0, 10), 'mixing': (0, 10) }

ATBound = {'whisking': (0, 12), 'cooktime': (0, 10), 'mixing': (0, 10) } #scaled from 210~510 to 0~10

dataStore = {'salt': [], 'pepper': [], 'mixing': [], 'whisking': [], 'cooktime': []}

flavour_record = []

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

# Function for flavour value
def flavour(salt, pepper, mixing, iteration,simulation = simulation):

    # simulation mode
    if simulation:
        #Make all the variables so their ranges are 0~1
        salt = salt/10
        pepper = pepper/10
        mixing = mixing/10

        if cosntantNoise and not timeVaryingNoise:
            random_amplitude = const_noise
        elif not cosntantNoise and timeVaryingNoise:
            random_amplitude = noise(iteration, 10, flavourNoise)
        else:
            random_amplitude = 0

        # Calculate the output
        salt_and_pepper_result = two_dim_gaussian([salt, pepper], 1, 0.8, 0.1, 0.1, output_Amplitude* (3/5))
        mixing_result = saturating_function(mixing, 0.3, output_Amplitude * (2/5))

        '''
        salt_and_pepper_result = two_dim_gaussian([salt, pepper], 0.5, 0.5, 0.1, 0.1, 1.5)
        mixing_result = saturating_function(mixing, 0.3, 1)
        '''
        #print(round(salt_and_pepper_result,3), round(mixing_result, 3))

        if discrete:
            return round(salt_and_pepper_result + mixing_result + random_amplitude*2*(random.random()-0.5))/1, salt_and_pepper_result + mixing_result
        else:
            return salt_and_pepper_result + mixing_result + random_amplitude*2*(random.random()-0.5), salt_and_pepper_result + mixing_result

    else:
        print("Enter result for FLAVOUR")
        while 1:
            try: 
                F = int(input())
                break
            except:
                print("please enter integer")
        return F

# Function for Appearence and Texture value
def appearance_and_texture(whisking, mixing, cooktime, iteration, simulation = simulation):

    # function if simulation is being used
    if simulation:

        #print("cooktime", cooktime)

        #Make all the variables so their ranges are 0~1
        mixing = mixing/10
        whisking = whisking/12
        cooktime = cooktime/10

        #print(cooktime)
        # Find amplitude of noise
        if cosntantNoise and not timeVaryingNoise:
            random_amplitude = const_noise
        elif not cosntantNoise and timeVaryingNoise:
            random_amplitude = noise(iteration, 10, AT_noise)
        else:
            random_amplitude = 0

        # Calculate the output for T and A
        cooktime_result = one_dim_gaussian(cooktime, 0.2, 0.2, output_Amplitude/6) + one_dim_gaussian(cooktime, 0.5, 0.4, output_Amplitude/10)
        whisking_result = saturating_function(whisking, 0.5, output_Amplitude/6)  + saturating_function(whisking, 0.5, output_Amplitude * (3/10))
        mixing_result = one_dim_gaussian(mixing, 0.9, 0.5, output_Amplitude/6) + one_dim_gaussian(mixing, 0.7, 0.4, output_Amplitude/10)

        '''
        cooktime_result = one_dim_gaussian(cooktime, 0.2, 0.2, 0.5) + one_dim_gaussian(cooktime, 0.5, 0.4, 0.2)
        whisking_result = saturating_function(whisking, 0.5, 0.5)  + saturating_function(whisking, 0.5, 0.6)
        mixing_result = one_dim_gaussian(mixing, 0.9, 0.5, 0.5) + one_dim_gaussian(mixing, 0.7, 0.4, 0.2)
        '''



        #print(round(cooktime_result,3), round(whisking_result, 3), round(mixing_result, 3))

        total = cooktime_result + mixing_result + whisking_result

        if discrete:
            return round(total + random_amplitude*2*(random.random()-0.5) + random_amplitude*2*(random.random()-0.5))/1, total, 
        else:
            return total + random_amplitude*2*(random.random()-0.5) + random_amplitude*2*(random.random()-0.5), total, 
        
    # if input from person
    else:
        print("Enter result for APPEARANCE + TEXTURE")
        while 1:
            try: 
                A_and_T = float(input())
                break
            except:
                print("please enter float")
        
        print("Wait until search is compelte\n")
        return A_and_T


def writeJson(data, filename):
    with open(filename + '.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=3)
    print("!!Json WRITE complete!!")

def readJson(filename):
    with open(filename + '.json', 'r') as myfile:
        data = myfile.read()

    print("!!Json READ complete!!")
    return json.loads(data)


def produceRandom():

    if sequentialRandom:
        SP_Threshold = 1.0
        MWC_Threshold = 1.0
    else:
        SP_Threshold = 0.45
        MWC_Threshold = 0.45

    data = [0]*10

    data = {"salt": [0]*experiments, "pepper": [0]*experiments, "mixing": [0]*experiments, 
                                    "whisking": [0]*experiments, "cooktime": [0]*experiments}

    sets = {"SPMset": [[0,0,0]]*experiments, "MWCset": [[0,0,0]]*experiments, "distance": [[0,0]]*experiments}


    i = 0
    count = 0
    while 1:
        #print("this is experiment number: ", i+1)
        for item in data:
            newrand = random.random()
            data[item][i] = round(newrand, 3)
        
        sets["SPMset"][i] = [data["salt"][i], data["pepper"][i], data["mixing"][i]]
        sets["MWCset"][i] = [data["mixing"][i], data["whisking"][i], data["cooktime"][i]]

        
        approval = True
        startIndex = 0
        if sequentialRandom and i > 0:
            startIndex = i - 1
        for j in range(startIndex, i):
            SPM_dist = euclidean(sets["SPMset"][i], sets["SPMset"][j])
            MWC_dist = euclidean(sets["MWCset"][i], sets["MWCset"][j])

            sets["distance"][i] = [SPM_dist, MWC_dist]
            if SPM_dist < SP_Threshold:
                approval = False
            if MWC_dist < MWC_Threshold:
                approval = False


        if approval: 
            i +=1 
            count = 0
        else:
            count += 1

        print(count)

        if i == experiments:
            break

    for item in sets["SPMset"]:
        for k in range(3):
            item[k] = round(item[k] * 10)

    for item in sets["MWCset"]:
        item[0] = round(item[0] * 10)
        item[1] = round(item[1] * 12, 2)
        item[2] = round(item[2] * 10, 3)

    writeJson(sets, "randomData")
    #return sets

    
    x = []
    y = []
    z = []
    for item in sets["SPMset"]:
        if type(item) == list:
            x.append(item[0])
            y.append(item[1])
            z.append(item[2])

    print("length = ",len(sets["distance"]), sets["distance"][0])
    for item in sets["distance"]:
        print(item)

 
    plt.scatter(x, y, s=10, c='red', alpha=0.5)
    plt.title('Scatter plot pythonspot.com')
    plt.xlabel('x')
    plt.ylabel('y')
    #plt.show()


    fig = plt.figure()
    ax = Axes3D(fig)

    ax.scatter(x, y, z)
    plt.show()

    
    

def bulkBayesian():

    flavour_output = []
    AT_output = []
    data = readJson("randomData")

    Flavour_Set = {"output": [], "salt": [], "pepper": [], "mixing": []}
    AppearanceTexture_Set = {"output": [], "mixing": [], "whisking": [], "cooktime": []}
    Total_Set = {"output": [], "salt": [], "pepper": [], "mixing": [], "whisking": [], "cooktime": []}

    for i in range(experiments):

        print("\n\nTHIS IS EXPERIMENT: ", i+1, "\n")
        print("salt: ", data["SPMset"][i][0])
        print("pepper: ", data["SPMset"][i][1])
        print("mixing: ", data["SPMset"][i][2])
        print("whisking: ", data["MWCset"][i][1])
        print("cooktime: ", 30*data["MWCset"][i][2] + 210)


        if simulation:
            data["SPMset"][i].append(flavour(data["SPMset"][i][0], data["SPMset"][i][1], data["SPMset"][i][2], i+1)[0])
            data["MWCset"][i].append(appearance_and_texture(data["MWCset"][i][1], data["MWCset"][i][0], data["MWCset"][i][2], i+1)[0])
        else:
            data["SPMset"][i].append(flavour(data["SPMset"][i][0], data["SPMset"][i][1], data["SPMset"][i][2], i+1))
            data["MWCset"][i].append(appearance_and_texture(data["MWCset"][i][1], data["MWCset"][i][0], data["MWCset"][i][2], i+1))
        
        # convert data into feasible format here
        Flavour_Set["output"].append(data["SPMset"][i][3])
        Flavour_Set["salt"].append(data["SPMset"][i][0])
        Flavour_Set["pepper"].append(data["SPMset"][i][1])
        Flavour_Set["mixing"].append(data["SPMset"][i][2])

        AppearanceTexture_Set["output"].append(data["MWCset"][i][3])
        AppearanceTexture_Set["mixing"].append(data["MWCset"][i][0])
        AppearanceTexture_Set["whisking"].append(data["MWCset"][i][1])
        AppearanceTexture_Set["cooktime"].append(data["MWCset"][i][2])


        Total_Set["output"].append(data["SPMset"][i][3] + data["MWCset"][i][3])
        Total_Set["salt"].append(data["SPMset"][i][0])
        Total_Set["pepper"].append(data["SPMset"][i][1])
        Total_Set["mixing"].append(data["SPMset"][i][2])
        Total_Set["whisking"].append(data["MWCset"][i][1])
        Total_Set["cooktime"].append(data["MWCset"][i][2])


        writeJson(data, "finalData")
        writeJson(Flavour_Set, "Flavour_Set")
        writeJson(AppearanceTexture_Set, "AppearanceTexture_Set")
        writeJson(Total_Set, "Total_Set")

        print("Wait for key enter")
        input()

## STUFF NOT BEING USED RN
def fitData():

    data = readJson("finalData")

    SPM_XYZ = []
    Flavour_output = []
    for item in data["SPMset"]:
        SPM_XYZ.append([item[0], item[1], item[2]])
        Flavour_output.append(item[3])

    popt, pcov = curve_fit(three_dim_gaussian, SPM_XYZ, Flavour_output)

    print("complete")
    
    index = np.argmax(popt)
def plot_current_status(iteration):
    global dataStore, flavour_record

    print("live plotting")
    print(iteration)
    print(len(flavour_record))
    x_axis = np.linspace(1, iteration, iteration)

    for i, item in enumerate(dataStore, 321):
        plt.subplot(i)
        plt.ylabel(item)
        plt.scatter(x_axis, dataStore[item], s = 20, c = 'blue', marker = ".")


    if simulation:
        print(len(x_axis), len(flavour_record))
        plt.subplot(326)
        plt.ylabel('Noise')
        plt.scatter(x_axis, flavour_record, s = 20, c = 'blue', marker = ".")

    plt.suptitle('Experiment 1 - Optimise Flavour') # or plt.suptitle('Main title')
    plt.show()


    #print(flavour_optimiser.max)
def omelette_optimisation():
    global dataStore, flavour_record

    if simulation:
        print("\n\n START SIMULATION \n\n")

    flavour_optimiser = BayesianOptimization(
        f=flavour,
        pbounds=FBound,
        verbose=2, # verbose = 1 prints only when a maximum is observed, verbose = 0 is silent
        random_state=random.randint(0,10000),
    )

    AT_optimiser = BayesianOptimization(
        f=appearance_and_texture,
        pbounds=ATBound,
        verbose=2, # verbose = 1 prints only when a maximum is observed, verbose = 0 is silent
        random_state=random.randint(0,10000),
    )

    F_utility = UtilityFunction(kind="ucb", kappa=1, xi=1e-4) #0.6 kappa
    AT_utility = UtilityFunction(kind="ucb", kappa=1, xi=1e-2)  #3 kappa

    Flogger = JSONLogger(path="./FLogs.json")
    ATlogger = JSONLogger(path="./ATLogs.json")
    flavour_optimiser.subscribe(Events.OPTMIZATION_STEP, Flogger)
    AT_optimiser.subscribe(Events.OPTMIZATION_STEP, ATlogger)

    # ----------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------

    
    print("------------------ STARTING SEARCH -------------------")
    print("\n\n\n")

    for i in range(experiments):

        F_next_point = flavour_optimiser.suggest(F_utility)
        for item in F_next_point:
            F_next_point[item] = round(F_next_point[item], 4)
    

        AT_next_point = AT_optimiser.suggest(AT_utility)
        #AT_next_point['mixing']   = F_next_point['mixing']
        #F_next_point['mixing'] = AT_next_point['mixing']




        if i == 0:
            F_next_point = {'salt': 2.7269, 'pepper': 5.2487, 'mixing': 2.601}
            AT_next_point = {'cooktime': 5.90, 'mixing': 8.146, 'whisking': 2.06}

        averagegMixing = (F_next_point['mixing'] + AT_next_point['mixing'])/2
        print("Av mixing ", averagegMixing)

        dataStore['salt'].append(F_next_point['salt'])
        dataStore['pepper'].append(F_next_point['pepper'])
        #dataStore['mixing'].append(F_next_point['mixing'])
        #dataStore['mixing'].append(AT_next_point['mixing'])
        dataStore['mixing'].append(averagegMixing)
        dataStore['whisking'].append(AT_next_point['whisking'])
        dataStore['cooktime'].append(AT_next_point['cooktime'])

        print("Iteration Number: ", i+1)
        print(F_next_point)
        print(AT_next_point)

        for item in F_next_point:
            F_next_point[item] += random.randint(0,1000) * 0.00001
            print(item, "  ", round(F_next_point[item]))
        for item in AT_next_point:
            AT_next_point[item] += random.randint(0,1000) * 0.00001
            if item == "cooktime":
                print(item, "  ", round(AT_next_point[item]*30 + 210))
            else:
                print(item, "  ", round(AT_next_point[item]))
        
        F_target = flavour(**F_next_point, iteration = i+2)
        AT_target = appearance_and_texture(**AT_next_point, iteration = i+1)

        print("Ftarget", F_target)
        print("ATtarget", AT_target)

        if simulation:
            flavour_record.append(F_target[0]-F_target[1])

        if i == 100:
            plot_current_status(i+1)

        if simulation == False:
            flavour_optimiser.register(params=F_next_point, target=F_target)
            AT_optimiser.register(params=AT_next_point, target=AT_target)
        else:
            flavour_optimiser.register(params=F_next_point, target=F_target[0])
            AT_optimiser.register(params=AT_next_point, target=AT_target[0])

        print("\n")

        #input()

        #plot_current_status(i+1)
    

if __name__ == "__main__":
    #print_func()
    #print(one_dim_gaussian(0.3,  0.3, 0.2, 1.5))
    #omelette_optimisation()    
    #produceRandom()
    bulkBayesian()
    #fitData()