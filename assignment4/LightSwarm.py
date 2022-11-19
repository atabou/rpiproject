
from __future__ import print_function
import os
import time
from datetime import datetime
import RPi.GPIO as GPIO

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

BUFFER = []
AVAILABLE_COLORS = ['r', 'g', 'b', 'y', 'm']
COLOR = {}
MUTEX = threading.Lock()

fig, (graph, bar) = plt.subplots(nrows=1, ncols=2)

time1 = 0


def get_time_as_master(current_time, recent, colormap):

    # Get an array of booleans to indicate when a master has changed

    verifier = [True]

    verifier = verifier + [recent[i]['Master'] != recent[i-1]['Master'] for i in range(1, len(recent) - 1)]
       
    if len(recent) > 1:

        if recent[-1]['Master'] == recent[-2]['Master']:
            verifier.append(False)
        
        else:
            verifier.append(True)
 
    # Filter out the booleans to only get the moments when the master has changed

    intervals = [packet for (packet, v) in zip(recent, verifier) if v]
        
    # Get the deltas between which the master has changed for each master

    deltas = [(intervals[i], intervals[i + 1]['Timestamp'] - intervals[i]['Timestamp']) for i in range(len(intervals) - 1)]
    deltas.append((intervals[-1], current_time - intervals[-1]['Timestamp']))

    # Get the total time each node has spent as master

    bar_values = []
 
    for packet, delta in deltas:

        pos = -1

        for i in range(len(bar_values)):
            if bar_values[i][0] == packet['Master']:
                pos = i
                break

        if pos != -1:
            bar_values[pos][1] += delta
        else:
            bar_values.append([packet['Master'], delta, colormap[packet['Master']]])

    bar_values.sort(key=lambda tup: tup[0])

    return list(zip(*bar_values))


def get_line_collection(current_time, recent, colormap):

    points = [(recent[i]['Timestamp'] - current_time, recent[i]['Data']['Value'][0], colormap[recent[i]['Master']]) for i in range(len(recent))]

    segments = []
        
    colors = []

    for i in range(len(points) - 1):
            
        segments.append(((points[i][0], points[i][1]), (points[i+1][0], points[i+1][1])))
           
        colors.append(points[i][2])

    return LineCollection(segments, colors=colors)



def get_data():

    global time1
    
    print(time.time() - time1)

    time1 = time.time()
   
    MUTEX.acquire()
   
    if len(BUFFER) > 0:

        # Get the current time

        current_time = time.time()

        # Filter to get last 30s of data
        
        recent = list(filter(lambda packet: packet['Timestamp'] - current_time >= -30, BUFFER))
 
        # Get the values for the graph

        segments = get_line_collection(current_time, recent, COLOR)

        # Get the values for the bar graph

        bar_values = get_time_as_master(current_time, recent, COLOR)
        
        MUTEX.release()

        return (segments, bar_values)
    
    MUTEX.release()
    
    return (LineCollection([]), ([], [], []))


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
    graph.add_collection(segments)


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
   
    print("Log From SwarmID:", (message[2]))
    print("Swarm Software Version:", (message[4]))
    print("StringLength:", (message[3]))

    logString = ""

    for i in range(0, (message[3])):
        logString = logString + chr((message[i+5]))
 
    print("logString:", logString)
    print()

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

    masters, timeasmaster, _ = get_time_as_master(time.time(), BUFFER, COLOR)

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

    RESET_TIME = time.time() + 30.0

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

                print("Swarm LOG_TO_SERVER_PACKET Received")

                # process the Log Packet

                incomingSwarmID = setAndReturnSwarmID((message[2]))

                logString = parseLogPacket(message)

        else:

            print("error - message = ", message)

        if (time.time() > RESET_TIME):

            # do our 2 minute round

            print(">>>>doing 300 second task")

            SendDEFINE_SERVER_LOGGER_PACKET(SOCKET)

            RESET_TIME = time.time() + 30.0


try:

    setup()

    loop()


except KeyboardInterrupt:
    GPIO.cleanup()
    print("Interrupted")

finally:
    GPIO.cleanup()
    print("Application Terminated.")
