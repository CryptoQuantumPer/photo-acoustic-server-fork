import ctypes
from ctypes import c_short, POINTER, c_uint, c_uint16, c_uint32, c_bool, c_int64, c_int16, c_ushort
import os
import matplotlib.pyplot as plt

dll_x64_path = os.path.join(os.getcwd(), 'device_interface', 'HT6004BX_SDK', 'DLL', 'x64')
ht_hard_dll = ctypes.WinDLL(os.path.join(dll_x64_path, 'HTHardDll.dll'))

# dll_x64_path = os.path.join(os.getcwd(), 'device_interface', 'HT6022_SDK', 'Hantek6022BE')
# ht_hard_dll_2 = ctypes.WinDLL(os.path.join(dll_x64_path, 'HTMarch.dll'))

device_index = 0

def search_device(return_buffer_size = 32):
    # ht_hard_dll.dsoHTSearchDevice.argtypes = [POINTER(c_short)]
    # ht_hard_dll.dsoHTSearchDevice.restype = c_uint
    device_info = (c_short * return_buffer_size)()
    result = ht_hard_dll.dsoHTSearchDevice(device_info)
    if result == 0:
        print(f'Founded device(s):')
    elif result == 1: print('No device found')
    return device_info

# dsoHTDeviceConnect
def connect_device(in_device_index: int = 0):
    device_index = in_device_index
    # ht_hard_dll.dsoHTDeviceConnect.argtypes = [c_uint]
    # ht_hard_dll.dsoHTDeviceConnect.restype = c_uint
    rr_con = ht_hard_dll.dsoHTDeviceConnect(device_index)
    if rr_con: print(f'dv{device_index} Connected successfully!')
    else: 
        print('FAIL: dsoHTDeviceConnect')
        exit()
        
        

def dsoInitHard(device_index):
    # ht_hard_dll.dsoInitHard.argtypes = [c_uint16]
    # ht_hard_dll.dsoInitHard.restype = c_uint
    state = ht_hard_dll.dsoInitHard(device_index)
    if state != 0: print(f'dsoInitHard of dv{device_index} succeed')
    else: print(f'fail dsoInitHard to dv{device_index}')
    return state

def dsoHTADCCHModGain(device_index, nCHMode):
    # ht_hard_dll.dsoHTADCCHModGain.argtypes = [c_uint16, c_uint16]
    # ht_hard_dll.dsoHTADCCHModGain.restype = c_uint
    state = ht_hard_dll.dsoHTADCCHModGain(device_index, nCHMode)
    if state != 0: print(f'dsoHTADCCHModGain of dv{device_index} succeed')
    else: print(f'fail dsoHTADCCHModGain to dv{device_index}')
    return state

def dsoHTSetSampleRate(device_index, nYTFormat, RELAYCONTROL, CONTROL):
    # ht_hard_dll.dsoHTSetSampleRate.argtypes = [c_uint16, c_uint16, POINTER(RelayControl), POINTER(ControlData)]
    # ht_hard_dll.dsoHTSetSampleRate.restype = c_uint16
    state = ht_hard_dll.dsoHTSetSampleRate(device_index, nYTFormat, ctypes.byref(RELAYCONTROL), ctypes.byref(CONTROL))
    if state != 0: print(f'dsoHTSetSampleRate of dv{device_index} succeed')
    else: print(f'fail dsoHTSetSampleRate to dv{device_index}')
    return state

def dsoHTSetCHAndTrigger(device_index, RELAYCONTROL, nTimeDIV):
    # ht_hard_dll.dsoHTSetCHAndTrigger.argtypes = [c_uint16, POINTER(RelayControl), c_uint16]
    # ht_hard_dll.dsoHTSetCHAndTrigger.restype = c_uint16
    state = ht_hard_dll.dsoHTSetCHAndTrigger(device_index, ctypes.byref(RELAYCONTROL), nTimeDIV)
    if state != 0: print(f'dsoHTSetCHAndTrigger of dv{device_index} succeed')
    else: print(f'fail dsoHTSetCHAndTrigger to dv{device_index}')
    return state

