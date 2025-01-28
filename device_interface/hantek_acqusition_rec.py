from hantek_acqusition import ControlData, RelayControl, search_device, ht_hard_dll, dsoHTGetData,dsoHTGetRollData, connect_device, dsoInitHard, dsoHTADCCHModGain, dsoHTSetSampleRate, dsoHTSetCHAndTrigger, dsoHTSetRamAndTrigerControl, dsoHTSetCHPos, dsoHTSetAmpCalibrate, dsoHTSetVTriggerLevel, dsoHTSetTrigerMode, dsoHTGetState, dsoHTStartCollectData, dsoHTGetData, dsoHTGetRollData, dsoHTSetSampleRate, dsoHTSetVTriggerLevel, dsoHTSetTrigerMode, dsoHTSetAmpCalibrate
import matplotlib.pyplot as plt
from ctypes import c_uint16, POINTER, c_uint, c_ushort
import os, json, time



hantek_settings_json_path = os.path.join(os.getcwd(), 'device_interface/hantek_settings.json')


with open(hantek_settings_json_path, 'r') as f:
    settings = json.load(f)
device_index = settings['device_index']

control_data = ControlData()
control_data.nCHSet = 0b1000  # disable all four channels (CH1, CH2, CH3, CH4)
control_data.nCHSet |= (1 << 0)  # Enable CH1
control_data.nCHSet |= (1 << 2)  # Enable CH3
control_data.nTimeDIV = settings['control_data']['nTimeDIV']
control_data.nTriggerSource = settings['control_data']['nTriggerSource']
control_data.nHTriggerPos = settings['control_data']['nHTriggerPos']
control_data.nVTriggerPos = settings['control_data']['nVTriggerPos']
control_data.nTriggerSlope = settings['control_data']['nTriggerSlope']
control_data.nBufferLen = settings['control_data']['nBufferLen']
control_data.nReadDataLen = settings['control_data']['nReadDataLen']
control_data.nAlreadyReadLen = settings['control_data']['nAlreadyReadLen']
control_data.nALT = settings['control_data']['nALT']
control_data.nETSOpen = settings['control_data']['nETSOpen']



nYTFormat = settings['nYTFormat'] # mode of horizontal format 0-normal, 1-Scan, 2-Roll
search_device()
connect_device(in_device_index = device_index)



def recent_change(file_path, seconds_threshold=10):
    if not os.path.exists(file_path): return False
    
    last_modified = os.path.getmtime(file_path)
    current_time = time.time()
    return current_time - last_modified <= seconds_threshold
    
def convert_to_lp_c_ushort(data_list):
    if not all(0 <= x <= 65535 for x in data_list):  # Ensure all values fit in c_ushort
        raise ValueError("All values in the list must be between 0 and 65535.")
    
    ushort_array = (c_ushort * len(data_list))(*data_list)  # Create a ctypes array
    return POINTER(c_ushort)(ushort_array)  # Return a pointer to the array

