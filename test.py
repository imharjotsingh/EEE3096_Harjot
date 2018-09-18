#!/usr/bin/python
import spidev
import time
import os
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
reset =17
freq =27
stop =22
display=23

#VariablesDefination
delay = 0.5
ldr_channel = 2
temp_channel = 0
pot_channel = 1


#interrupt switches set up
GPIO.setup(reset, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(freq, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(stop, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(display, GPIO.IN, pull_up_down=GPIO.PUD_UP)


#Create SPI Object
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz=1000000


#read SPI data from MCP3008 chip
def getChannel(channel):
  adc = spi.xfer2([1,(8+channel)<<4,0])
  data = ((adc[1]&3) << 8) + adc[2]
  return data
    
def ConvertVolts(data,places):
  volts = (data * 3.3) / float(1023)
  volts = round(volts,places)
  return volts

def ConvertTemp(data,places):
  temp = (((data * 3.30)/float(1023))-0.50)/0.01
  temp = round(temp,places)
  return temp

#convert light incident to LDR to a percent
def ConvertLight(data, places):
    vOut=(data*3.3)/float(1023)
    light=vOut/3.3*100
    light=round(light,places)
    return light
    

#generation  of a  string to display time and timer in the correct format using string slicing
def TimeFormat(t):
    instance=time.localtime(t)
    return(str(instance.tm_min).zfill(2)+":"+str(instance.tm_sec).zfill(2)+":"+str(t-int(t))[2:4]) 


#stop callbaack function 
def stopcallback(channel): 
    global mon
    global lc
    if (mon==1):
        mon=0
    elif (mon==0):
        mon=1
        lc=0

#frequency callback function 
def freqcallback(channel):
    global delay
    if (delay==0.5):
        delay=1
    elif (delay==1):
        delay=2
    elif (delay==2):
        delay=0.5

   #reset callback function 
def resetcallback(channel):
    global starttime
    global logit
    global lc
    starttime=time.time()
    logit=""
    lc=0
    os.system('clear')

#display callback function def
def displaycallback(channel):
    global mon
    global logit
    if (mon==0):
        print("Time     Timer    Pot  Temp   Light")
        print(logit)
    
#Under a rising edge, the callback function is called 
GPIO.add_event_detect(reset,GPIO.RISING,callback=resetcallback,bouncetime=200)
GPIO.add_event_detect(freq, GPIO.RISING,callback=freqcallback,bouncetime=200)
GPIO.add_event_detect(stop, GPIO.RISING,callback=stopcallback,bouncetime=200)
GPIO.add_event_detect(display,GPIO.RISING,callback=displaycallback,bouncetime=200)

#Display on/off variable
mon=1

#Default display frequency
delay=0.5

#variable of initial start time, used for timer
starttime=time.time()

lc=0
log=""
logit=""

#infinite loop
while True: 

  # Read the light sensor data
  ldr_level = getChannel(ldr_channel)
  light = ConvertLight(ldr_level,2)
 
  # Read the temperature sensor data
  temp_level = getChannel(temp_channel)
  temp = ConvertTemp(temp_level,2)
 
  #Reas the potentiometer data 
  pot_level=getChannel(pot_channel)
  pot_volts=ConvertVolts(pot_level,2)

  #create string for displaying at this time instance
  log=TimeFormat(time.time())+" " +TimeFormat(time.time()-starttime) + " "+"{}V {}C {}%".format(pot_volts, temp, light)
  
  #if stop has not been pressed
  if (mon==1):
      print("Time     Timer    Pot  Temp   Light")
      print(log)
  #if stop has been pressed, and has less than 5 time instances in the string that display outputs
  elif ((mon==0) and (lc<5)):
    logit=logit+"\n"+log
    lc=lc+1

  #delay, also deals with the frequency
  time.sleep(delay)
# while True:
#     ldr_value = ReadChannel(ldr_channel)
#     print "---------------------------------------"
#     print("LDR Value: %d" % ldr_value)

#     temp_value = ReadChannel(temp_channel)
#     print "---------------------------------------"
#     print("Temp Value: %d" % temp_value)
#     pot_value = ReadChannel(pot_channel)
#     print "---------------------------------------"
#     print("Pot Value: %d" % pot_value)
#     time.sleep(delay)
