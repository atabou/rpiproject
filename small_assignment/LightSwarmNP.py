
from __future__ import print_function
import os
import time
from datetime import datetime
import RPi.GPIO as GPIO
import numpy as np
import tracemalloc as tm

from netifaces import interfaces, ifaddresses, AF_INET

from socket import socket, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST

import threading

from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.animation import FuncAnimation

"""

GLOBAL VARIABLE DEFINITIONS

"""

# Application meta-data

VERSIONNUMBER = 7

# UDP variable definitions

MYPORT = 2910
SOCKET = None

# UDP packet type definitions

LIGHT_UPDATE_PACKET         = 0
RESET_SWARM_PACKET          = 1
DEFINE_SERVER_LOGGER_PACKET = 4
LOG_TO_SERVER_PACKET        = 5

# Swarm variable definitions

SWARMSTATUS = None
SWARMSIZE   = 5
RESET_TIME  = 0

logString = ""

# Graph related definitions

MASTERS = np.array([])
TIMESTAMPS = np.array([])
DATA = np.array([])

BUFFER = []
AVAILABLE_COLORS = ['r', 'g', 'b', 'y', 'm']
COLOR = {}
MUTEX = threading.Lock()

fig, (graph, bar) = plt.subplots(nrows=1, ncols=2)


def get_time_as_master(current_time, masters, timestamps, colormap):
 
    # Get an array of booleans to indicate when a master has changed (~17.9%)

    verifier = np.concatenate((np.array([True]), masters[:-1:] != masters[1::]))

    # Filter the masters and timestamps arrays to only include moments when the master has changed (~6.4%)
    
    masters = masters[verifier]
    
    timestamps = timestamps[verifier]
 
    # Get the deltas between which the master has changed for each master (~23.6%)

    deltas = np.append(timestamps[1::] - timestamps[:-1:], [current_time - timestamps[-1]])
    
    # Get the total time each node has spent as master and add the corresponding color (~49.3%)
 
    values = [(m, deltas[masters == m].sum(), colormap[m]) for m in np.unique(masters)]
    
    # Unzip values to get the correct format (~2.9%)

    return list(zip(*values))


def get_line(current_time, masters, timestamps, data, colormap):

    # Merge the x and y points in one array (~31.2%)

    points = np.dstack((timestamps - current_time, data))[0].tolist()
 
    # Create an segments by associating points together (~12.4%)

    segments = list(zip(points[:-1:], points[1::]))
 
    # Assign colors to segments (~56.4%)

    colors = np.vectorize(colormap.get)(masters)

    # Return a tuple consisting of the segments and the colors (negligeable)

    return segments, colors



def get_data():


    # Acquire the lock so that no one can write to the saved data
   
    MUTEX.acquire()
   
    #masters = np.array([m['Master'] for m in BUFFER])
    #timestamps = np.array([t['Timestamp'] for t in BUFFER])
    #data = np.array([d['Data']['Value'][0] for d in BUFFER])
    
    tm.start()
    
    measurement = time.time()
    
    if len(BUFFER) > 0:

        # Get the current time

        current_time = time.time()

        # Get a filter array for the last 30 seconds (~46us)

        recent = TIMESTAMPS >= current_time - 30
        
        # Filter the data to plot based on the above boolean array (~38us)

        masters = MASTERS[recent]
        
        timestamps = TIMESTAMPS[recent]
        
        data = DATA[recent]
 
        # Get the values for the graph (~743us)

        segments = get_line(current_time, masters, timestamps, data, COLOR)

        # Get the values for the bar graph (~301us)

        bar_values = get_time_as_master(current_time, masters, timestamps, COLOR)        

        MUTEX.release()

        print("Get data time:", time.time() - measurement)

        memcurrent, mempeak = tm.get_traced_memory()

        print("Current memory use:", str(memcurrent), "B")
        print("Peak memory use:", str(mempeak), "B")

        return (segments, bar_values)
    
    # Release the lock

    MUTEX.release()
    
    print("Get data time:", time.time() - measurement)
    
    tm.get_traced_memory()
    
    print("Current memory use:", str(memcurrent))
    print("Peak memory use:", str(mempeak))
    
    return (([], []), ([], [], []))


