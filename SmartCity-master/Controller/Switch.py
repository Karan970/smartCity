line_id = 0
cars = 0

d = {0: "A", 1: "B", 2: "C"}
import random

f = 1
glob = 1


def rand1(q):
    return random.randint(30, 60)


def rand2(q):
    return random.randint(20, 40)


def rand3(q):
    return random.randint(15, 30)


def rand():
    return random.randrange(30, 60)


def perSecCar(n, g):
    m = float("{0:.2f}".format(n / g))
    return m


def calculate_carpersec(f, k, i, carPerSec):
    for j in range(3):
        if j == i and glob % 10 != 0 and f == 1:
            if k == 1:
                carsGreenSec[j] = rand1(g[j])
                carPerSec[j] = perSecCar(carsGreenSec[j], g[j])
            elif k == 2:
                carsGreenSec[j] = rand2(g[j])
                carPerSec[j] = perSecCar(carsGreenSec[j], g[j])
            else:
                carsGreenSec[j] = rand3(g[j])
                carPerSec[j] = perSecCar(carsGreenSec[j], g[j])
        elif j == i:
            f = 0
            if k == 1:
                carsGreenSec[j] = rand3(g[j])
                carPerSec[j] = perSecCar(carsGreenSec[j], g[j])
            elif k == 2:
                carsGreenSec[j] = rand1(g[j])
                carPerSec[j] = perSecCar(carsGreenSec[j], g[j])
            else:
                carsGreenSec[j] = rand2(g[j])
                carPerSec[j] = perSecCar(carsGreenSec[j], g[j])
            if glob % 20 == 0:
                f = 1


def calculate_waittime(i, waitTime):
    for t in range(3):
        if t != i:
            waitTime[t] += g[i]


def calculate_green(i, g, caPerSec, waitTime):
    c = carPerSec[i] / sum(carPerSec) + (waitTime[i] / (sum(waitTime)))
    g[i] = int(c * int(sum(carsGreenSec) / 3))
    return g[i]


def print_output(i):
    print(str(g[i]) + " Green Light for " + str(d[i]) + " Line")
    print(str(previous) + " Previous cycle green")
    print(str(carsGreenSec) + " Cars passing in greenLight")
    print(str(carPerSec) + " Cars Passing Per Second")
    print(str(waitTime) + " Wait Time")
    print(str(sum(carsGreenSec)) + " Total Number of cars in cycle")
    print(str(sum(waitTime) / 3) + " Average WaitTime")
    print()


with open("trafficdata.csv", 'w') as csvfive:
    carsGreenSec = [0, 0, 0]  # number of cars in green
    carPerSec = [0, 0, 0]
    waitTime = [60, 30, 0]
    iwaitTime = [60, 30, 0]
    g = [30, 30, 30]
    p = []

    n = 3
    for j in range(3):
        carsGreenSec[j] = rand()
        carPerSec[j] = perSecCar(carsGreenSec[j], 30)
    print(str("[30,30,30]") + " Green in Previous Cycle")
    print(str(carsGreenSec) + " Number of cars captured")
    print(str(carPerSec) + " Rate of flow of car")
    print(str(waitTime) + " Wait Time")
    print(str(sum(carsGreenSec)) + " Total Number of cars in cylce")
    print(str(sum(waitTime) / 3) + " Average WaitTime")
    print()
    glob = 1

import os
import sys
import time
import uuid
import json
import logging
import argparse
from AWSIoTPythonSDK.core.greengrass.discovery.providers import DiscoveryInfoProvider
from AWSIoTPythonSDK.core.protocol.connection.cores import ProgressiveBackOffCore
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from AWSIoTPythonSDK.exception.AWSIoTExceptions import DiscoveryInvalidRequestException
from itertools import cycle

AllowedActions = ['both', 'publish', 'subscribe']


# General message notification callback
def customOnMessage(message):
    print('Received message on topic %s: %s\n' % (message.topic, message.payload))
    global line_id, cars
    j = json.loads(message.payload.decode("utf-8"))




MAX_DISCOVERY_RETRIES = 10
GROUP_CA_PATH = "./groupCA/"

# Read in command-line parameters
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help="Your AWS IoT custom endpoint")
parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="Root CA file path")
parser.add_argument("-c", "--cert", action="store", dest="certificatePath", help="Certificate file path")
parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", help="Private key file path")
parser.add_argument("-n", "--thingName", action="store", dest="thingName", default="Bot", help="Targeted thing name")
parser.add_argument("-M", "--message", action="store", dest="message", default="Hello World!",
                    help="Message to publish")

