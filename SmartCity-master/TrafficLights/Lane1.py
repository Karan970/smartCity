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
from datetime import datetime
import random
from threading import Thread
import time
from time import sleep
from tkinter import *
import cv2
import sys
import math
import tkinter as tk

def run_periodically(func, ms):
    func()
    root.after(ms, run_periodically, func, ms)



def thread_function1(g):
    video_source = "traffic.mp4"

    TrackerType = "KCF"

    cascadePath = "car4-1.xml"

    def cent_dist(a, b):
        temp = math.sqrt(pow((a[1] - b[1]), 2) + pow((a[0] - b[0]), 2))
        return temp

    def checkOverlap(a, b):
        (x1, y1, w1, h1) = a
        (x2, y2, w2, h2) = b

        if (x1 < (x2 + w2 / 2)):
            if (x1 + w1 > (x2 + w2 / 2)):
                if (y1 < (y2 + h2 / 2)):
                    if (y1 + h1 > (y2 + h2 / 2)):
                        return True
        if (x2 < (x1 + w1 / 2)):
            if (x2 + w2 > (x1 + w1 / 2)):
                if (y2 < (y1 + h1 / 2)):
                    if (y2 + h2 > (y1 + h1 / 2)):
                        return True
        return False

    def removeOverlaps(objectsFoundLocal):
        objectsFoundTemp = []
        for i in range(0, len(objectsFoundLocal)):
            matchBool = False
            for j in range(i + 1, len(objectsFoundLocal)):
                if (checkOverlap(objectsFoundLocal[i], objectsFoundLocal[j])):
                    matchBool = True
            if not matchBool:
                objectsFoundTemp.append(objectsFoundLocal[i])
        return objectsFoundTemp

    tracker = {}
    status = {}
    trackerLifeTime = {}
    bbox = {}
    bboxOld = {}
    ok = {}
    centroid_car = {}
    centroid_tracker = {}
    Dir = {}

    no_trackers = 15
    for i in range(0, no_trackers):
        trackerLifeTime[i] = 0
        tracker[i] = cv2.TrackerMedianFlow_create()
        status[i] = "OFF"
        ok[i] = False

    # cascade init
    car_cascade = cv2.CascadeClassifier(cascadePath)

    video = cv2.VideoCapture(video_source)
    video.set(cv2.CAP_PROP_FPS, 1000)

    if not video.isOpened():
        print("Could not open video")
        sys.exit()

    ok1, frame = video.read()

    frameTrackersPrev = frame.copy()
    frameHaarPrev = frame.copy()
    if not ok1:
        print('Cannot read video file')
        sys.exit()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    cars = car_cascade.detectMultiScale(gray, 1.3, 5)

    cars = removeOverlaps(cars)

    for i in range(0, no_trackers):
        bbox[i] = (0, 0, 0, 0)
        bboxOld[i] = (0, 0, 0, 0)
        tracker[i] = cv2.TrackerMedianFlow_create()
        ok[i] = tracker[i].init(frame, bbox[i])
        tracker[i] = cv2.TrackerMedianFlow_create()
        status[i] = "OFF"
        Dir[i] = "IN"
        ok[i] = False
    trackersOn = 0
    carCount = 0
    carCountIn = 0
    carCountOut = 0
    stTime = time.time()
    pause = False
    absoluteStTime = time.time()
    totalFrames = 0
    wait = int(27)+int(time.time())
    while time.time()<wait:
        if video.read() ==None:
            break

        ok1, frame = video.read()
        if frame is None:
            break


        frameHaar = frame.copy()
        frameTrackers = frame.copy()
        if not ok1:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cars = car_cascade.detectMultiScale(gray, 1.3, 5)
        cars = removeOverlaps(cars)

        i = 0
        for (x, y, w, h) in cars:
            centroid_car[i] = (x + (w / 2), y + (h / 2))
            i += 1

        for i in range(0, no_trackers):
            if status[i] != "OFF":
                temp = (bbox[i][0] + (bbox[i][2] / 2), bbox[i][1] + (bbox[i][3] / 2))
            else:
                centroid_tracker[i] = (0, 0)

        for i in range(0, len(cars)):
            matchFound = False
            for j in range(0, no_trackers):  # check if any trackers are already tracking the car
                if status[j] == "DUP":
                    continue
                if status[j] == "OFF":
                    continue
                if ((checkOverlap(cars[i], bbox[j])) | (checkOverlap(bbox[j], cars[i]))):
                    if ((cars[i][2] < bbox[j][2]) & (matchFound == False)):
                        p1 = (int(bbox[j][0]), int(bbox[j][1]))
                        p2 = (int(bbox[j][0] + bbox[j][2]), int(bbox[j][1] + bbox[j][3]))
                        if status[j] == "NEW":
                            continue

                        tracker[j] = cv2.TrackerMedianFlow_create()
                        temp = (cars[i][0], cars[i][1], cars[i][2], cars[i][3])
                        bbox[j] = temp
                        ok[j] = tracker[j].init(frame, temp)
                        status[j] = "HUD"
                        matchFound = True
                        p1 = (int(bbox[j][0]), int(bbox[j][1]))
                        p2 = (int(bbox[j][0] + bbox[j][2]), int(bbox[j][1] + bbox[j][3]))
                    cv2.rectangle(frameHaar, (cars[i][0], cars[i][1]),
                                  (cars[i][0] + cars[i][2], cars[i][1] + cars[i][3]),
                                  (0, 255, 0), 2)
                    matchFound = True
            if matchFound == False:
                for k in range(0, no_trackers):
                    if status[k] == "OFF":
                        cv2.rectangle(frameHaar, (cars[i][0], cars[i][1]),
                                      (cars[i][0] + cars[i][2], cars[i][1] + cars[i][3]), (0, 0, 255), 2)
                        trackerLifeTime[k] = 0
                        tracker[k] = cv2.TrackerMedianFlow_create()
                        temp = (cars[i][0], cars[i][1], cars[i][2], cars[i][3])
                        bbox[k] = temp
                        ok[k] = tracker[k].init(frame, temp)
                        temp = (cars[i][0], cars[i][1], cars[i][2], cars[i][3])
                        bbox[k] = temp
                        trackersOn += 1
                        status[k] = "NEW"
                        break

        for i in range(0, no_trackers):
            if status[i] == "OFF":
                pass
            elif status[i] == "UD":
                bboxOld[i] = bbox[i]

                if ((bbox[i][0] + bbox[i][2] / 2) < (frame.shape[1] / 2)):
                    Dir[i] = "OUT"
                else:
                    Dir[i] = "IN"
                ok[i], bbox[i] = tracker[i].update(frame)
                trackerLifeTime[i] += 1
                if not ok[i]:
                    status[i] = "LOST"
                    # print ("trackerOn -= 1", i, "st = ", status[i])
                    trackersOn -= 1
                    pause = True
                    carCount += 1
                    if (Dir[i] == "IN"):
                        carCountIn += 1
                    elif (Dir[i] == "OUT"):
                        carCountOut += 1
                elif bbox[i][2] < 20:  # Out Of Sight (Too Small)
                    status[i] = "LOST"

                    trackersOn -= 1
                    carCount += 1
                    if (Dir[i] == "IN"):
                        carCountIn += 1
                    elif (Dir[i] == "OUT"):
                        carCountOut += 1
                    pause = True
                    ok[i] = False
            elif status[i] == "NEW":
                status[i] = "UD"
            elif status[i] == "HUD":
                status[i] = "UD"
            elif status[i] == "DUP":
                status[i] = "OFF"
                bbox[i] == (0, 0, 0, 0)
                ok[i] = False
            elif status[i] == "LOST":
                status[i] = "OFF"
                bbox[i] == (0, 0, 0, 0)
                ok[i] = False

        for i in range(0, len(bbox)):
            if (bbox[i] == (0, 0, 0, 0)):
                continue
            if (status[i] == "OFF"):
                continue
            matchBool = False
            for j in range(i + 1, len(bbox)):
                if (bbox[j] == (0, 0, 0, 0)):
                    continue
                if (status[j] == "OFF"):
                    continue
                if (checkOverlap(bbox[i], bbox[j])):
                    status[i] = "DUP"
                    trackersOn -= 1
                    bbox[i] == (0, 0, 0, 1)
                    matchBool = True
        for i in range(0, no_trackers):
            if ok[i]:
                p1 = (int(bbox[i][0]), int(bbox[i][1]))
                p2 = (int(bbox[i][0] + bbox[i][2]), int(bbox[i][1] + bbox[i][3]))
                if ((status[i] == "UD")):
                    cv2.rectangle(frameTrackers, p1, p2, (0, 255, 0), 1)

        cv2.putText(frameTrackers, (str)(carCountIn), (int(530), int(110)), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)

        #cv2.imshow('Haar', frameHaar)
        cv2.imshow('Trackers', frameTrackers)

        frameTrackersPrev = frameTrackers.copy()
        frameHaarPrev = frameHaar.copy()

        if pause:
            key = cv2.waitKey(1) & 0xFF
            pause = False
            if ((key == ord('q')) | (key == 27)):
                break
        key = cv2.waitKey(1) & 0xFF
        if ((key == ord('q')) | (key == 27)):
            break
        endTime = time.time()
        totalFrames += 1


        stTime = endTime
    video.release()
    cv2.destroyAllWindows()



