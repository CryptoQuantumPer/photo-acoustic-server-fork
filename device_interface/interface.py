import matplotlib.pyplot as plt
# import pygame
import serial
import time



class leonado:
    serleonado = serial.Serial(port='/dev/cu.usbmodem11401', baudrate=115200, timeout=.1)
    serleonado.timeout = 1
    def read_write_string(string, print_response = True):
        string = string.strip()
        leonado.serleonado.write(string.encode())
        time.sleep(0.01)
        ser_return = leonado.serleonado.readline().decode ('ascii')

        if print_response: print(ser_return)
        return ser_return
        


while True:
    leonado.read_write_string('LED_BUILTIN1')
    time.sleep(0.3)
    leonado.read_write_string('LED_BUILTIN0')
    time.sleep(0.3)
    