args = parser.parse_args()
host = args.host
rootCAPath = args.rootCAPath
certificatePath = args.certificatePath
privateKeyPath = args.privateKeyPath
clientId = args.thingName
thingName = args.thingName

'''if args.mode not in AllowedActions:
    parser.error("Unknown --mode option %s. Must be one of %s" % (args.mode, str(AllowedActions)))
    exit(2)
'''

if not args.certificatePath or not args.privateKeyPath:
    parser.error("Missing credentials for authentication.")
    exit(2)

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Progressive back off core
backOffCore = ProgressiveBackOffCore()

# Discover GGCs
discoveryInfoProvider = DiscoveryInfoProvider()
discoveryInfoProvider.configureEndpoint(host)
discoveryInfoProvider.configureCredentials(rootCAPath, certificatePath, privateKeyPath)
discoveryInfoProvider.configureTimeout(10)  # 10 sec

retryCount = MAX_DISCOVERY_RETRIES
discovered = False
groupCA = None
coreInfo = None
while retryCount != 0:
    try:
        discoveryInfo = discoveryInfoProvider.discover(thingName)
        caList = discoveryInfo.getAllCas()
        coreList = discoveryInfo.getAllCores()

        # We only pick the first ca and core info
        groupId, ca = caList[0]
        coreInfo = coreList[0]
        print("Discovered GGC: %s from Group: %s" % (coreInfo.coreThingArn, groupId))

        print("Now we persist the connectivity/identity information...")
        groupCA = GROUP_CA_PATH + groupId + "_CA_" + str(uuid.uuid4()) + ".crt"
        if not os.path.exists(GROUP_CA_PATH):
            os.makedirs(GROUP_CA_PATH)
        groupCAFile = open(groupCA, "w")
        groupCAFile.write(ca)
        groupCAFile.close()

        discovered = True
        print("Now proceed to the connecting flow...")
        break
    except DiscoveryInvalidRequestException as e:
        print("Invalid discovery request detected!")
        print("Type: %s" % str(type(e)))
        # print("Error message: %s" % e.message)
        print("Stopping...")
        break
    except BaseException as e:
        print("Error in discovery!")
        print("Type: %s" % str(type(e)))
        # print("Error message: %s" % e.message)
        retryCount -= 1
        print("\n%d/%d retries left\n" % (retryCount, MAX_DISCOVERY_RETRIES))
        print("Backing off...\n")
        backOffCore.backOff()

if not discovered:
    print("Discovery failed after %d retries. Exiting...\n" % (MAX_DISCOVERY_RETRIES))
    sys.exit(-1)

# Iterate through all connection options for the core and use the first successful one
myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
myAWSIoTMQTTClient.configureCredentials(groupCA, privateKeyPath, certificatePath)
myAWSIoTMQTTClient.onMessage = customOnMessage

connected = False
for connectivityInfo in coreInfo.connectivityInfoList:
    currentHost = connectivityInfo.host
    currentPort = connectivityInfo.port
    print("Trying to connect to core at %s:%d" % (currentHost, currentPort))
    myAWSIoTMQTTClient.configureEndpoint(currentHost, currentPort)
    try:
        myAWSIoTMQTTClient.connect()
        connected = True
        break
    except BaseException as e:
        print("Error in connect!")
        print("Type: %s" % str(type(e)))
        # print("Error message: %s" % e.message)

if not connected:
    print("Cannot connect to core %s. Exiting..." % coreInfo.coreThingArn)
    sys.exit(-2)

def getJson(myAWSIoTMQTTClient, userdata, message):
    customOnMessage(message)

loopCount = 0
top = ["lane1/update", "lane2/update", "lane3/update"]
top1 = ["lane1/numCar","lane2/numCar","lane3/numCar"]
topics = cycle(top)
topics1 = cycle(top1)
k = 0
c = [0, 1, 2]
li = ["One","two","three"]

green = 0
for k in range(100):
    for i, topic, lineId in zip(c, topics,li):
        message = {}
        previous = list(g)
        green = calculate_green(i, g, carPerSec, waitTime)
        message["laneId"] = lineId
        message['flag'] = 1
        message['green'] = str(green)
        print(message)
        messageJson = json.dumps(message)
        k += 1
        glob += 1
        myAWSIoTMQTTClient.publish("green/update", messageJson, 0)
        time.sleep(green)
        waitTime[i] = 0
        calculate_waittime(i, waitTime)
        calculate_carpersec(f, int(k % 3), i, carPerSec)
    loopCount += 1
