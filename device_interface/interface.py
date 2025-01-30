import matplotlib.pyplot as plt
# import pygame
import serial
import time



class leonado:
    # serleonado = serial.Serial(port='/dev/cu.usbmodem11401', baudrate=115200, timeout=.1) # mac
    serleonado = serial.Serial(port='COM18', baudrate=115200, timeout=.1) # windows
    serleonado.timeout = 1
    def read_write_string(string, print_response = True):
        string = str(string.strip())
        leonado.serleonado.write(string.encode())
        time.sleep(0.01)
        ser_return = leonado.serleonado.readline().decode('ascii')

        if print_response: print(ser_return)
        time.sleep(0.01)
        
        return ser_return


class operation():
    laser_frequency = 1 # hz
    def datacollection():
        pass
    def system_matrix_dc(): # run system_matrix data collection
        leonado.read_write_string('LED_BLINKIN1')
        leonado.read_write_string('FIREL1')

        # move interval
        for y in range (0, 40):
            for x in range(0, 40):
                leonado.read_write_string(f'MOVE {x} {y}')
                time.sleep(1/operation.laser_frequency)
                print(x,y)

        leonado.read_write_string('MOVE 0 0')
        leonado.read_write_string('FIREL0')
        leonado.read_write_string('LED_BLINKIN0')


# operation.system_matrix_dc()


# for i in range(0, 40, 10):
#     command = f'MOVE {i} 0'
#     print(command)
#     leonado.rw_string(command)



# leonado.rw_string('MOVE 0 0')

# while True:
#     leonado.rw_string('LED_BUILTIN1')
#     time.sleep(0.3)
#     leonado.rw_string('LED_BUILTIN0')
#     time.sleep(0.3)
    