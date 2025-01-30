import ctypes
from ctypes import c_short, POINTER, c_uint, c_uint16, c_uint32, c_bool, c_int64, c_ushort, c_int
import os
import matplotlib.pyplot as plt
import numpy as np

dll_x64_path = os.path.join(os.getcwd(), 'device_interface', 'HT6004BX_SDK', 'DLL', 'x64')
ht_hard_dll = ctypes.WinDLL(os.path.join(dll_x64_path, 'HTHardDll.dll'))

# dll_x64_path = os.path.join(os.getcwd(), 'device_interface', 'HT6022_SDK', 'Hantek6022BE')
# ht_hard_dll_2 = ctypes.WinDLL(os.path.join(dll_x64_path, 'HTMarch.dll'))

m_nDeviceIndex = 0

m_bStartC: bool = True
# General Definitions
MAX_TIMEDIV_NUM = 36  # Total time division levels
TIMEDIV_OFFSET = 2  # Time base offset

DRIVERVERLEN = 8  # Must be even
AUTOSET_TIME1 = 19
AUTOSET_TIME2 = 18
ZERO_START_VOLT = 5
BUF_10K_LIMIT = None  # Undefined

PI = 3.14159265358979323846

BUF_4K_LEN = 0x1000
BUF_3K_LEN = 0x0C00  # 3072
BUF_8K_LEN = 0x2000
BUF_16K_LEN = 0x4000
BUF_32K_LEN = 0x8000
BUF_64K_LEN = 0x10000

BUF_INSERT_LEN = None  # BUF_72K_LEN is undefined

DEF_READ_DATA_LEN = BUF_4K_LEN  # Default data read length
DEF_DRAW_DATA_LEN = 2500  # Default data draw length

MAX_INSERT_TIMEDIV = 6  # 200nS maximum interpolation for time division
MAX_DOUBLE_TIMEDIV = MAX_INSERT_TIMEDIV
MAX_SF_T_TIMEDIV = MAX_INSERT_TIMEDIV - 2  # Requires software-triggered time division
MAX_SINE_TIMEDIV = 3  # Must use sine interpolation

MIN_SCAN_TIMEDIV = 25  # Minimum time division for scan mode
MIN_ROLL_TIMEDIV = 27  # Minimum time division for roll mode

SINE_WAVE_LEN = 128  # Length of sine wave in the center window
MAX_ETS_TIMEDIV = 3  # ETS maximum time division (0, 1, 2, 3)
ETS_SAMPLING_100M = 0  # ETS 100M sampling

# Calibration
NEW_CAL_LEVEL_LEN = 400  # Calibration level length

# Vertical Settings
CH1 = 0
CH2 = 1
CH3 = 2
CH4 = 3

MAX_CH_NUM = 4
HORIZONTAL = MAX_CH_NUM  # Horizontal lever
MATH = MAX_CH_NUM  # Vertical lever (CH1/CH2/CH3/CH4/MATH/REF)
REF = MAX_CH_NUM + 1
ALL_CH = MAX_CH_NUM + 2
MIN_DATA = 0
MAX_DATA = 255
MID_DATA = 128
MAX_VOLTDIV_NUM = 12

# Display Modes
YT = 0
XY = 1
YT_NORMAL = 0
YT_SCAN = 1
YT_ROLL = 2

# Coupling Modes
DC = 0
AC = 1
GND = 2

# Trigger
MAX_TRIGGER_SOURCE_NUM = MAX_CH_NUM + 2  # CH1/CH2/CH3/CH4/EXT/(EXT/10)
MAX_ALT_TRIGGER_NUM = MAX_CH_NUM + 2  # CH1/CH2/CH3/CH4
EXT = MAX_CH_NUM
EXT10 = MAX_CH_NUM + 1

# Trigger Types
EDGE = 0
PULSE = 1
VIDEO = 2
CAN = 3
LIN = 4
UART = 5
SPI = 6
IIC = 7

FORCE = 0x80

# Trigger Modes
AUTO = 0
NORMAL = 1
SINGLE = 2