def __configure__():
    print("Configuring Hantek Device")
    with open(hantek_settings_json_path, 'r') as f:
        settings = json.load(f)
    device_index = settings['device_index']
    control_data = ControlData()
    control_data.nCHSet = 0b1000  # disable all four channels (CH1, CH2, CH3, CH4)
    control_data.nCHSet |= (1 << 0)  # Enable CH1
    control_data.nCHSet |= (1 << 2)  # Enable CH3
    control_data.nTimeDIV = settings['control_data']['nTimeDIV']
    control_data.nTriggerSource = settings['control_data']['nTriggerSource']
    control_data.nHTriggerPos = settings['control_data']['nHTriggerPos']
    control_data.nVTriggerPos = settings['control_data']['nVTriggerPos']
    control_data.nTriggerSlope = settings['control_data']['nTriggerSlope']
    control_data.nBufferLen = settings['control_data']['nBufferLen']
    control_data.nReadDataLen = settings['control_data']['nReadDataLen']
    control_data.nAlreadyReadLen = settings['control_data']['nAlreadyReadLen']
    control_data.nALT = settings['control_data']['nALT']
    control_data.nETSOpen = settings['control_data']['nETSOpen']
    relay_control = RelayControl()
    # Enable channels CH1 and CH2, disable CH3 and CH4
    relay_control.bCHEnable[0] = settings['relay_control']['bCHEnable'][0]   # Enable CH1
    relay_control.bCHEnable[1] = settings['relay_control']['bCHEnable'][1]
    relay_control.bCHEnable[2] = settings['relay_control']['bCHEnable'][2]
    relay_control.bCHEnable[3] = settings['relay_control']['bCHEnable'][3]
    # Set voltage divisions for each channel
    relay_control.nCHVoltDIV[0] = settings['relay_control']['nCHVoltDIV'][0]
    relay_control.nCHVoltDIV[1] = settings['relay_control']['nCHVoltDIV'][1]
    relay_control.nCHVoltDIV[2] = settings['relay_control']['nCHVoltDIV'][2]
    relay_control.nCHVoltDIV[3] = settings['relay_control']['nCHVoltDIV'][3]
    # Set channel coupling (1: DC, 2: AC, 4: GND)
    relay_control.nCHCoupling[0] = settings['relay_control']['nCHCoupling'][0]
    relay_control.nCHCoupling[1] = settings['relay_control']['nCHCoupling'][1]
    relay_control.nCHCoupling[2] = settings['relay_control']['nCHCoupling'][2]
    relay_control.nCHCoupling[3] = settings['relay_control']['nCHCoupling'][3]
    # Set bandwidth limit (1: ON, 0: OFF)
    relay_control.bCHBWLimit[0] = settings['relay_control']['bCHBWLimit'][0]
    relay_control.bCHBWLimit[1] = settings['relay_control']['bCHBWLimit'][1]
    relay_control.bCHBWLimit[2] = settings['relay_control']['bCHBWLimit'][2]
    relay_control.bCHBWLimit[3] = settings['relay_control']['bCHBWLimit'][3]
    print('starting configuration')

    dsoInitHard(device_index)
    dsoHTADCCHModGain(device_index, nCHMode= settings['nCHMode'])
    dsoHTSetSampleRate(device_index, nYTFormat= nYTFormat, RELAYCONTROL=relay_control, CONTROL=control_data)
    dsoHTSetCHAndTrigger(device_index, RELAYCONTROL= relay_control, nTimeDIV= control_data.nTimeDIV)
    dsoHTSetRamAndTrigerControl(device_index, nTimeDiv=control_data.nTimeDIV, nCHset=control_data.nCHSet, nTrigerSource=control_data.nTriggerSource, nPeak=0)
    nPos_channels = settings['nPos_channels']
    for i in range(4):
        dsoHTSetCHPos(device_index, nVoltDIV=relay_control.nCHVoltDIV[i], nPos=nPos_channels[i], nCH=i, nCHMode=relay_control.nCHCoupling[i])
        dsoHTSetAmpCalibrate(device_index, nCHSet=settings['control_data']['nCHSet'], nTimeDIV=control_data.nTimeDIV, nVoltDiv=relay_control.nCHVoltDIV[i], pCHPOS=convert_to_lp_c_ushort(settings['nPos_channels'])) 
        
    dsoHTSetSampleRate(device_index, nYTFormat= nYTFormat, RELAYCONTROL=relay_control, CONTROL=control_data)
    dsoHTSetVTriggerLevel(device_index, nPos= settings['nPos_trigger'], nSensitivity=settings['nSensitivity_trigger'])
    dsoHTSetTrigerMode(device_index, nTriggerMode=settings["nTriggerMode"], nTriggerSlop= settings["nTriggerSlop"], nTriggerCouple= settings["nTriggerCouple"])


__configure__()


plt.ion()

while True:
    if recent_change(hantek_settings_json_path, seconds_threshold=1) == True: __configure__()
    if dsoHTGetState(device_index) != 0:
        pCH1DATA, pCH2DATA, pCH3DATA, pCH4DATA = (c_uint16 * control_data.nBufferLen)(), (c_uint16 * control_data.nBufferLen)(), (c_uint16 * control_data.nBufferLen)(), (c_uint16 * control_data.nBufferLen)()
        dsoHTGetRollData(device_index, pCH1DATA, pCH2DATA, pCH3DATA, pCH4DATA, control_data)
        plt.plot(pCH1DATA)
        plt.draw()
        plt.pause(0.0001)
        plt.clf()




continuous_data_CH1 : list = []
continuous_data_CH2 : list = []
continuous_data_CH3 : list = []
continuous_data_CH4 : list = []
    
    
i = 0

while i < 10:
    if dsoHTGetState(device_index) != 0:
        pCH1DATA, pCH2DATA, pCH3DATA, pCH4DATA = (c_uint16 * control_data.nBufferLen)(), (c_uint16 * control_data.nBufferLen)(), (c_uint16 * control_data.nBufferLen)(), (c_uint16 * control_data.nBufferLen)()
        dsoHTGetData(device_index, pCH1DATA, pCH2DATA, pCH3DATA, pCH4DATA, control_data)

        continuous_data_CH1.extend(list(pCH1DATA))
        continuous_data_CH2.extend(list(pCH2DATA))
        i += 1
    dsoHTStartCollectData(device_index, nStartControl=0)

 
 
 
fig , ax = plt.subplots()
x_data, y_data = [], []
line, = ax.plot([], [], lw=2)
ax.set_xlim(0, 280)
ax.set_ylim(0, 4096)
def update(frame):
    pass


# print("SHOWING COMPLETED DATA")

# fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(8, 6), sharex=True)
# axes[0].plot(continuous_data_CH1)
# axes[0].set_ylim(0, 350)
# axes[0].legend(['ultrasonic data'])

# # axes[1].plot(continuous_data_CH2)
# # axes[1].set_ylim(0, 350)
# # axes[1].legend(['Laser Firing'])
# plt.show()


# nStartControl 0:1 AUTO trigger, 1:1 Roll Mode, 2:1 stop after this collect 



# from scipy.io import savemat, loadmat
# import numpy as np
# import json


# datajson_save_dir = os.path.join(os.getcwd(), 'device_interface', 'data.json')

# with open(datajson_save_dir, 'r') as f:
#     data_json_loaded = json.load(f)
# with open(datajson_save_dir, 'w') as f:
#     data_json_loaded['ultrasound'].append(list(continuous_data_CH1))
#     data_json_loaded['sig'].append(list(continuous_data_CH2))
#     json.dump(data_json_loaded, f, indent=4)
    