def animate(i):


    global fig
    global graph
    global bar


    segments, bar_data = get_data()

    
    bar.clear()
    graph.clear()

    
    bar.set_title('Time Spent as Master (Last 30s)')
    bar.set_xlabel('SwarmID')
    bar.set_ylabel('percentage (%)')
    bar.set_ylim([0, 30])
    bar.bar(range(1, len(bar_data[1]) + 1), bar_data[1], color=bar_data[2])
    bar.set_xticks(range(1, len(bar_data[1]) + 1), bar_data[0])

    graph.set_title('Value of the Master (last 30s)')
    graph.set_xlabel('time elapsed (s)')
    graph.set_ylabel('value')
    graph.set_xlim([-30, 0])
    graph.set_ylim([0, 1024])

    segments, colors = segments
    line = LineCollection(segments, colors=colors)

    graph.add_collection(line)


def animation_thread():
    
    global fig
    global graph
    global bar

    animation = FuncAnimation(fig, animate, interval=1000)

    plt.tight_layout()
    plt.show()


# Raspberry Pi IO and GPIO variable definitions

LED = 38
BUTTON = 22
PRESSED = False


# UDP Commands and packets

def SendDEFINE_SERVER_LOGGER_PACKET(s):

    print("DEFINE_SERVER_LOGGER_PACKET Sent")

    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

    # get IP address

    for ifaceName in interfaces():
        addresses = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr': 'No IP addr'}])]
        print('%s: %s' % (ifaceName, ', '.join(addresses)))

    # last interface (wlan0) grabbed

    print(addresses)

    myIP = addresses[0].split('.')

    print(myIP)

    data = ["" for i in range(14)]

    data[0]  = int("F0", 16).to_bytes(1, 'little')
    data[1]  = int(DEFINE_SERVER_LOGGER_PACKET).to_bytes(1, 'little')
    data[2]  = int("FF", 16).to_bytes(1, 'little')  # swarm id (FF means not part of swarm)
    data[3]  = int(VERSIONNUMBER).to_bytes(1, 'little')
    data[4]  = int(myIP[0]).to_bytes(1, 'little')  # 1 octet of ip
    data[5]  = int(myIP[1]).to_bytes(1, 'little')  # 2 octet of ip
    data[6]  = int(myIP[2]).to_bytes(1, 'little')  # 3 octet of ip
    data[7]  = int(myIP[3]).to_bytes(1, 'little')  # 4 octet of ip
    data[8]  = int(0x00).to_bytes(1, 'little')
    data[9]  = int(0x00).to_bytes(1, 'little')
    data[10] = int(0x00).to_bytes(1, 'little')
    data[11] = int(0x00).to_bytes(1, 'little')
    data[12] = int(0x00).to_bytes(1, 'little')
    data[13] = int(0x0F).to_bytes(1, 'little')

    mymessage = ''.encode()

    s.sendto(mymessage.join(data), ('<broadcast>'.encode(), MYPORT))


def SendRESET_SWARM_PACKET(s):

    print("RESET_SWARM_PACKET Sent")

    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

    data = ["" for i in range(14)]

    data[0] = int("F0", 16).to_bytes(1, 'little')
    data[1] = int(RESET_SWARM_PACKET).to_bytes(1, 'little')
    data[2] = int("FF", 16).to_bytes(1, 'little')  # swarm id (FF means not part of swarm)
    data[3] = int(VERSIONNUMBER).to_bytes(1, 'little')
    data[4] = int(0x00).to_bytes(1, 'little')
    data[5] = int(0x00).to_bytes(1, 'little')
    data[6] = int(0x00).to_bytes(1, 'little')
    data[7] = int(0x00).to_bytes(1, 'little')
    data[8] = int(0x00).to_bytes(1, 'little')
    data[9] = int(0x00).to_bytes(1, 'little')
    data[10] = int(0x00).to_bytes(1, 'little')
    data[11] = int(0x00).to_bytes(1, 'little')
    data[12] = int(0x00).to_bytes(1, 'little')
    data[13] = int(0x0F).to_bytes(1, 'little')

    mymessage = ''.encode()

    s.sendto(mymessage.join(data), ('<broadcast>'.encode(), MYPORT))


