# Brian Lesko
# This file contains supporting code for the main app
# 11/22/23 

# Open serial communication with an arduino from a python script using the library pyserial using this class.

import serial # !pip install pyserial
import serial.tools.list_ports

class arduino:

    def __init__(self,port,baude_rate,timeout):
        self.port = port
        self.baude_rate = baude_rate
        self.timeout = timeout
        self.serial = serial.Serial(port=port, baudrate=baude_rate, timeout=timeout)
        # raise an error if the port is not open
        if not self.isconnected():
            raise Exception("Could not open serial port: " + str(port))

    def isconnected(self): 
        return self.serial.isOpen()

    def disconnect(self):
        self.serial.close()

    def send(self,command):
        command = command + '\n'
        self.serial.write(command.encode('utf-8'))

    def read(self):
        self.serial.flushInput()
        response = self.serial.readline().decode('utf-8')
        return response
    
    def read2(self):
        data = ""
        while self.serial.inWaiting() > 0:
            data += self.serial.readline().decode().strip()
        return data

    # Send a command and receive a response
    def send_and_receive(self,command):
        command = command + '\n'
        self.serial.write(command.encode('utf-8'))
        response = self.serial.readline().decode('utf-8')
        return response
    
    def isconnected(self):
        return self.serial.isOpen()
    
    def any(self):
        # returns true if there is data in the buffer
        return self.serial.inWaiting() > 0
    
    @classmethod
    def list_ports(cls):
        ports = serial.tools.list_ports.comports()
        available_ports = [port.device for port in ports]
        return available_ports

    
def example():
    # port = '/dev/ttyACM0' # on the raspberry pi, this is the port that the arduino is connected to
    port = '/dev/tty.usbmodemF412FA9FD4E42' # on mac you must go to the terminal and type 'ls /dev/tty.*' to find the port
    # port = 'COM4' # Windows port 
    my_arduino = arduino(port,9600,.1)

    command = "ON"
    response = my_arduino.send_and_receive(command)
    command = "OFF"
    response = my_arduino.send_and_receive(command)
    my_arduino.disconnect()

    # Hey It's Brian. remember you have to write a code on the ardino to listen for a serial communication