# Edge Types
RISE = 0
FALL = 1
volt_indicies = {3: ("20 mV/Div", 20e-3), 4: ("50 mV/Div", 50e-3), 5: ("100 mV/Div", 0.1),
                              6: ("200 mV/Div", 0.2),
                              7: ("500 mV/Div", 0.5), 8: ("1 V/Div", 1.0), 9: ("2 V/Div", 2.0), 10: ("5 V/Div", 5.0)}
 

class ControlData(ctypes.Structure):
    _fields_ = [
        ("nCHSet", c_short),            # Channel enable/disable
        ("nTimeDIV", c_short),          # Time base index
        ("nTriggerSource", c_short),    # Trigger source index
        ("nHTriggerPos", c_short),      # Horizontal trigger position (0-100)
        ("nVTriggerPos", c_short),      # Vertical trigger position
        ("nTriggerSlope", c_short),     # Edge trigger slope (0: rise, 1: fall)
        ("nBufferLen", c_int),          # Buffer length
        ("nReadDataLen", c_int),        # Length of data to be read
        ("nAlreadyReadLen", c_int),     # Length of data already read
        ("nALT", c_short),              # Alternate trigger (0: off, 1: on)
        ("nETSOpen", c_short),          # FPGA version
        ("nDriverCode", c_short),       # Driver code
        ("nLastAddress", c_int),        # Last address
        ("nFPGAVersion", c_short)       # FPGA version
    ]

class RELAYCONTROL(ctypes.Structure):
    _fields_ = [
        ("bCHEnable", c_bool * MAX_CH_NUM),   # Channel Enable/Disable Array
        ("nCHVoltDIV", c_short * MAX_CH_NUM),# Voltage Division Array
        ("nCHCoupling", c_short * MAX_CH_NUM),# Coupling Mode Array (0: DC, 1: AC, 2: GND)
        ("bCHBWLimit", c_int * MAX_CH_NUM),  # Bandwidth Limit Array (1: ON, 0: OFF)
        ("nTrigSource", c_short),            # Trigger Source (0: CH1, 1: CH2, etc.)
        ("bTrigFilt", c_int),                # High Frequency Rejection Filter (1: ON, 0: OFF)
        ("nALT", c_short)                    # Alternate Trigger (1: Alternate, 0: Non-alternate)
    ]
    




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
def dsoHTDeviceConnect(in_device_index: int = 0):
    device_index = in_device_index
    # ht_hard_dll.dsoHTDeviceConnect.argtypes = [c_uint]
    # ht_hard_dll.dsoHTDeviceConnect.restype = c_uint
    rr_con = ht_hard_dll.dsoHTDeviceConnect(device_index)
    if rr_con: print(f'dv{device_index} Connected successfully!')
    else: 
        print('FAIL: dsoHTDeviceConnect')
        exit()
    return rr_con
        
        

def dsoInitHard(device_index):
    ht_hard_dll.dsoInitHard.argtypes = [c_ushort]
    ht_hard_dll.dsoInitHard.restype = c_uint
    state = ht_hard_dll.dsoInitHard(device_index)
    if state != 0: print(f'dsoInitHard of dv{device_index} succeed')
    else: print(f'fail dsoInitHard to dv{device_index}')
    return state

def dsoHTADCCHModGain(device_index, nCHMode):
    ht_hard_dll.dsoHTADCCHModGain.argtypes = [c_ushort, c_int]
    ht_hard_dll.dsoHTADCCHModGain.restype = c_uint
    state = ht_hard_dll.dsoHTADCCHModGain(device_index, nCHMode)
    if state != 0: print(f'dsoHTADCCHModGain of dv{device_index} succeed')
    else: print(f'fail dsoHTADCCHModGain to dv{device_index}')
    return state

