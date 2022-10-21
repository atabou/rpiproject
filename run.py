
import time
import socket
import RPi.GPIO as GPIO

"""
Setup UDP socket
"""

UDP_LOCAL_IP = "0.0.0.0"
UDP_LOCAL_PORT = 4210

UDP_TARGET_IP = "192.168.86.29"
UDP_TARGET_PORT = 4210

udp = None

"""
Setup button
"""

PRESSED = False
BUTTON = 22


def button_interrupt(channel):
    global PRESSED
    PRESSED = True


"""
Setup WGYR LEDs
"""

WLED = 32
GLED = 36
YLED = 38
RLED = 40

FLASHING_PERIOD = 1 # 1 second

TRESHOLD = 1024

"""
Setup time related variables
"""

TIME_STAMP = 0
TIME_LIMIT = 10


"""
Setup finite state machine
"""

# Language symbols

press = 0
stay = 1
low = 2
med = 3
high = 4
limit = 5


# Function states

def start():

    global PRESSED
    global TIME_STAMP

    # Runs if the button was pressed
    if PRESSED:
        PRESSED = False
        TIME_STAMP = time.time()
        return press

    # Interval to rerun the start state
    time.sleep(0.2)

    return stay


# Steps to follow in w state

def w():

    global PRESSED
    global TIME_STAMP
    global TIME_LIMIT
    global TRESHOLD

    # Turn white LED on and all others off
    GPIO.output(WLED, GPIO.HIGH)
    GPIO.output(GLED, GPIO.LOW)
    GPIO.output(YLED, GPIO.LOW)
    GPIO.output(RLED, GPIO.LOW)

    # Check for button press
    if PRESSED:
        PRESSED = False
        return press

    # Check for udp

    try:

        data, _ = udp.recvfrom(1024)
 
        TIME_STAMP = time.time()

        if int(data) < TRESHOLD / 3:
            return low

        elif int(data) < 2 * TRESHOLD / 3:
            return med

        else:
            return high

    except BlockingIOError:
        pass

    # Check for time
    if time.time() - TIME_STAMP > TIME_LIMIT:
        return limit

    time.sleep(0.2)

    return stay


# Steps to follow in wg state

def wg():

    global PRESSED
    global TIME_STAMP
    global TIME_LIMIT
    global TRESHOLD

    # Turn white LED on and all others off
    GPIO.output(WLED, GPIO.HIGH)
    GPIO.output(GLED, GPIO.HIGH)
    GPIO.output(YLED, GPIO.LOW)
    GPIO.output(RLED, GPIO.LOW)

    # Check for button press
    if PRESSED:
        
        PRESSED = False
        return press

    # Check for udp
    try:
        
        data, _ = udp.recvfrom(1024)        

        TIME_STAMP = time.time()

        if int(data) < TRESHOLD / 3:
            return low

        elif int(data) < 2 * TRESHOLD / 3:
            return med

        else:
            return high

    except BlockingIOError:
        pass

    # Check for time
    if time.time() - TIME_STAMP > TIME_LIMIT:
        return limit

    time.sleep(0.2)
    
    # No state change
    return stay


def wgy():

    global PRESSED
    global TIME_STAMP
    global TIME_LIMIT
    global TRESHOLD
    
    # Turn white LED on and all others off
    GPIO.output(WLED, GPIO.HIGH)
    GPIO.output(GLED, GPIO.HIGH)
    GPIO.output(YLED, GPIO.HIGH)
    GPIO.output(RLED, GPIO.LOW)

    # Check for button press 
    if PRESSED:
        PRESSED = False
        return press

    # Check for udp
    try:
        data, _ = udp.recvfrom(1024)

        TIME_STAMP = time.time()

        if int(data) < TRESHOLD / 3:
            return low

        elif int(data) < 2 * TRESHOLD / 3:
            return med

        else:
            return high

    except BlockingIOError:
        pass

    # Check for time
    if time.time() - TIME_STAMP > TIME_LIMIT:
        return limit

    time.sleep(0.2)
    
    # No state change
    return stay


