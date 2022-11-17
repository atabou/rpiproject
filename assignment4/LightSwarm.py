
from __future__ import print_function
import time
import RPi.GPIO as GPIO

from netifaces import interfaces, ifaddresses, AF_INET

from socket import socket, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
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

BUFFER = pd.DataFrame(columns=['Timestamp', 'Master', 'Version', 'Length'] + [i for i in range(SWARMSIZE)])

# last_30_s = df[time.time() - df['Timestamp'] >= -30].sort_values(['Timestamp'])


def get_bar_chart_values(df):
    
    df1 = df.sort_values(['Timestamp'])
    df1['Changed'] = df1['Master'].shift(1) != df1['Master']
    df1 = df1[df1['Changed'] == True]
    df1['Delta'] = (df1['Timestamp'].shift(-1) - df1['Timestamp']).fillna(0)
    df1.iloc[-1, df1.columns.get_loc('Delta')] = 17 - df1.iloc[-1, df1.columns.get_loc('Timestamp')]
    df1 = df1.groupby(by=['Master'])['Delta'].sum().reset_index(name='Percentage')
    sum = df1['Percentage'].sum()
    df1['Percentage'] = 100 * df1['Percentage'] / sum

    return df1


def get_line_chart_values(df):
    pass

fig, (graph, bar) = plt.subplots(nrows=1, ncols=2)

graph.set_title('Value of the master over the last 30s')
graph.set_xlabel('time elapsed (s)')
graph.set_ylabel('value')

bar.set_title('Share of Time Spent as Master in the Last 30s')
bar.set_xlabel('SwarmID')
bar.set_ylabel('percentage (%)')
bar.set_ylim([0, 100])
#bar.set_xticks()

#bar.bar(np.arange(len(vals)), vals)

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

    parsed_data = { 'Timestamp': time.time() }
 
    parsed_data['Master'] = message[2]
    print("Log From SwarmID:", (message[2]))

    parsed_data['Version'] = message[4],
    print("Swarm Software Version:", (message[4]))

    parsed_data['Length'] = message[3]
    print("StringLength:", (message[3]))

    logString = ""

    for i in range(0, (message[3])):
        logString = logString + chr((message[i+5]))
 
    print("logString:", logString)

    data = logString.split("|")
    
    data = [data[i].split(",") for data in range(len(data))]

    for i in range(len(data)):
        
        parsed_data['Address' + str(i)] = data[i][5]
        parsed_data['Version' + str(i)] = data[i][2]
        parsed_data['State' + str(i)]   = data[i][1]
        parsed_data['StatStr' + str(i)] = data[i][4]
        parsed_data['Value' + str(i)]   = data[i][3]
        
    BUFFER = pd.concat([BUFFER, pd.DataFrame(parsed_data)])
    
    return logString


def setAndReturnSwarmID(incomingID):
    global SWARMSTATUS

    for i in range(0, SWARMSIZE):
        if (SWARMSTATUS[i][5] == incomingID):
            return i

        else:

            if (SWARMSTATUS[i][5] == 0):  # not in the system, so put it in

                SWARMSTATUS[i][5] = incomingID
                
                print("incomingID %d " % incomingID)
                print("assigned #%d" % i)
                
                return i

    # if we get here, then we have a new swarm member.
    # Delete the oldest swarm member and add the new one in
    # (this will probably be the one that dropped out)

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

def button_interrupt(channel):
   
    global BUFFER

    # Reset SWARMSTATUS.
    
    reset_swarm_status()

    # Save BUFFER to file.

    BUFFER.to_csv(f"{time.time()}.csv")

    # Reset BUFFER.

    BUFFER = pd.DataFrame(columns=['Timestamp', 'Master', 'Version', 'Length'] + [i for i in range(SWARMSIZE)])

    # Reset graphs?
    # Flush the network card 

    # Reset the swarm

    SendRESET_SWARM_PACKET(SOCKET)
    
    # Turn the light on for 3 seconds

    GPIO.output(LED, GPIO.HIGH)
    
    time.sleep(3)
    
    GPIO.output(LED, GPIO.LOW)
    
    # Redefine server logger for the swarm

    SendDEFINE_SERVER_LOGGER_PACKET(SOCKET)


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


def loop():

    global RESET_TIME
    global SWARMSTATUS
    global PRESSED

    while(1):

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