# nYTFormat - mode of horizontal format 0-normal, 1-Scan, 2-Roll
def dsoHTSetSampleRate(device_index, nYTFormat, relay_con, CONTROL):
    ht_hard_dll.dsoHTSetSampleRate.argtypes = [c_ushort, c_ushort, POINTER(RELAYCONTROL), POINTER(ControlData)]
    ht_hard_dll.dsoHTSetSampleRate.restype = c_uint16
    state = ht_hard_dll.dsoHTSetSampleRate(device_index, nYTFormat, ctypes.byref(relay_con), ctypes.byref(CONTROL))
    if state != 0: print(f'dsoHTSetSampleRate of dv{device_index} succeed')
    else: print(f'fail dsoHTSetSampleRate to dv{device_index}')
    return state

def dsoHTSetCHAndTrigger(device_index, relay_con, nTimeDIV):
    ht_hard_dll.dsoHTSetCHAndTrigger.argtypes = [c_ushort, POINTER(RELAYCONTROL), c_ushort]
    ht_hard_dll.dsoHTSetCHAndTrigger.restype = c_uint16
    state = ht_hard_dll.dsoHTSetCHAndTrigger(device_index, ctypes.byref(relay_con), nTimeDIV)
    if state != 0: print(f'dsoHTSetCHAndTrigger of dv{device_index} succeed')
    else: print(f'fail dsoHTSetCHAndTrigger to dv{device_index}')
    return state

def dsoHTSetRamAndTrigerControl(device_index, nTimeDiv, nCHset, nTrigerSource, nPeak):
    ht_hard_dll.dsoHTSetRamAndTrigerControl.argtypes = [c_ushort, c_short, c_short, c_short, c_int]
    ht_hard_dll.dsoHTSetRamAndTrigerControl.restype = c_uint16
    state = ht_hard_dll.dsoHTSetRamAndTrigerControl(device_index, nTimeDiv, nCHset, nTrigerSource, nPeak)
    if state != 0: print(f'dsoHTSetRamAndTrigerControl of dv{device_index} succeed')
    else: print(f'fail dsoHTSetRamAndTrigerControl to dv{device_index}')
    return state

def dsoHTSetCHPos(device_index, nVoltDIV, nPos, nCH, nCHMode):
    print(device_index, nVoltDIV, nPos, nCH, nCHMode)
    ht_hard_dll.dsoHTSetCHPos.argtypes = [c_ushort, c_short, c_short, c_short, c_int]
    ht_hard_dll.dsoHTSetCHPos.restype = c_uint16
    state = ht_hard_dll.dsoHTSetCHPos(device_index, nVoltDIV, nPos, nCH, nCHMode)
    if state != 0: print(f'dsoHTSetCHPos of dv{device_index} succeed')
    else: print(f'fail dsoHTSetCHPos to dv{device_index}')
    return state

def dsoHTSetVTriggerLevel(device_index, nPos, nSensitivity):
    ht_hard_dll.dsoHTSetVTriggerLevel.argtypes = [c_ushort, c_short, c_int]
    ht_hard_dll.dsoHTSetVTriggerLevel.restype = c_uint16
    state = ht_hard_dll.dsoHTSetVTriggerLevel(device_index, nPos, nSensitivity)
    if state != 0: print(f'dsoHTSetVTriggerLevel of dv{device_index} succeed')
    else: print(f'fail dsoHTSetVTriggerLevel to dv{device_index}')
    return state

def dsoHTSetTrigerMode(device_index, nTriggerMode, nTriggerSlop, nTriggerCouple):
    ht_hard_dll.dsoHTSetTrigerMode.argtypes = [c_ushort, c_ushort, c_short, c_int]
    ht_hard_dll.dsoHTSetTrigerMode.restype = c_uint16
    state = ht_hard_dll.dsoHTSetTrigerMode(device_index, nTriggerMode, nTriggerSlop, nTriggerCouple)
    if state != 0: print(f'dsoHTSetTrigerMode of dv{device_index} succeed')
    else: print(f'fail dsoHTSetTrigerMode to dv{device_index}')
    return state