def dsoHTSetRamAndTrigerControl(device_index, nTimeDiv, nCHset, nTrigerSource, nPeak):
    # ht_hard_dll.dsoHTSetRamAndTrigerControl.argtypes = [c_uint16, c_uint16, c_uint16, c_uint16, c_uint16]
    # ht_hard_dll.dsoHTSetRamAndTrigerControl.restype = c_uint16
    state = ht_hard_dll.dsoHTSetRamAndTrigerControl(device_index, nTimeDiv, nCHset, nTrigerSource, nPeak)
    if state != 0: print(f'dsoHTSetRamAndTrigerControl of dv{device_index} succeed')
    else: print(f'fail dsoHTSetRamAndTrigerControl to dv{device_index}')
    return state

def dsoHTSetCHPos(device_index, nVoltDIV, nPos, nCH, nCHMode):
    # ht_hard_dll.dsoHTSetCHPos.argtypes = [c_uint16, c_uint16, c_uint16, c_uint16, c_uint16]
    # ht_hard_dll.dsoHTSetCHPos.restype = c_uint16
    state = ht_hard_dll.dsoHTSetCHPos(device_index, nVoltDIV, nPos, nCH, nCHMode)
    if state != 0: print(f'dsoHTSetCHPos of dv{device_index} succeed')
    else: print(f'fail dsoHTSetCHPos to dv{device_index}')
    return state

def dsoHTSetVTriggerLevel(device_index, nPos, nSensitivity):
    # ht_hard_dll.dsoHTSetVTriggerLevel.argtypes = [c_uint16, c_uint16, c_uint16]
    # ht_hard_dll.dsoHTSetVTriggerLevel.restype = c_uint16
    state = ht_hard_dll.dsoHTSetVTriggerLevel(device_index, nPos, nSensitivity)
    if state != 0: print(f'dsoHTSetVTriggerLevel of dv{device_index} succeed')
    else: print(f'fail dsoHTSetVTriggerLevel to dv{device_index}')
    return state

def dsoHTSetTrigerMode(device_index, nTriggerMode, nTriggerSlop, nTriggerCouple):
    # ht_hard_dll.dsoHTSetTrigerMode.argtypes = [c_uint16, c_uint16, c_uint16, c_uint16]
    # ht_hard_dll.dsoHTSetTrigerMode.restype = c_uint16
    state = ht_hard_dll.dsoHTSetTrigerMode(device_index, nTriggerMode, nTriggerSlop, nTriggerCouple)
    if state != 0: print(f'dsoHTSetTrigerMode of dv{device_index} succeed')
    else: print(f'fail dsoHTSetTrigerMode to dv{device_index}')
    return state


# nYTFormat - mode of horizontal format 0-normal, 1-Scan, 2-Roll
def dsoHTSetSampleRate(device_index, nYTFormat, RELAYCONTROL, CONTROL):
    # ht_hard_dll.dsoHTSetSampleRate.argtypes = [c_uint16, c_uint16, POINTER(RelayControl), POINTER(ControlData)]
    # ht_hard_dll.dsoHTSetSampleRate.restype = c_uint16
    state = ht_hard_dll.dsoHTSetSampleRate(device_index, nYTFormat, ctypes.byref(RELAYCONTROL), ctypes.byref(CONTROL))
    if state != 0: print(f'dsoHTSetSampleRate of dv{device_index} succeed')
    else: print(f'fail dsoHTSetSampleRate to dv{device_index}')
    return state

def dsoHTSetAmpCalibrate(device_index, nCHSet, nTimeDIV, nVoltDiv, pCHPOS):
    # ht_hard_dll.dsoHTSetAmpCalibrate.argtypes = [c_uint16, c_uint16, c_uint16, c_uint16, POINTER(c_uint16)]
    # ht_hard_dll.dsoHTSetAmpCalibrate.restype = c_uint
    state = ht_hard_dll.dsoHTSetAmpCalibrate(device_index, nCHSet, nTimeDIV, nVoltDiv, pCHPOS)
    if state != 0: print(f'dsoHTSetAmpCalibrate of dv{device_index} succeed')
    else: print(f'fail dsoHTSetAmpCalibrate to dv{device_index}')
    return state