def thread_function(g, a, b, c):
    tk = Tk()
    win = Canvas(tk, width=55, height=200)
    win.pack()
    win.create_oval(5, 5, 50, 50, fill=a)
    win.create_oval(5, 55, 50, 100, fill=b)
    win.create_oval(5, 105, 50, 150, fill=c)
    win.master.title("Lane1")

    wait = int(time.time() + int(g))
    while time.time() < wait:
        tk.update()


if __name__ == "__main__":
    g = 0
    flag = 0
    j = {}
    lane_id = ""


    def customOnMessage(message):
        print('Received message on topic %s: %s\n' % (message.topic, message.payload))
        j = json.loads(message.payload.decode("utf-8"))
        global flag, g, lane_id
        flag = j['flag']
        g = j['green']
        lane_id = j['laneId']


    MAX_DISCOVERY_RETRIES = 10
    GROUP_CA_PATH = "./groupCA/"

    parser = argparse.ArgumentParser()

    #args = parser.parse_args()
    #host: Go to AWS IoT Console. Go to settings and copy the Endpoint.
    #rootCAPath: http://www.symantec.com/content/en/us/enterprise/verisign/roots/VeriSign-Class%203-Public-Primary-Certification-Authority-G5.pem
    #certificatePath: Enter the cert.pem file that is created when you create Lane1
    #privateKeyPath: Enter the private.key file that is created when  you create Lane1
    clientId = "Lane1"
    thingName = "Lane1"

    logger = logging.getLogger("AWSIoTPythonSDK.core")
    logger.setLevel(logging.DEBUG)
    streamHandler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)

    backOffCore = ProgressiveBackOffCore()

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

            retryCount -= 1
            print("\n%d/%d retries left\n" % (retryCount, MAX_DISCOVERY_RETRIES))
            print("Backing off...\n")
            backOffCore.backOff()

    if not discovered:
        print("Discovery failed after %d retries. Exiting...\n" % (MAX_DISCOVERY_RETRIES))
        sys.exit(-1)

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

    if not connected:
        print("Cannot connect to core %s. Exiting..." % coreInfo.coreThingArn)
        sys.exit(-2)

    payloadDict = {}


    def getJson(myAWSIoTMQTTClient, userdata, message):

        customOnMessage(message)



    while True:
        myAWSIoTMQTTClient.subscribe("green/update", 0, getJson)
        if flag == 1 and lane_id == "One":
            t = int(time.time())
            thread = Thread(target=thread_function, args=(g, "green", "black", "black"))
            thread1 = Thread(target=thread_function1, args=(g, ))
            thread.start()
            thread1.start()

            mes = {'laneId': 1, 'green': g, 'starttime': str(datetime.now())}
            wait = int(time.time()) + int(g)
            while time.time() < wait:
                if int(time.time() - t) == abs(10):
                    mes['endtime'] = str(datetime.now())
                    mes['car'] = str(random.randint(5, 10))
                    payL = json.dumps(mes)
                    myAWSIoTMQTTClient.publish("update/lambda", payL, 0)
                    print("Lambda")
                    mes['starttime'] = mes['endtime']
                    t = time.time()
            thread1.join()
            thread.join()

            myAWSIoTMQTTClient.publish("lane1/numCar", str(random.randint(0, int(g))), 0)
            flag = 0
        else:
            g = int(g)+1
            thread = Thread(target=thread_function, args=((g), "black", "black", "red"))
            thread.start()
            thread.join()