def dsoHTSetCHAndTriggerVB(device_index, pCHEnable, pCHVoltDIV, pCHCoupling, pCHBWLimit, nTriggerSource, nTriggerFilt, nALT, nTimeDIV):
    ht_hard_dll.dsoHTSetCHAndTriggerVB.argtypes = [POINTER(RELAYCONTROL.bCHEnable), c_ushort, c_short, c_int]
    ht_hard_dll.dsoHTSetCHAndTriggerVB.restype = c_uint16
    state = ht_hard_dll.dsoHTSetCHAndTriggerVB(device_index, pCHEnable, pCHVoltDIV, pCHCoupling, pCHBWLimit, nTriggerSource, nTriggerFilt, nALT, nTimeDIV)
    
    if state == 1: print(f'dsoHTSetTrigerMode of dv{device_index} succeed')
    else: print(f'fail dsoHTSetTrigerMode to dv{device_index}')
    return state


@staticmethod
def convert_read_data(input_data, scale, scale_points=32.0):
    """
        Helper function for converting the data taken from the scope into its true analog representation.
        Takes input from scope data, and the scaling factor, with the optional number of points in the
        scaling division. Returns an array of analog values read from the scope.
    """
    point_div = scale / scale_points
    out = [0.0 for _ in input_data]
    input_data = [j for j in input_data]
    for j in range(0, len(input_data)):
        out[j] = input_data[j] * point_div
    return input_data


def dsoHTSetAmpCalibrate(device_index, nCHSet, nTimeDIV, nVoltDiv, pCHPOS):
    # ht_hard_dll.dsoHTSetAmpCalibrate.argtypes = [c_uint16, c_uint16, c_uint16, c_uint16, POINTER(c_uint16)]
    # ht_hard_dll.dsoHTSetAmpCalibrate.restype = c_uint
    state = ht_hard_dll.dsoHTSetAmpCalibrate(device_index, nCHSet, nTimeDIV, nVoltDiv, pCHPOS)
    if state != 0: print(f'dsoHTSetAmpCalibrate of dv{device_index} succeed')
    else: print(f'fail dsoHTSetAmpCalibrate to dv{device_index}')
    return state

def dsoHTStartCollectData(device_index, nStartControl):
    ht_hard_dll.dsoHTStartCollectData.argtypes = [c_ushort, c_short]
    ht_hard_dll.dsoHTStartCollectData.restype = c_uint
    state = ht_hard_dll.dsoHTStartCollectData(device_index, nStartControl)
    if state == 1: 
        print(f'dsoHTStartCollectData of dv{device_index} succeed')
    else: print(f'fail dsoHTStartCollectData to dv{device_index}')
    return state


def dsoHTGetState(device_index, print_succcess:bool=False):
    ht_hard_dll.dsoHTGetState.argtypes = [c_ushort]
    ht_hard_dll.dsoHTGetState.restype = c_ushort
    state = ht_hard_dll.dsoHTGetState(device_index)
    
    is_triggered = bool(state & 0x01)
    is_data_finished = bool(state & 0x02)
    return is_triggered, is_data_finished

def dsoHTGetData(device_index, pCH1Data_buffer, pCH2Data_buffer, pCH3Data_buffer, pCH4Data_buffer, CONTROL, print_succcess = False):
    ht_hard_dll.dsoHTGetData.argtypes = [c_ushort, POINTER(c_ushort), POINTER(c_ushort), POINTER(c_ushort), POINTER(c_ushort), POINTER(ControlData)]
    ht_hard_dll.dsoHTGetData.restype = c_int64
    state = ht_hard_dll.dsoHTGetData(device_index, pCH1Data_buffer, pCH2Data_buffer, pCH3Data_buffer, pCH4Data_buffer, ctypes.byref(CONTROL))
    if state != 0 and print_succcess == True: 
        print(f'dsoHTGetData get data of dv{device_index} succeed')
    elif state == 0: print(f'FAIL: dsoHTGetData data retrieval ; returned {state}')
    return state

def scale_data(raw_data, volt_div):
    return (raw_data - 128) * (volt_div / 25.5)


