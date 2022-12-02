'''
**********************************************************************
* Filename    : dot_matrix.py
* Description : Script show charactors and pictures on 8*8 led
*               dot matrix.
* Author      : Cavon
* Brand       : SunFounder
* E-mail      : service@sunfounder.com
* Website     : www.sunfounder.com
* Update      : Cavon    2016-10-18    New release
**********************************************************************
'''

import RPi.GPIO as GPIO
import time
import plotPoints

SDI   = 17
RCLK  = 18
SRCLK = 27

per_line = [0xfe, 0xfd, 0xfb, 0xf7, 0xef, 0xdf, 0xbf, 0x7f]


def print_msg():
    print('Program is running...')
    print('Please press Ctrl+C to end the program...')


def setup():
    GPIO.setmode(GPIO.BCM)    # Number GPIOs by its BCM location
    GPIO.setup(SDI, GPIO.OUT)
    GPIO.setup(RCLK, GPIO.OUT)
    GPIO.setup(SRCLK, GPIO.OUT)
    GPIO.output(SDI, GPIO.LOW)
    GPIO.output(RCLK, GPIO.LOW)
    GPIO.output(SRCLK, GPIO.LOW)


# Shift the data to 74HC595
# Writes to row
def serial_write_to_matrix(data):
    
    for bit in range(0, 8):
    
        GPIO.output(SDI, 1 & (data >> bit))
        
        GPIO.output(SRCLK, GPIO.HIGH)
        
        time.sleep(0.000001)
        
        GPIO.output(SRCLK, GPIO.LOW)


def flush_led_matrix():
    
    GPIO.output(RCLK, GPIO.HIGH)
    
    time.sleep(0.000001)
    
    GPIO.output(RCLK, GPIO.LOW)


def flash(table):
    
    for i in range(8):
        
        serial_write_to_matrix(per_line[i])

        serial_write_to_matrix(table[i])
        
        flush_led_matrix()

        # Clean up last line
        #if i >= 8:
        #    hc595_in(per_line[7])
        #    hc595_in(0x00)
        #    hc595_out()


def show(table, second):
    
    start = time.time()
    
    while True:
    
        flash(table)
        
        finish = time.time()
        
        if finish - start > second:
            break


def main():
    luminosity = [10,11,12,13,14,15,16,17]
    while True:
        for i in range(64):
            show(plotPoints.luminosity[i], 0.1)
        # time.sleep(1)


def destroy():

    GPIO.cleanup()


if __name__ == '__main__':
    setup()
    try:
        main()
    except KeyboardInterrupt:
        destroy()
