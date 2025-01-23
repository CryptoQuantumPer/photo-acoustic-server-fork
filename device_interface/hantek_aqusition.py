import ctypes
from ctypes import c_short, POINTER, c_uint, c_uint16, c_uint32, c_bool
import os, time
import platform

dll_x64_path = os.path.join(os.getcwd(), 'device_interface', 'HT6004BX_SDK', 'DLL', 'x64')
ht_hard_dll = ctypes.WinDLL(os.path.join(dll_x64_path, 'HTHardDll.dll'))

device_index = 0

def search_device(return_buffer_size = 32):
    ht_hard_dll.dsoHTSearchDevice.argtypes = [POINTER(c_short)]
    ht_hard_dll.dsoHTSearchDevice.restype = c_uint
    device_info = (c_short * return_buffer_size)()
    result = ht_hard_dll.dsoHTSearchDevice(device_info)
    if result:
        print(f'Founded {result} device(s):')
    return device_info

# dsoHTDeviceConnect
def connect_device(device_index: int = 0):
    ht_hard_dll.dsoHTDeviceConnect.argtypes = [c_uint]
    ht_hard_dll.dsoHTDeviceConnect.restype = c_uint
    rr_con = ht_hard_dll.dsoHTDeviceConnect(device_index)
    if rr_con: print(f'dv{device_index} Connected successfully!')
    else: 
        print('FAIL: dsoHTDeviceConnect')
        exit()


search_device()
connect_device(device_index)

# Remaks from documentation: should run after connect_device
ht_hard_dll.dsoInitHard.argtypes = [c_uint]
ht_hard_dll.dsoInitHard.restype = c_uint
rt_value = ht_hard_dll.dsoInitHard(device_index)
if rt_value != 0: print(f'dsoInitHard of dv{device_index} succeed')
else : print(f'fail dsoInitHard to dv{device_index}')

# Getting the FPGA version
ht_hard_dll.dsoGetFPGAVersion.argtypes = [c_uint16]
ht_hard_dll.dsoGetFPGAVersion.restype = c_uint16
FPGA_ver = ht_hard_dll.dsoGetFPGAVersion(device_index)
print(f'dv{device_index} FPGA version: {FPGA_ver}')

# Setting Channel level
# // see dsoHTReadCalibrationData
nVoltDIV = 6 # the setting of 1V/div is the index 6
nPos = 128 # position range from 0-255. 128 for middle
nCH = 0 # 0 for CH1, 1 for CH2, 2 for CH3, 3 for CH4
nCHMod = 4 #Channel working mode (1,2,4)
ht_hard_dll.dsoHTSetCHPos.argtypes = [c_uint, c_uint, c_uint, c_uint, c_uint]
ht_hard_dll.dsoHTSetCHPos.restype = c_uint
dsoHTSetCHPos_return = ht_hard_dll.dsoHTSetCHPos(device_index, nVoltDIV, nPos, nCH, nCHMod)
if dsoHTSetCHPos_return != 0: print(f'set channel level of dv{device_index} succeeed')
else: print('FAIL TO SET CHANNEL LEVEL: dsoHTSetCHPos')


# set trigger level: dsoHTSetVTriggerLevel
nPos = 128
nSensitivity = 1 # value range from 1-10. "1" for the highest sensitivity
ht_hard_dll.dsoHTSetVTriggerLevel.argtypes = [c_uint, c_uint, c_uint]
ht_hard_dll.dsoHTSetVTriggerLevel.restype = c_uint
dsoHTSetVTriggerLevel_return = ht_hard_dll.dsoHTSetVTriggerLevel(device_index, nPos, nSensitivity)
if dsoHTSetVTriggerLevel_return != 0: print(f'set trigger level of dv{device_index} succeed')
else: print('FAIL: dsoHTSetVTriggerLevel')


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
        ("nFPGAVersion", c_uint16),      # FPGA version
    ]