def parseLogPacket(message):

    global BUFFER
    global MASTERS
    global TIMESTAMPS
    global DATA
   
    # print("Log From SwarmID:", (message[2]))
    # print("Swarm Software Version:", (message[4]))
    # print("StringLength:", (message[3]))

    logString = ""

    for i in range(0, (message[3])):
        logString = logString + chr((message[i+5]))
 
    # print("logString:", logString)
    # print()

    data = logString.split("|")
   
    data = [data[i].split(",") for i in range(len(data))]

    packet = {

        'Timestamp': time.time(),
        'Master': message[2],
        'Version': message[4],
        'Length': message[3],
        'Data': {
            'Address': [],
            'Version': [],
            'isMaster': [],
            'State': [],
            'Value': []
        }

    }

    for i in range(len(data)):
        
        packet['Data']['Address'].append(data[i][5])
        packet['Data']['Version'].append(data[i][2])
        packet['Data']['isMaster'].append(data[i][1])
        packet['Data']['State'].append(data[i][4])
        packet['Data']['Value'].append(int(data[i][3]))
    
    MUTEX.acquire()

    BUFFER.append(packet)
    
    MASTERS = np.concatenate((MASTERS, np.array([message[2]])))
    TIMESTAMPS = np.concatenate((TIMESTAMPS, np.array([time.time()])))
    DATA = np.concatenate((DATA, np.array([int(data[0][3])])))

    MUTEX.release()

    return logString


def setAndReturnSwarmID(incomingID):
    
    global SWARMSTATUS
    global COLOR
    global AVAILABLE_COLORS

    for i in range(0, SWARMSIZE):
        
        if (SWARMSTATUS[i][5] == incomingID):
            return i

        else:

            if (SWARMSTATUS[i][5] == 0):  # not in the system, so put it in

                SWARMSTATUS[i][5] = incomingID
        
                MUTEX.acquire()

                COLOR[incomingID] = AVAILABLE_COLORS[0]
                AVAILABLE_COLORS = AVAILABLE_COLORS[1::]

                MUTEX.release()

                print("incomingID %d " % incomingID)
                print("assigned #%d" % i)
                print()
                
                return i

    # if we get here, then we have a new swarm member.
    # Delete the oldest swarm member and add the new one in
    # (this will probably be the one that dropped out)
    # Here the same color is reassigned to the same node as we have run out of colors.

    oldTime = time.time()

    oldSwarmID = 0

    for i in range(0, SWARMSIZE):

        if (oldTime > SWARMSTATUS[i][1]):

            oldTime = SWARMSTATUS[i][1]
            oldSwarmID = i

    # remove the old one and put this one in....
    SWARMSTATUS[oldSwarmID][5] = incomingID
    # the rest will be filled in by Light Packet Receive
    print("oldSwarmID %i" % oldSwarmID)
    print()

    return oldSwarmID


def reset_swarm_status():

    global SWARMSTATUS

    SWARMSTATUS = [[0 for x in range(6)] for y in range(SWARMSIZE)]

    # 6 items per swarm item

    # 0 - NP  Not present, P = present, TO = time out
    # 1 - timestamp of last LIGHT_UPDATE_PACKET received
    # 2 - Master or slave status   M S
    # 3 - Current Test Item - 0 - CC 1 - Lux 2 - Red 3 - Green  4 - Blue
    # 4 - Current Test Direction  0 >=   1 <=
    # 5 - IP Address of Swarm

    for i in range(0, SWARMSIZE):
        SWARMSTATUS[i][0] = "NP"
        SWARMSTATUS[i][5] = 0


# Define button interrupt callback function