def wgyr():

    global PRESSED
    global TIME_STAMP
    global TIME_LIMIT
    global TRESHOLD
    
    # Turn WGYR onq
    GPIO.output(WLED, GPIO.HIGH)
    GPIO.output(GLED, GPIO.HIGH)
    GPIO.output(YLED, GPIO.HIGH)
    GPIO.output(RLED, GPIO.HIGH)

    # Check for button press 
    if PRESSED:
        PRESSED = False
        return press

    # Check for udp
    try:
        data, _ = udp.recvfrom(1024)

        TIME_STAMP = time.time()

        if int(data) < TRESHOLD / 3:
            return low

        elif int(data) < 2 * TRESHOLD / 3:
            return med

        else:
            return high

    except BlockingIOError:
        pass

    # Check for time
    if time.time() - TIME_STAMP > TIME_LIMIT:
        return limit

    time.sleep(0.2)

    # No state change
    return stay


def flashing():

    global PRESSED
    global FLASHING_PERIOD

    # Turn all Color LED off
    GPIO.output(WLED, GPIO.HIGH)
    GPIO.output(YLED, GPIO.LOW)
    GPIO.output(RLED, GPIO.LOW)
    GPIO.output(GLED, GPIO.LOW)

    if PRESSED:
        PRESSED = False
        return press

    # Flash the while LED

    time.sleep(float(FLASHING_PERIOD) / 2)

    GPIO.output(WLED, GPIO.LOW)

    time.sleep(float(FLASHING_PERIOD) / 2)

    # No state change
    return stay


def wgyr_off():

    global udp

    # Send stop message
    udp.sendto("stop".encode(), (UDP_TARGET_IP, UDP_TARGET_PORT))

    # Turn the socket off

    udp.close()

    # Turn all LEDs off
    GPIO.output(GLED, GPIO.LOW)
    GPIO.output(YLED, GPIO.LOW)
    GPIO.output(RLED, GPIO.LOW)
    GPIO.output(WLED, GPIO.LOW)

    # Send UDP stop message

    time.sleep(0.5)

    # Anything can be returned
    return 0


def connect():

    global udp

    # Bind socket to port

    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    udp.setblocking(0)

    udp.bind((UDP_LOCAL_IP, UDP_LOCAL_PORT))

    # Send start message
    udp.sendto("start".encode(), (UDP_TARGET_IP, UDP_TARGET_PORT))

    # Anything can be returned
    return 0


states = [start, w, wg, wgy, wgyr, flashing, wgyr_off, connect]

# Current state variable initialized to start state

current_state = 0

# Transition matrix for FSM

transition_matrix = [

    [7, 0, -1, -1, -1, -1],
    [6, 1,  2,  3,  4,  5],
    [6, 2,  2,  3,  4,  5],
    [6, 3,  2,  3,  4,  5],
    [6, 4,  2,  3,  4,  5],
    [6, 5, -1, -1, -1, -1],
    [0, 0,  0,  0,  0,  0],
    [1, 1,  1,  1,  1,  1]

]

"""
Start running the application
"""

if __name__ == '__main__':

    try:
        # Start the display

        # display.begin()

        # time.sleep(2)

        # display.clear()

        # Initialize GPIO Pins

        GPIO.setmode(GPIO.BOARD)

        GPIO.setup(WLED, GPIO.OUT)
        GPIO.setup(GLED, GPIO.OUT)
        GPIO.setup(YLED, GPIO.OUT)
        GPIO.setup(RLED, GPIO.OUT)

        GPIO.output(GLED, GPIO.LOW)
        GPIO.output(YLED, GPIO.LOW)
        GPIO.output(RLED, GPIO.LOW)
        GPIO.output(WLED, GPIO.LOW)

        # Set interupt for when the button is pressed

        GPIO.setup(BUTTON, GPIO.IN, GPIO.PUD_UP)

        GPIO.add_event_detect(BUTTON, GPIO.FALLING, callback=button_interrupt, bouncetime=200)

        # Loop over finite state machine

        while(True):

            symbol = states[current_state]()

            current_state = transition_matrix[current_state][symbol]

            if current_state == -1:
                print("Error! Resetting to start state")
                current_state == 0

    except KeyboardInterrupt:

        GPIO.cleanup()
        print("Interrupted")