# Create an instance of ControlData and populate it based on your C++ example
control_data = ControlData()
control_data.nCHSet = 0x0F  # Enable all four channels (CH1, CH2, CH3, CH4)
control_data.nTimeDIV = 7   # Example time base index
control_data.nTriggerSource = 0  # CH1 as the trigger source
control_data.nHTriggerPos = 50   # Horizontal trigger position: 50%
control_data.nVTriggerPos = 64   # Vertical trigger position
control_data.nTriggerSlope = 0   # Rising edge trigger
control_data.nBufferLen = 4096   # Buffer length (4K)
control_data.nReadDataLen = 4096  # Data length to be read (4K)
control_data.nAlreadyReadLen = 4096  # No data has been read yet
control_data.nALT = 0  # Alternate trigger off
control_data.nFPGAVersion = 0xA000  # Example FPGA version (from your C++ code)

PCONTROLDATA = POINTER(ControlData)

nCHMod = 1 # Channel mode (1,2,4)
dsoHTSetHTriggerLength_return = ht_hard_dll.dsoHTSetHTriggerLength(device_index, ctypes.byref(control_data), nCHMod)
if dsoHTSetHTriggerLength_return != 0: print(f'dsoHTSetHTriggerLength of dv{device_index} succeed')
else: print('FAIL: dsoHTSetHTriggerLength')



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

relay_control = RelayControl()

# // Configure each field:
# Enable channels CH1 and CH2, disable CH3 and CH4
relay_control.bCHEnable[0] = True   # Enable CH1
relay_control.bCHEnable[1] = True   # Enable CH2
relay_control.bCHEnable[2] = False  # Disable CH3
relay_control.bCHEnable[3] = False  # Disable CH4

# Set voltage divisions for each channel
relay_control.nCHVoltDIV[0] = 8
relay_control.nCHVoltDIV[1] = 8
relay_control.nCHVoltDIV[2] = 8
relay_control.nCHVoltDIV[3] = 8

# Set channel coupling (0: DC, 1: AC, 2: GND)
relay_control.nCHCoupling[0] = 1
relay_control.nCHCoupling[1] = 1
relay_control.nCHCoupling[2] = 1
relay_control.nCHCoupling[3] = 1

# Set bandwidth limit (1: ON, 0: OFF)
relay_control.bCHBWLimit[0] = False
relay_control.bCHBWLimit[1] = False
relay_control.bCHBWLimit[2] = False
relay_control.bCHBWLimit[3] = False

relay_control.nTrigSource = 0  # Trigger on CH1 # Set the trigger source to CH1
relay_control.bTrigFilt = True  # Enable high frequency rejection filter - high frequency rejection filter (1: ON, 0: OFF)
relay_control.nALT = 0  # No alternate triggering Set alternate trigger (1: alternate, 0: non-alternate)


ht_hard_dll.dsoHTSetCHAndTrigger.argtypes = [c_uint16, POINTER(RelayControl), c_uint16]
ht_hard_dll.dsoHTSetCHAndTrigger.restype = c_uint16
nTimeDIV = 19 
dsoHTSetCHAndTrigger_return = ht_hard_dll.dsoHTSetCHAndTrigger(device_index, ctypes.byref(relay_control), nTimeDIV)
if dsoHTSetCHAndTrigger_return != 0: print(f'dsoHTSetCHAndTrigger Relay control of dv{device_index} succeed')
else: print('FAIL: dsoHTSetCHAndTrigger')



# dsoHTSetSampleRate
ht_hard_dll.dsoHTSetSampleRate.argtypes = [c_uint16, c_uint16, POINTER(RelayControl), PCONTROLDATA]
ht_hard_dll.dsoHTSetSampleRate.restype = c_uint16
nYTFormat = 7 # Horizontal format. 0: Normal, 1: Scan-scan for signal, 2:Roll.
dsoHTSetSampleRate_return = ht_hard_dll.dsoHTSetSampleRate(device_index, nYTFormat, ctypes.byref(relay_control), ctypes.byref(control_data))
if dsoHTSetSampleRate_return != 0: print(f'dsoHTSetSampleRate Relay control of dv{device_index} succeed')
else: print('FAIL: dsoHTSetSampleRate')