def reset_swarm():

    global PRESSED
    global BUFFER
    global AVAILABLE_COLORS
    global COLOR

    # Flush the socket (remove all pending data) 
    
    # Reset graphs

    bar.clear()

    graph.clear()

    # Reset SWARMSTATUS.
    
    reset_swarm_status()
 
    # Reset the swarm

    SendRESET_SWARM_PACKET(SOCKET)

    # Prepare Data

    data = ""

    masters, timeasmaster, _ = get_time_as_master(time.time(), MASTERS, TIMESTAMPS, COLOR)

    ip_address = os.popen("/usr/sbin/ifconfig wlan0 | /usr/bin/grep -o 'inet [0-9]*\.[0-9]*\.[0-9]*\.[0-9]*' | /usr/bin/grep -o '[0-9].*'").read()
    ip_address = ip_address[:len(ip_address) - 1:]
    ip_address = ip_address.split(".")

    for i in range(len(masters)):
        data += ip_address[0] + '.' + ip_address[1] + '.' + ip_address[2] + '.' + str(masters[i]) + '\n'
    
    for i in range(len(masters)):
        data += str(masters[i]) + ': ' + str(timeasmaster[i]) + 's\n'

    data += str(BUFFER)

    # Save BUFFER to file.
 
    fp = open(str(datetime.now()) + '.log', 'w')

    fp.write(data)

    fp.close()

    # Reset BUFFER.

    MUTEX.acquire()

    BUFFER = []
    AVAILABLE_COLORS = ['r', 'g', 'b', 'y', 'm']
    COLOR = {}

    MUTEX.release()

 
    # Redefine server logger for the swarm

    SendDEFINE_SERVER_LOGGER_PACKET(SOCKET)
    
    # Turn the light on for 3 seconds

    GPIO.output(LED, GPIO.HIGH)
    
    time.sleep(3)
    
    GPIO.output(LED, GPIO.LOW)


def button_interrupt(channel):
    
    global PRESSED
    PRESSED = True


def setup():

    global SOCKET
    global RESET_TIME
    global SWARMSTATUS

    print("--------------")
    print("LightSwarm Logger")
    print("Version ", VERSIONNUMBER)
    print("--------------")

    # Create a socket server
    SOCKET = socket(AF_INET, SOCK_DGRAM)
    SOCKET.bind(('', MYPORT))
 
    # Broadcast DEFINE_SERVER_LOGGER_PACKET to tell swarm where to send logging information

    SendDEFINE_SERVER_LOGGER_PACKET(SOCKET)

    time.sleep(3)

    SendDEFINE_SERVER_LOGGER_PACKET(SOCKET)

    # Initialize the swarm status

    reset_swarm_status()
    
    # Set GPIO adressing mode

    GPIO.setmode(GPIO.BOARD)
     
    # Initialize button GPIO pin and button interrupt

    GPIO.setup(BUTTON, GPIO.IN, GPIO.PUD_UP)
    GPIO.add_event_detect(BUTTON, GPIO.FALLING, callback=button_interrupt, bouncetime=200)

    # Initialize LED GPIO pins

    GPIO.setup(LED, GPIO.OUT)

    # Set LED pins to low.

    GPIO.output(LED, GPIO.LOW)

    # Set the next reset time

    RESET_TIME = time.time() + 300.0

    # Initialize Threads

    anim_thread = threading.Thread(target=animation_thread)

    anim_thread.start()


def loop():

    global RESET_TIME
    global SWARMSTATUS
    global PRESSED

    while(1):

        if PRESSED == True:
            reset_swarm()
            PRESSED = False

        # receive datclient (data, addr)
        d = SOCKET.recvfrom(1024)

        message = d[0]

        if PRESSED is True:
            pass

        if (len(message) > 1):

            if (message[1] == LIGHT_UPDATE_PACKET):

                incomingSwarmID = setAndReturnSwarmID((message[2]))
                
                SWARMSTATUS[incomingSwarmID][0] = "P"
                SWARMSTATUS[incomingSwarmID][1] = time.time()
                
            if ((message[1]) == LOG_TO_SERVER_PACKET):

                #print("Swarm LOG_TO_SERVER_PACKET Received")

                # process the Log Packet

                incomingSwarmID = setAndReturnSwarmID((message[2]))

                logString = parseLogPacket(message)

        else:

            print("error - message = ", message)

        if (time.time() > RESET_TIME):

            # do our 2 minute round

            print(">>>>doing 300 second task")

            reset_swarm()

            RESET_TIME = time.time() + 300.0


try:

    setup()

    loop()


except KeyboardInterrupt:
    GPIO.cleanup()
    print("Interrupted")

finally:
    GPIO.cleanup()
    print("Application Terminated.")
