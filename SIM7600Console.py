#!/usr/bin/python
# -*- coding:utf-8 -*-
import RPi.GPIO as GPIO
import serial
import time

ser = serial.Serial('/dev/ttyS0', 115200)
try:
    ser.flushInput()
except serial.serialutil.PortNotOpenError:
    print("Serial port not open. ")
power_key = 6
rec_buff = ''
rec_buff2 = ''
time_count = 0


class color:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def power_on(power_key):
    print('Starting SIM7600.')
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(power_key, GPIO.OUT)
    time.sleep(0.1)
    GPIO.output(power_key, GPIO.HIGH)  # Presses power button in to turn on.
    time.sleep(2)
    GPIO.output(power_key, GPIO.LOW)  # Releases power button.
    time.sleep(20)
    ser.flushInput()
    print('SIM7600 is ready\n')


def power_down(power_key):
    print('Powering down SIM7600X.')
    GPIO.output(power_key, GPIO.HIGH)  # Presses power button in to turn off.
    time.sleep(3)
    GPIO.output(power_key, GPIO.LOW)  # Releases power button.
    time.sleep(18)
    print('SIM7600 is shut down.')


def shutdown():
    """
    Performs necessary operations for proper shutdown of SIM7600.
    """
    send('AT+CGPS=0', 1)
    # send('AT+CGPSDEL', 1)  # Required by documentation at the end of each use.
    if ser is not None:
        ser.close()
    power_down(power_key)
    GPIO.cleanup()


def send(command, timeout):  # 132164
    buffer_read = ''
    ser.write((command + '\r\n').encode())
    time.sleep(1)
    try:
        time.sleep(timeout)
    except KeyboardInterrupt:
        shutdown()
    if ser.inWaiting():
        time.sleep(0.01)
        buffer_read = ser.read(ser.inWaiting())
        return buffer_read.decode()
    else:
        return 0


def read():
    buffer_read = ''
    if ser.inWaiting():
        time.sleep(0.01)
        buffer_read = ser.read(ser.inWaiting())
    if buffer_read != '':
        return buffer_read.decode()


def console():
    repeat = ''
    menu_txt = (f'{color.HEADER}{color.UNDERLINE}Console Commands{color.ENDC}\n'
                f'{color.BOLD}Settings{color.ENDC} - Get current SIM7600 settings.\n'
                f'{color.BOLD}Read{color.ENDC} - reads from buffer.\n'
                f'{color.BOLD}Exit{color.ENDC} - exits loop and ends program after shutting SIM7600 down.\n'
                f'{color.BOLD}ExitHot{color.ENDC} - terminates Python without shutting down. (Good for updating Python code).\n'
                f'{color.BOLD}Reboot{color.ENDC} - Shuts SIM7600 down and turns it back om.\n'
                f'{color.BOLD}PowerOn{color.ENDC} - Turns on SIM7600.\n'
                f'{color.BOLD}PowerOff{color.ENDC} - Turns SIM7600 off (keeps serial lines open).\n'
                f'{color.BOLD}Repeat{color.ENDC} - repeats previous command.\n'
                f'{color.BOLD}Exec: <command>{color.ENDC} - Executes Python command.\n'
                f'{color.BOLD}Eval: <command>{color.ENDC} - Executes Python command and prints result.\n'
                f'{color.WARNING}All other commands are sent to SIM7600 GPS/LTE HAT.{color.ENDC}\n\n')
    print(menu_txt)
    while True:
        cli = input('Command: ')
        if cli.lower() == 'repeat':
            cli = repeat
        if cli.lower() == "settings":
            print('Current SIM7600 configuration:')
            commands = 'AT+CGPS?;+CGPSNMEA?;+CGPSINFOCFG?'
            send(commands, 1)
        elif cli.lower() == "exit":
            print('Exiting loop and shutting down.')
            break
        elif cli.lower() == "exithot":
            print('Terminating program.\nGoodbye')
            exit()
        elif cli.lower() == "reboot":
            print('Rebooting program.\n')
            shutdown()
            ser = serial.Serial('/dev/ttyS0', 115200)
            power_on(power_key)
        elif cli.lower() == "poweron":
            print('Turning SIM7600 on.\n')
            power_on(power_key)
        elif cli.lower() == "poweroff":
            print('Turning SIM7600 off.\n')
            power_down(power_key)
        elif cli.lower() == "read":
            print('Reading from buffer:\n')
            buffer = read()
            if buffer is not None or 0:
                gps_status = parse_gps(buffer)
                print(gps_status)
            else:
                print('Buffer empty.')
        elif 'eval:' in cli.lower():
            command = cli[5:]
            print(f'Executing Python eval command.\neval("{command}")')
            result = eval(f"{command}")
            print(f'Result: {result}')
        elif 'exec:' in cli.lower():
            command = cli[5:]
            print(f'Executing Python exec command.\nexec("{command}")')
            exec(f"{command}")
            print(f'Result: {result}')
        elif cli.lower() == 'help':
            print(menu_txt)
        else:
            print('Sending command to HAT.\n')
            result = send(cli, 1)
            print(str(result))
        repeat = cli


def parse_gps(gps):
    gps_status = {'GPS': 0,  # Set dictionary with number of satellites in view.
                  'GLONASS': 0,
                  'GALILEO': 0,
                  'BEIDOU': 0}
    gps = gps.splitlines()  # SIM7600 buffer returns different NMEA sentences on new lines.
    for line in range(len(gps)):  # Iterate through each NMEA sentence.
        gps[line] = gps[line].split(',')  # NMEA sentence information diliminated by commas. Split into list.
        for item in range(len(gps[line])):  # Iterate through each item of NMEA sentence.
            gps[line][item] = gps[line][item].replace(' ', '')  # Remove extra white space in list.
            if gps[line][0] == '$GPGSV':  # GP = GPS / GSV = Satellites in View
                gps_status['GPS'] = int(gps[line][3])  # gps[line][3] is the index for the GSV number.
            elif gps[line][0] == '$GLGSV':  # GL = GLONASS / GSV = Satellites in View
                gps_status['GLONASS'] = int(gps[line][3])
            elif gps[line][0] == '$GAGSV':  # GA = GALILEO / GSV = Satellites in View
                gps_status['GALILEO'] = int(gps[line][3])
            elif gps[line][0] == '$BDGSV':  # BD = BEIDOU / GSV = Satellites in View
                gps_status['BEIDOU'] = int(gps[line][3])
    return gps_status


test = send('AT+CGPS=?', 1)  # Check if SIM7600 module is on.
if test == 0:  # 0 returned if power is off.
    power_on(power_key)
else:
    print('SIM7600 is already powered on.')
    GPIO.setmode(GPIO.BCM)  # GPIO normally set during power_on - required here for hot start.
    GPIO.setwarnings(False)
    GPIO.setup(power_key, GPIO.OUT)


if __name__ == "__main__":
    console()
    shutdown()