def dsoHTStartCollectData(device_index, nStartControl):
    # ht_hard_dll.dsoHTStartCollectData.argtypes = [c_uint16, c_uint16]
    # ht_hard_dll.dsoHTStartCollectData.restype = c_uint
    state = ht_hard_dll.dsoHTStartCollectData(device_index, nStartControl)
    if state != 0: 
        pass
        # print(f'dsoHTStartCollectData of dv{device_index} succeed')
    else: print(f'fail dsoHTStartCollectData to dv{device_index}')
    return state


def dsoHTGetState(device_index, print_succcess:bool=False):
    # ht_hard_dll.dsoHTGetState.argtypes = [c_uint16]
    # ht_hard_dll.dsoHTGetState.restype = c_uint
    state = ht_hard_dll.dsoHTGetState(device_index)
    # if state != 0 and print_succcess == True: 
    #     print(f'dsoHTGetState:data collection of dv{device_index} succeed')
    # else: print(f'fail dsoHTGetState of dv{device_index}')
    return state

def dsoHTGetData(device_index, pCH1Data_buffer, pCH2Data_buffer, pCH3Data_buffer, pCH4Data_buffer, CONTROL, print_succcess = False):
    # ht_hard_dll.dsoHTGetData.argtypes = [c_uint16, POINTER(c_uint16), POINTER(c_uint16), POINTER(c_uint16), POINTER(c_uint16), POINTER(ControlData)]
    # ht_hard_dll.dsoHTGetData.restype = c_uint
    state = ht_hard_dll.dsoHTGetData(device_index, pCH1Data_buffer, pCH2Data_buffer, pCH3Data_buffer, pCH4Data_buffer, ctypes.byref(CONTROL))
    if state != 0 and print_succcess == True: 
        print(f'dsoHTGetData get data of dv{device_index} succeed')
    elif state == 0: print(f'FAIL: dsoHTGetData data retrieval ; returned {state}')
    return state


def dsoHTGetRollData(device_index, pCH1Data_buffer, pCH2Data_buffer, pCH3Data_buffer, pCH4Data_buffer, CONTROL, print_success=False):
    # ht_hard_dll.dsoHTGetRollData.argtypes = [c_uint16, POINTER(c_uint16), POINTER(c_uint16), POINTER(c_uint16), POINTER(c_uint16), POINTER(ControlData)]
    # ht_hard_dll.dsoHTGetRollData.restype = c_uint
    state = ht_hard_dll.dsoHTGetRollData(device_index, pCH1Data_buffer, pCH2Data_buffer, pCH3Data_buffer, pCH4Data_buffer, ctypes.byref(CONTROL))
    if state != 0 and print_success == True: 
        print(f'dsoHTGetRollData get data of dv{device_index} succeed')
    # elif state == 0: print(f'FAIL: dsoHTGetRollData data retrieval ; returned {state}')
    return state



# dsoHTSetHTriggerLength
class ControlData(ctypes.Structure):
    _fields_ = [
        ("nCHSet", c_uint16),            # Channel enable/disable
        ("nTimeDIV", c_uint16),          # Time base index
        ("nTriggerSource", c_uint16),    # Trigger source index
        ("nHTriggerPos", c_uint16),      # Horizontal trigger position (0-100)
        ("nVTriggerPos", c_uint16),      # Vertical trigger position
        ("nTriggerSlope", c_uint16),     # Edge trigger slope (0: rise, 1: fall)
        ("nBufferLen", c_uint32),        # Buffer length
        ("nReadDataLen", c_uint32),      # Length of data to be read
        ("nAlreadyReadLen", c_uint32),   # Length of data already read
        ("nALT", c_uint16),              # Alternate trigger (0: off, 1: on)
        ("nETSOpen", c_uint16),      # FPGA version
    ]

# PCONTROLDATA = POINTER(ControlData)