# dsoHTStartCollectData
ht_hard_dll.dsoHTStartCollectData.argtypes = [c_uint, c_uint16]
ht_hard_dll.dsoHTStartCollectData.restype = c_uint 
nStartContorl = 0b000 #0b000, 0b001, 0b010, 0b011, 0b101 correspond to the number 0,1,2,3,4,5 ; AUTO Triger, ROLL, Stop After Collection, AUTO Trigger + Stop After Collection, ROLL Mode + Stop After Collection
dsoHTStartCollectData_return = ht_hard_dll.dsoHTStartCollectData(device_index, nStartContorl) 
if dsoHTStartCollectData_return != 0: print(f'dsoHTStartCollectData Relay control of dv{device_index} succeed')
else: print('FAIL: dsoHTStartCollectData')


# dsoHTGetState
# Get state of collection; function returns 2 bits; bit 0 if collection triggers 0 bit is 1; bit 1 turns into 1 when finish collection 
ht_hard_dll.dsoHTGetState.argtypes = [c_uint16]
ht_hard_dll.dsoHTGetState.restype = c_uint
dsoHTGetState_return = ht_hard_dll.dsoHTGetState(device_index)
binary_representation_16bit = format(dsoHTGetState_return, '08b')

triggered_state = dsoHTGetState_return & 0b1
state_of_collection = (dsoHTGetState_return >> 1) & 0b1
if binary_representation_16bit[0] == '1': print(f'data collection of dv{device_index} triggered')
else: print(f'Caution : dsoHTGetState of dv{device_index} has not been triggered, {binary_representation_16bit} state')
if binary_representation_16bit[1] == '1': print(f'data collection of dv{device_index} is finished ')
else: print(f'Caution : dsoHTGetState of dv{device_index} is not done!! please be patient {binary_representation_16bit} state')


# dsoHTGetData
control_data.nReadDataLen = 4096
ht_hard_dll.dsoHTGetRollData.argtypes = [c_uint16, POINTER(c_uint16), POINTER(c_uint16), POINTER(c_uint16), POINTER(c_uint16), POINTER(ControlData)]
ht_hard_dll.dsoHTGetRollData.restype = c_uint
pCH1DATA, pCH2DATA, pCH3DATA, pCH4DATA = (c_uint16 * 4096)(), (c_uint16 * 4096)(), (c_uint16 * 4096)(), (c_uint16 * 4096)()
dsoHTGetRollData_return = ht_hard_dll.dsoHTGetRollData(device_index, pCH1DATA, pCH2DATA, pCH3DATA, pCH4DATA, ctypes.byref(control_data))
if dsoHTGetRollData_return != 0: print(f'dsoHTGetRollData get data of dv{device_index} succeed')
else: print(f'FAIL: dsoHTGetRollData data retrieval ; returned {dsoHTGetRollData_return}')
# print(f'print whether the returned data is the same for CH1 : {bool(list(pCH1DATA) == list((c_uint16 * 4096)))}')





import matplotlib.pyplot as plt
return_data = [pCH1DATA, pCH2DATA, pCH3DATA, pCH4DATA]

plt.plot(return_data[0])
plt.show()

# for i in range(len(return_data)):
#     plt.plot(list(return_data)[i])
#     plt.show()

# while True:
#     dsoHTGetRollData_return = ht_hard_dll.dsoHTGetRollData(device_index, pCH1DATA, pCH2DATA, pCH3DATA, pCH4DATA, ctypes.byref(control_data))
    
#     if dsoHTGetRollData_return != 0:
#         print(f'Roll mode data retrieved successfully for device {device_index}.')
#         plt.plot(list(pCH2DATA))
#         plt.show()
#         time.sleep(1)  # Adjust the sleep time as needed
#     else:
#         print(f'Failed to retrieve roll mode data for device {device_index}.')
#         break



# print(list(pCH1DATA))