# def dsoHTGetRollData(device_index, pCH1Data_buffer, pCH2Data_buffer, pCH3Data_buffer, pCH4Data_buffer, CONTROL, print_success=False):
#     # ht_hard_dll.dsoHTGetRollData.argtypes = [c_uint16, POINTER(c_int64), POINTER(c_int64), POINTER(c_int64), POINTER(c_uint16), POINTER(ControlData)]
#     # ht_hard_dll.dsoHTGetRollData.restype = c_uint16
#     state = ht_hard_dll.dsoHTGetRollData(device_index, pCH1Data_buffer, pCH2Data_buffer, pCH3Data_buffer, pCH4Data_buffer, ctypes.byref(CONTROL))
#     if state != 0 and print_success == True: 
#         print(f'dsoHTGetRollData get data of dv{device_index} succeed')
#     # elif state == 0: print(f'FAIL: dsoHTGetRollData data retrieval ; returned {state}')
#     return state



m_stControl = ControlData()
RelayControl = RELAYCONTROL()
# def Hard():
m_nTimeDIV = 17
m_nYTFormat = YT_NORMAL

m_stControl.nCHSet = 0x0F
m_stControl.nTimeDIV = m_nTimeDIV
m_stControl.nTriggerSource = CH3
m_stControl.nHTriggerPos = 50
m_stControl.nVTriggerPos = 100
m_stControl.nBufferLen = BUF_8K_LEN
m_stControl.nReadDataLen = BUF_8K_LEN
m_stControl.nAlreadyReadLen = BUF_8K_LEN
m_stControl.nALT = 0
m_stControl.nFPGAVersion = 0xa000



bCHEnable = [1, 1, 1, 1]
nCHVoltDIV = [9, 9, 9, 9]
nCHCoupling = [AC, AC, AC, AC]
bCHBWLimit = [0, 0, 0, 0]

for i in range(MAX_CH_NUM):
    RelayControl.bCHEnable[i] = bCHEnable[i]
    RelayControl.nCHVoltDIV[i] = nCHVoltDIV[i]
    RelayControl.nCHCoupling[i] = nCHCoupling[i]
    RelayControl.bCHBWLimit[i] = bCHBWLimit[i]
RelayControl.nTrigSource = CH1 
RelayControl.bTrigFilt = 0
RelayControl.nALT = 0
m_nTriggerMode = EDGE
m_nTriggerSLope = RISE
m_nTriggerSweep = AUTO
m_nLeverPos = [None, None, None, None]
m_nLeverPos[CH1] = 128
m_nLeverPos[CH2] = 128
m_nLeverPos[CH3] = 128
m_nLeverPos[CH4] = 128

m_bCollect = True
m_nReadOK = 0
    


for _field_name, _field_type in m_stControl._fields_:
    value = getattr(m_stControl, _field_name)
    print(f'm_stControl {_field_name} {value}')
for _field_name, _field_type in RelayControl._fields_:
    value = getattr(RelayControl, _field_name)
    print(f'm_stControl {_field_name} {value}')

def Init():
    dsoInitHard(device_index= m_nDeviceIndex)
    dsoHTADCCHModGain(device_index= m_nDeviceIndex, nCHMode = 4)
    
    dsoHTSetSampleRate(device_index = m_nDeviceIndex, nYTFormat= m_nYTFormat, relay_con=RelayControl, CONTROL=m_stControl)
    dsoHTSetCHAndTrigger(device_index = m_nDeviceIndex, relay_con=RelayControl, nTimeDIV=m_stControl.nTimeDIV)
    dsoHTSetRamAndTrigerControl(device_index = m_nDeviceIndex, nTimeDiv=m_stControl.nTimeDIV, nCHset=m_stControl.nCHSet, nTrigerSource=m_stControl.nTriggerSource, nPeak= 0 )
    
    for i in range(MAX_CH_NUM):
        dsoHTSetCHPos(device_index = m_nDeviceIndex, nVoltDIV= RelayControl.nCHVoltDIV[i], nPos= m_nLeverPos[i], nCH=i, nCHMode= 4)
    dsoHTSetVTriggerLevel(device_index = m_nDeviceIndex, nPos= m_nLeverPos[CH1], nSensitivity = 4)
    