MAX_CH_NUM = 4
class RelayControl(ctypes.Structure):
    _fields_ = [
        ("bCHEnable", c_bool * MAX_CH_NUM),   # Channel Enable/Disable Array
        ("nCHVoltDIV", c_uint16 * MAX_CH_NUM),# Voltage Division Array
        ("nCHCoupling", c_uint16 * MAX_CH_NUM),# Coupling Mode Array (0: DC, 1: AC, 2: GND)
        ("bCHBWLimit", c_bool * MAX_CH_NUM),  # Bandwidth Limit Array (1: ON, 0: OFF)
        ("nTrigSource", c_uint16),            # Trigger Source (0: CH1, 1: CH2, etc.)
        ("bTrigFilt", c_bool),                # High Frequency Rejection Filter (1: ON, 0: OFF)
        ("nALT", c_uint16)                    # Alternate Trigger (1: Alternate, 0: Non-alternate)
    ]


# ht_hard_dll.dsoHTGetRollData.argtypes = [c_uint16]
# ht_hard_dll.dsoHTGetRollData.restype = c_uint
# state = ht_hard_dll_2.dsoOpenDevice(device_index)
# if state != 0: print(f'dsoHTSetAmpCalibrate of dv{device_index} succeed')
# else: print(f'fail dsoHTSetAmpCalibrate to dv{device_index}')


# initilization flow chart:
# dsoSetUSBBus >> dsoInitHard >> dsoHTADCCHModGain >> dsoHTReadCalibrationData >> 
# settings :
# >> dsoHTSetSampleRate >> dsoHTSetCHAndTrigger >> dsoHTSetRamAndTrigerControl >> dsoHTSetCHPos >> dsoHTSetVTriggerLevel >> dsoHTSetTrigerModer

# collection
# dsoHTStartCollectData <- false
# ________
# dsoHTGetState x 2
# ________
# true -> dsoHTGetData
# change setting


control_data = ControlData()
control_data.nCHSet = 0x0F    # disable all four channels (CH1, CH2, CH3, CH4)
# control_data.nCHSet |= (1 << 0)  # Enable CH1
# control_data.nCHSet |= (1 << 2)  # Enable CH3
control_data.nTimeDIV = 16    # Example time base index
control_data.nTriggerSource = 0  # CH1 as the trigger source
control_data.nHTriggerPos = 0   # Horizontal trigger position: 50%
control_data.nVTriggerPos = 255   # Vertical trigger position
control_data.nTriggerSlope = 1   # Rising edge trigger
control_data.nBufferLen = 4096   # Buffer length (4K)
control_data.nReadDataLen = 4096  # Data length to be read (4K)
control_data.nAlreadyReadLen = 4096  # No data has been read yet
control_data.nALT = 1  # Alternate trigger off
control_data.nETSOpen = False


relay_control = RelayControl()
# Enable channels CH1 and CH2, disable CH3 and CH4
relay_control.bCHEnable[0] = 1   # Enable CH1
relay_control.bCHEnable[1] = 1   # Enable CH2
relay_control.bCHEnable[2] = 0  # Disable CH3
relay_control.bCHEnable[3] = 0  # Disable CH4

# Set voltage divisions for each channel
relay_control.nCHVoltDIV[0] = 9
relay_control.nCHVoltDIV[1] = 10
relay_control.nCHVoltDIV[2] = 0
relay_control.nCHVoltDIV[3] = 0

# Set channel coupling (1: DC, 2: AC, 4: GND)
relay_control.nCHCoupling[0] = 2
relay_control.nCHCoupling[1] = 1
relay_control.nCHCoupling[2] = 2
relay_control.nCHCoupling[3] = 2

# Set bandwidth limit (1: ON, 0: OFF)
relay_control.bCHBWLimit[0] = 0
relay_control.bCHBWLimit[1] = 0
relay_control.bCHBWLimit[2] = 0
relay_control.bCHBWLimit[3] = 0




