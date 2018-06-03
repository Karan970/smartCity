
d = {0:"A",1:"B",2:"C"}
import random
def rand1(q):
    return random.randint(int(q),int(2*q))
def rand():
    return random.randrange(30,60)
def perSecCar(n,g):
    m = float("{0:.2f}".format(n/g))
    return m
    
with open("trafficdata.csv",'w') as csvfive:
    carsGreenSec = [0,0,0]
    carPerSec = [0,0,0]
    waitTime = [60,30,0]
    g = [30,30,30]
    p = []
   
    n = 3
    for j in range(3):
        carsGreenSec[j] = rand()
        carPerSec[j] = perSecCar(carsGreenSec[j],30)
    print(str("[30,30,30]") + " Green in Previous Cycle")
    print(str(carsGreenSec) +" Number of cars captured")
    print(str(carPerSec) +" Rate of flow of car")
    print(str(waitTime) +" Wait Time")
    print(str(sum(carsGreenSec))+" Total Number of cars in cylce")
    print(str(sum(waitTime)/3)+" Average WaitTime")
    k = 0
    for l in range(10):
        p = list(g)
        f = (carPerSec[(l+1)%n]+carPerSec[(l+2)%n])/1.025
        g[l%n] = int((carPerSec[l%n]*waitTime[l%n])/f)
        waitTime[l%n] = 0
        for t in range(3):
            if t!= l%n:
                waitTime[t] += g[l%n]
              
        for j in range(3):
            if j == l%n:
                carsGreenSec[j] = rand1(g[j])     
                carPerSec[j] = perSecCar(carsGreenSec[j],g[l%n])
        if l%n == 0:
            print(str(l+1) + " Cycle")
        print(str(g[l%n]) + " Green Light for " +str(d[l%n]) +" Line")
       
        print(str(p) + " Previous cycle green")
        print( str(carsGreenSec) + " Cars passing in greenLight")
        print( str(carPerSec) + " Cars Passing Per Second")
        print(str(waitTime) + " Wait Time")
        print(str(sum(carsGreenSec))+" Total Number of cars in cycle")
        print(str(sum(waitTime)/3)+" Average WaitTime")

               


               

