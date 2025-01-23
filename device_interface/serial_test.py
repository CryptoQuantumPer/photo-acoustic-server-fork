import serial
import time

serialcomm = serial.Serial(port='/dev/cu.usbmodem11401', baudrate=115200, timeout=.1)
serialcomm.timeout = 1
while True:
    i = input ("input (on/off): ").strip()
    if i == 'done':
        print('finished program')
        break
    serialcomm.write (i .encode ())
    time.sleep (0.01)
    print(serialcomm.readline().decode ('ascii'))
serialcomm.close ()