nYTFormat = 0 # mode of horizontal format 0-normal, 1-Scan, 2-Roll
search_device()
connect_device(in_device_index = 0)
dsoInitHard(device_index)
dsoHTADCCHModGain(device_index, nCHMode= 4)
dsoHTSetSampleRate(device_index, nYTFormat= nYTFormat, RELAYCONTROL=relay_control, CONTROL=control_data)
dsoHTSetCHAndTrigger(device_index, RELAYCONTROL= relay_control, nTimeDIV= control_data.nTimeDIV)
dsoHTSetRamAndTrigerControl(device_index, nTimeDiv=control_data.nTimeDIV, nCHset=control_data.nCHSet, nTrigerSource=control_data.nTriggerSource, nPeak=0)

nPos_channels = [128, 128, 0, 0]
for i in range(2):
    print(f'CH{i}')
    dsoHTSetCHPos(device_index, nVoltDIV=11, nPos=nPos_channels[i], nCH=i, nCHMode=relay_control.nCHCoupling[i])
    # dsoHTSetAmpCalibrate(device_index, nCHSet=control_data.nCHSet, nTimeDIV=control_data.nTimeDIV, nVoltDiv=relay_control.nCHVoltDIV[i] , pCHPOS=control_data.nVTriggerPos)
dsoHTSetSampleRate(device_index, nYTFormat= nYTFormat, RELAYCONTROL=relay_control, CONTROL=control_data)

# nPeak???, nCHMode ???, nYTFormat ???5 
# ค่อยว่ากันนันนะคนไทย 
dsoHTSetVTriggerLevel(device_index, nPos=255, nSensitivity=0)
dsoHTSetTrigerMode(device_index, nTriggerMode=0, nTriggerSlop=0, nTriggerCouple=0)



# from interface import leonado
# leonado.rw_string("FIREL000 1")


continuous_data_CH1 : list = []
continuous_data_CH2 : list = []
continuous_data_CH3 : list = []
continuous_data_CH4 : list = []

dsoHTStartCollectData(device_index, nStartControl=2)
while i < 5:
    if dsoHTGetState(device_index) != 0:
        pCH1DATA, pCH2DATA, pCH3DATA, pCH4DATA = (c_ushort * control_data.nBufferLen)(), (c_ushort * control_data.nBufferLen)(), (c_ushort * control_data.nBufferLen)(), (c_ushort * control_data.nBufferLen)()
        # dsoHTGetRollData(device_index, pCH1DATA, pCH2DATA, pCH3DATA, pCH4DATA, control_data)
        
        # ht_hard_dll.dsoHTGetData.argtypes = [c_uint16, POINTER(c_uint16), POINTER(c_uint16), POINTER(c_uint16), POINTER(c_uint16), POINTER(ControlData)]
        # ht_hard_dll.dsoHTGetData.restype = c_int64
        state = ht_hard_dll.dsoHTGetData(device_index, pCH1DATA, pCH2DATA, pCH3DATA, pCH4DATA, ctypes.byref(control_data))
        
        continuous_data_CH1.extend(list(pCH1DATA))
        continuous_data_CH2.extend(list(pCH2DATA))
        i += 1
    

 


print("SHOWING COMPLETED DATA")

fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(8, 6), sharex=True)
axes[0].plot(continuous_data_CH1)
# axes[0].set_ylim(0, 350)
axes[0].legend(['CH1: ultrasonic data'])

axes[1].plot(continuous_data_CH2)
# axes[1].set_ylim(0, 350)
axes[1].legend(['CH2: Laser Firing'])

axes[2].plot(continuous_data_CH1[0: control_data.nBufferLen])
axes[2].set_ylim(0, 350)
axes[2].legend(['osciloscope output data'])

plt.show()

# nStartControl 0:1 AUTO trigger, 1:1 Roll Mode, 2:1 stop after this collect 


from scipy.io import savemat, loadmat
import numpy as np
import json


datajson_save_dir = os.path.join(os.getcwd(), 'device_interface', 'data.json')

with open(datajson_save_dir, 'r') as f:
    data_json_loaded = json.load(f)
with open(datajson_save_dir, 'w') as f:
    data_json_loaded['ultrasound'].append(list(continuous_data_CH1))
    data_json_loaded['sig'].append(list(continuous_data_CH2))
    json.dump(data_json_loaded, f, indent=4)
    