# def startAStatus():
#     global m_bStartC
#     if m_bStartC:
#         dsoHTStartCollectData(device_index = m_nDeviceIndex, nStartControl= 1)
#         m_bStartC = False
#         return 0
#     return dsoHTGetState(device_index = m_nDeviceIndex)

    
def ReadData():
    pReadData = []
    pReadData = (c_ushort * MAX_CH_NUM)()
    for i in range(MAX_CH_NUM):
        # pReadData[i] = (c_ushort * m_stControl.nBufferLen)()
        pReadData.append((c_ushort * m_stControl.nBufferLen)())
    dsoHTGetData(device_index = m_nDeviceIndex, pCH1Data_buffer= pReadData[CH1], pCH2Data_buffer=pReadData[CH2], pCH3Data_buffer=pReadData[CH3], pCH4Data_buffer=pReadData[CH4], CONTROL = m_stControl)
    return pReadData


read_data = None

dsoHTDeviceConnect(m_nDeviceIndex)
Init()
if m_bStartC:
    dsoHTStartCollectData(device_index= m_nDeviceIndex, nStartControl = 1)
    m_bStartC = False
    
    is_triggered, is_data_finished = dsoHTGetState(device_index= m_nDeviceIndex)
    print(f'bef state {is_triggered, is_data_finished}')
    
i = 0
continuous_data = [[],[],[],[]]

plt.ion()
fig, ax = plt.subplots(nrows=4, ncols=1)
plt.show()

volts_per_div = 1e-0  # 100mV per division
time_per_div = 1e-3  # 5 microseconds per division
adc_offset = 128  # Midpoint for signed conversion (assuming 8-bit unsigned)
adc_scale = volts_per_div / 128  # Approximate scale factor


while True:
    is_triggered, is_data_finished = dsoHTGetState(device_index= m_nDeviceIndex)
    
    if is_triggered: print(f'bef state {is_triggered, is_data_finished}')
    while (dsoHTGetState(device_index= m_nDeviceIndex) != 0x02):
        read_data = np.array(ReadData())
        for i in range(len(read_data)):
            # scaled_data = convert_read_data(read_data[i], 2.0)
            # scaled_data = scale_data(read_data[i], RelayControl.nCHVoltDIV[i])
            adc_values_uint8 = read_data[i]
            voltages = (adc_values_uint8 - adc_offset) * adc_scale
            
            ax[i].cla()  # Clear the previous plot
            ax[i].plot(voltages)  # Plot the scaled data
            ax[i].set_title(f"Channel {i+1}")
        dsoHTStartCollectData(device_index= m_nDeviceIndex, nStartControl = 1)
        
        plt.pause(1e-10)
        
        print('reading data')
        
    
    # if is_triggered and is_data_finished:
    #     print(f'bef state {is_triggered, is_data_finished}')
    #     read_data = np.array(ReadData())
    #     break
    #     # for num, yCH_data in enumerate(read_data):
    #     #     continuous_data[num].extend(yCH_data)
    
print(read_data.shape)
plt.plot(read_data[0]) # plot CH1
plt.show()




# convertion
adc_values_uint8 = np.frombuffer(binary_data, dtype=np.uint8)


# Convert ADC values to voltage
voltages = (adc_values_uint8 - adc_offset) * adc_scale

plt.plot(voltages)
plt.show()

# Generate time values based on the oscilloscope sampling interval
num_samples = len(voltages)
time_values = np.linspace(0, num_samples * time_per_div, num_samples)

# Create a DataFrame for easy saving and analysis
df = pd.DataFrame({"Time (s)": time_values, "Voltage (V)": voltages})

# Save to CSV file
df.to_csv(csv_output_path, index=False)

# Plot the extracted waveform (first 1000 samples for visualization)
plt.figure(figsize=(10, 4))
plt.plot(time_values[:1000], voltages[:1000], label="Extracted Waveform")
plt.title("Extracted Waveform from Hantek 6254BE")
plt.xlabel("Time (s)")
plt.ylabel("Voltage (V)")
plt.grid()
plt.legend()
plt.show()

# Output file path
print(f"Waveform data saved to: {csv_output_path}")