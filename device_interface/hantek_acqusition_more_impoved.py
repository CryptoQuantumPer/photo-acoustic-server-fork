import os, time, sys, json
from ctypes import c_short, POINTER, c_uint, c_uint16, byref , _SimpleCData, Structure,c_bool, c_ushort, c_int, c_int8, c_int16, c_int32
if sys.platform == "win32":
    from ctypes import WinDLL
else: WinDLL = None
import matplotlib.pyplot as plt
import numpy as np
from interface import leonado



base_filepath = os.path.join(os.getcwd(), 'device_interface')
dll_x64_path = os.path.join(base_filepath, 'HT6004BX_SDK', 'DLL', 'x64')


MAX_CH_NUM = 4

class ControlData(Structure):
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

class RELAYCONTROL(Structure):
    _fields_ = [
        ("bCHEnable", c_short * MAX_CH_NUM),   # Channel Enable/Disable Array
        ("nCHVoltDIV", c_ushort * MAX_CH_NUM),# Voltage Division Array
        ("nCHCoupling", c_short * MAX_CH_NUM),# Coupling Mode Array (0: DC, 1: AC, 2: GND)
        ("bCHBWLimit", c_int * MAX_CH_NUM),  # Bandwidth Limit Array (1: ON, 0: OFF)
        ("nTrigSource", c_short),            # Trigger Source (0: CH1, 1: CH2, etc.)
        ("bTrigFilt", c_int),                # High Frequency Rejection Filter (1: ON, 0: OFF)
        ("nALT", c_short)                    # Alternate Trigger (1: Alternate, 0: Non-alternate)
    ]



class oscilloscope(object):
    def __init__(self, scopeid = 0):
        self.scopeid = c_ushort(scopeid)
        
        self.m_stControl = ControlData()
        self.m_relaycontrol = RELAYCONTROL()
        
        #------ defienitions--------
        self.TIME_DIV_INDEX = {
            0: ('2ns/Div', 2e-9),   1: ('5ns/Div', 5e-9),    2: ('10ns/Div', 10e-9),  
            3: ('20ns/Div', 20e-9),  4: ('50ns/Div', 50e-9),  5: ('100ns/Div', 100e-9),
            6: ('200ns/Div', 200e-9), 7: ('500ns/Div', 500e-9), 8: ('1us/Div', 1e-6),  
            9: ('2us/Div', 2e-6),    10: ('5us/Div', 5e-6),   11: ('10us/Div', 10e-6),
            12: ('20us/Div', 20e-6), 13: ('50us/Div', 50e-6), 14: ('100us/Div', 100e-6),  
            15: ('200us/Div', 200e-6), 16: ('500us/Div', 500e-6), 17: ('1ms/Div', 1e-3),  
            18: ('2ms/Div', 2e-3),   19: ('5ms/Div', 5e-3),   20: ('10ms/Div', 10e-3),
            21: ('20ms/Div', 20e-3), 22: ('50ms/Div', 50e-3), 23: ('100ms/Div', 100e-3),  
            24: ('200ms/Div', 200e-3), 25: ('500ms/Div', 500e-3), 26: ('1s/Div', 1),
            27: ('2s/Div', 2),       28: ('5s/Div', 5),       29: ('10s/Div', 10),  
            30: ('20s/Div', 20),     31: ('50s/Div', 50),     32: ('100s/Div', 100), 
            33: ('200s/Div', 200),   34: ('500s/Div', 500),   35: ('1000s/Div', 1000)
        }

        self.VOLT_DIV_INDEX = {
            0: ('2mV/Div', 2e-3, 16e-3),   1: ('5mV/Div', 5e-3, 40e-3),   2: ('10mV/Div', 10e-3, 80e-3),  
            3: ('20mV/Div', 20e-3, 160e-3), 4: ('50mV/Div', 50e-3, 400e-3), 5: ('100mV/Div', 100e-3, 800e-3),
            6: ('200mV/Div', 200e-3, 1.6),  7: ('500mV/Div', 500e-3, 4.0),  8: ('1V/Div', 1.0, 8.0),  
            9: ('2V/Div', 2.0, 16.0),      10: ('5V/Div', 5.0, 40.0),      11: ('10V/Div', 10.0, 80.0)
        }
        
        self.hthard_dll = WinDLL(os.path.join(dll_x64_path, 'HTHardDll.dll'))
        
        self.MAX_TIMEDIV_NUM = 36  # Total time division levels
        self.TIMEDIV_OFFSET = 2  # Time base offset

        self.DRIVERVERLEN = 8  # Must be even
        self.AUTOSET_TIME1 = 19
        self.AUTOSET_TIME2 = 18
        self.ZERO_START_VOLT = 5
        self.BUF_10K_LIMIT = None  # Undefined

        self.PI = 3.14159265358979323846
        self.BUF_4K_LEN = 0x1000
        self.BUF_3K_LEN = 0x0C00  # 3072
        self.BUF_8K_LEN = 0x2000
        self.BUF_16K_LEN = 0x4000
        self.BUF_32K_LEN = 0x8000
        self.BUF_64K_LEN = 0x10000

        self.BUF_INSERT_LEN = None  # BUF_72K_LEN is undefined

        self.DEF_READ_DATA_LEN = self.BUF_4K_LEN  # Default data read length
        self.DEF_DRAW_DATA_LEN = 2500  # Default data draw length

        self.MAX_INSERT_TIMEDIV = 6  # 200nS maximum interpolation for time division
        self.MAX_DOUBLE_TIMEDIV = self.MAX_INSERT_TIMEDIV
        self.MAX_SF_T_TIMEDIV = self.MAX_INSERT_TIMEDIV - 2  # Requires software-triggered time division
        self.MAX_SINE_TIMEDIV = 3  # Must use sine interpolation

        self.MIN_SCAN_TIMEDIV = 25  # Minimum time division for scan mode
        self.MIN_ROLL_TIMEDIV = 27  # Minimum time division for roll mode

        self.SINE_WAVE_LEN = 128  # Length of sine wave in the center window
        self.MAX_ETS_TIMEDIV = 3  # ETS maximum time division (0, 1, 2, 3)
        self.ETS_SAMPLING_100M = 0  # ETS 100M sampling

        #  Calibration
        self.NEW_CAL_LEVEL_LEN = 400  # Calibration level length

        # Vertical Settings
        self.CH1 = 0
        self.CH2 = 1
        self.CH3 = 2
        self.CH4 = 3

        self.MAX_CH_NUM = MAX_CH_NUM
        self.HORIZONTAL = self.MAX_CH_NUM  # Horizontal lever
        self.MATH = self.MAX_CH_NUM  # Vertical lever (CH1/CH2/CH3/CH4/MATH/REF)
        self.REF = self.MAX_CH_NUM + 1
        self.ALL_CH = self.MAX_CH_NUM + 2
        self.MIN_DATA = 0
        self.MAX_DATA = 255
        self.MID_DATA = 128
        self.MAX_VOLTDIV_NUM = 12

        # Display Modes
        self.YT = 0
        self.XY = 1
        self.YT_NORMAL = 0
        self.YT_SCAN = 1
        self.YT_ROLL = 2

        # Coupling Modes
        self.DC = 0
        self.AC = 1
        self.GND = 2
        
        # Trigger
        self.MAX_TRIGGER_SOURCE_NUM = self.MAX_CH_NUM + 2  # CH1/CH2/CH3/CH4/EXT/(EXT/10)
        self.MAX_ALT_TRIGGER_NUM = self.MAX_CH_NUM + 2  # CH1/CH2/CH3/CH4
        self.EXT = self.MAX_CH_NUM
        self.EXT10 = self.MAX_CH_NUM + 1

        # Trigger Types
        self.EDGE = 0
        self.PULSE = 1
        self.VIDEO = 2
        self.CAN = 3
        self.LIN = 4
        self.UART = 5
        self.SPI = 6
        self.IIC = 7

        self.FORCE = 0x80

        # Trigger Modes
        self.AUTO = 0
        self.NORMAL = 1
        self.SINGLE = 2

        # Edge Types
        self.RISE = 0
        self.FALL = 1
        
        self.OPEN_PEAK_COLLECTION = 1
        
        self.cal_data = None
        
        # ------settings-----
        self.nCHMode = 4
        self.m_ntimediv = 17
        self.m_nYTFormat = self.YT_NORMAL
        self.nTrigSource = self.CH1
        self.bCHEnable = [1, 1, 1, 1]
        self.nCHVoltDIV = [8, 11, 9, 9]
        self.nCHCoupling = [self.AC, self.DC, self.AC, self.AC]
        self.bCHBWLimit = [0, 0, 0, 0]
        self.nPos_channel = [128, 128, 128, 128]
        self.nSensitivity_trigger = 1
        self.m_nTriggerMode = self.PULSE
        self.m_nTriggerSlope = self.RISE
        self.m_nTriggerCouple = self.nCHCoupling[self.nTrigSource]  # DC:0 AC:1 2:Low frequency suppression 3:High frequency suppression
        self.m_nTriggerSweep = self.AUTO
        self.nStartControl_collect = self.AUTO
    
        self.nPeak = self.OPEN_PEAK_COLLECTION
        
        print(f'TIME_DIV {self.TIME_DIV_INDEX[self.m_ntimediv]}')
        
        
    def set_m_stControl(self):
        self.m_stControl.nCHSet = 0x0F
        self.m_stControl.nTimeDIV = self.m_ntimediv
        self.m_stControl.nTriggerSource = self.CH3
        self.m_stControl.nHTriggerPos = 50
        self.m_stControl.nVTriggerPos = 128
        self.m_stControl.nBufferLen = self.BUF_8K_LEN
        self.m_stControl.nReadDataLen = self.m_stControl.nBufferLen
        self.m_stControl.nAlreadyReadLen = self.m_stControl.nBufferLen
        self.m_stControl.nALT = 0
        self.m_stControl.nFPGAVersion = 0xa000
    def set_m_relaycontrol(self):
        for i in range(MAX_CH_NUM):
            self.m_relaycontrol.bCHEnable[i] = self.bCHEnable[i]
            self.m_relaycontrol.nCHVoltDIV[i] = self.nCHVoltDIV[i]
            self.m_relaycontrol.nCHCoupling[i] = self.nCHCoupling[i]
            self.m_relaycontrol.bCHBWLimit[i] = self.bCHBWLimit[i]
        self.m_relaycontrol.nTrigSource = self.nTrigSource
        self.m_relaycontrol.bTrigFilt = 0
        self.m_relaycontrol.nALT = 0
  
    def search_device(self, return_buffer_size = 32):
        self.ht_hard_dll.dsoHTSearchDevice.argtypes = [POINTER(c_short)]
        self.ht_hard_dll.dsoHTSearchDevice.restype = c_uint
        device_info = (c_short * return_buffer_size)()
        result = self.ht_hard_dll.dsoHTSearchDevice(device_info)
        if result == 0:
            print(f'Founded device(s):')
        elif result == 1: print('No device found')
        return device_info

    def dsoHTDeviceConnect(self, scopeid = 0):
        self.scopeid = scopeid
        self.hthard_dll.dsoHTDeviceConnect.argtypes = [c_uint]
        self.hthard_dll.dsoHTDeviceConnect.restype = c_uint
        rr_con = self.hthard_dll.dsoHTDeviceConnect(self.scopeid)
        if rr_con: print(f'dv{self.scopeid} Connected successfully!')
        else: 
            print('FAIL: dsoHTDeviceConnect')
            exit()
        return rr_con
            
    def dsoInitHard(self):
        self.hthard_dll.dsoInitHard.argtypes = [c_ushort]
        self.hthard_dll.dsoInitHard.restype = c_uint
        retval = self.hthard_dll.dsoInitHard(self.scopeid)
        if retval == 0:
            return True
        else:
            print(f'dsoInitHard retval:  {retval}')
            return False

    def setup_dso_cal_level(self):
        if self.cal_data is None:
            self.cal_data = (c_short * self.NEW_CAL_LEVEL_LEN)()
        retval = self.hthard_dll.dsoHTReadCalibrationData(self.scopeid, byref(self.cal_data), c_short(self.NEW_CAL_LEVEL_LEN))
        
        if retval == 0:
            return True
        else:
            print(f'setup_dso_cal_level retval:  {retval}')
            return False

    def dsoHTADCCHModGain(self):
        '''
        parram function; scopeid [nCHMode]
        '''
        self.hthard_dll.dsoHTADCCHModGain.argtypes = [c_ushort, c_int]
        self.hthard_dll.dsoHTADCCHModGain.restype = c_uint
        retval = self.hthard_dll.dsoHTADCCHModGain(self.scopeid, self.nCHMode)
        if retval == 0:
            return True
        else:
            print(f'dsoHTADCCHModGain retval:  {retval}')
            return False

    # nYTFormat - mode of horizontal format 0-normal, 1-Scan, 2-Roll
    def dsoHTSetSampleRate(self):
        '''
            parram function; scopeid [nYTFormat, relay_con, CONTROL]
        '''
        self.hthard_dll.dsoHTSetSampleRate.argtypes = [c_ushort, c_ushort, POINTER(RELAYCONTROL), POINTER(ControlData)]
        self.hthard_dll.dsoHTSetSampleRate.restype = c_uint16
        retval = self.hthard_dll.dsoHTSetSampleRate(self.scopeid, self.m_nYTFormat, byref(self.m_relaycontrol), byref(self.m_stControl))
        if retval == 0:
            return True
        else:
            print(f'dsoHTSetSampleRate retval:  {retval}')
            return False

    def dsoHTSetCHAndTrigger(self):
        '''
            parram function; scopeid [relay_con, nTimeDIV]
        '''
        self.hthard_dll.dsoHTSetCHAndTrigger.argtypes = [c_ushort, POINTER(RELAYCONTROL), c_ushort]
        self.hthard_dll.dsoHTSetCHAndTrigger.restype = c_uint16
        retval = self.hthard_dll.dsoHTSetCHAndTrigger(self.scopeid, byref(self.m_relaycontrol), self.m_ntimediv)
        if retval == 0:
            return True
        else:
            print(f'dsoHTSetCHAndTrigger retval:  {retval}')
            return False

    def dsoHTSetRamAndTriggerControl(self):
        '''
            parram function; scopeid [nTimeDiv, nCHset, nTrigerSource, nPeak]
        '''
        self.hthard_dll.dsoHTSetRamAndTrigerControl.argtypes = [c_ushort, c_short, c_short, c_short, c_int]
        self.hthard_dll.dsoHTSetRamAndTrigerControl.restype = c_uint16
        retval = self.hthard_dll.dsoHTSetRamAndTrigerControl(self.scopeid, self.m_ntimediv, self.m_stControl.nCHSet, self.nTrigSource, self.nPeak)
        if retval == 0:
            return True
        else:
            print(f'dsoHTSetRamAndTrigerControl retval:  {retval}')
            return False

    # TODO: added CHLevel(calibration data to dsoHTSetCHPos)
    # def dsoHTSetCHPos(self, CHLevel, nVoltDIV, nPos, nCH, nCHMode):
    #     print(CHLevel, nVoltDIV, nPos, nCH, nCHMode)
    #     self.ht_hard_dll.dsoHTSetCHPos.argtypes = [c_ushort, c_short, c_short, c_short, c_short, c_int]
    #     self.ht_hard_dll.dsoHTSetCHPos.restype = c_uint16
    #     retval = self.ht_hard_dll.dsoHTSetCHPos(self.scopeid, CHLevel, nVoltDIV, nPos, nCH, nCHMode)
    #     if retval == 0:
    #         return True
    #     else:
    #         print(f'dsoHTSetCHPos retval:  {retval}')
    #         return False
    
    def dsoHTSetCHPos(self):
        """
        Sets the channel position for each oscilloscope channel.

        Parameters:
        - Uses `self.scopeid` (device index).
        - Uses `self.m_relaycontrol.nCHVoltDIV[n_ch]` (voltage division for each channel).
        - Uses `self.nPos_channel[n_ch]` (vertical position for each channel).
        - Uses `self.nCHMode` (channel mode).

        Returns:
        - True if all channels succeed.
        - False if any channel fails.
        """
        self.hthard_dll.dsoHTSetCHPos.argtypes = [c_ushort, c_ushort, c_ushort, c_ushort, c_ushort]
        self.hthard_dll.dsoHTSetCHPos.restype = c_ushort
        
        nPos_channel_ushort = (c_ushort * self.MAX_CH_NUM)()
        for num in range(self.MAX_CH_NUM):
            nPos_channel_ushort[num] = self.nPos_channel[num]
        
        for n_ch in range(self.MAX_CH_NUM): 
            retval = self.hthard_dll.dsoHTSetCHPos(
                c_ushort(self.scopeid), 
                c_ushort(self.m_relaycontrol.nCHVoltDIV[n_ch]),  # Pass single voltage division value
                c_ushort(self.nPos_channel[n_ch]),  # Pass single position value
                c_ushort(n_ch), 
                c_ushort(self.nCHMode)
            )
            print(f'dsoHTSetCHPos retval:  {retval} of Channel {n_ch}')

    
    def dsoHTSetAmpCalibrate(self):
        '''
            param function; scopeid [nCHSet, nTimeDIV, nVoltDIV, pCHpos]
        '''
        
        self.hthard_dll.dsoHTSetAmpCalibrate.argtypes = [c_ushort, c_ushort, c_ushort, POINTER(c_ushort), POINTER(c_ushort)]
        self.hthard_dll.dsoHTSetAmpCalibrate.restype = c_ushort
        
        nPos_channel_ushort = (c_ushort * self.MAX_CH_NUM)()
        for num in range(self.MAX_CH_NUM):
            nPos_channel_ushort[num] = self.nPos_channel[num]
        retval = self.hthard_dll.dsoHTSetAmpCalibrate(c_ushort(self.scopeid), c_ushort(self.m_stControl.nCHSet), c_ushort(self.m_ntimediv),
                                                       self.m_relaycontrol.nCHVoltDIV, nPos_channel_ushort)
        if retval == 0:
            return True
        else:
            print(f'dsoHTSetAmpCalibrate retval:  {retval}')
            return False

    def dsoHTSetVTriggerLevel(self):
        '''
            param function; scopeid [nPos, nSensitivity]
        '''
        self.hthard_dll.dsoHTSetVTriggerLevel.argtypes = [c_ushort, c_short, c_int]
        self.hthard_dll.dsoHTSetVTriggerLevel.restype = c_uint16
        retval = self.hthard_dll.dsoHTSetVTriggerLevel(self.scopeid, self.m_stControl.nVTriggerPos, 
                                                        self.nSensitivity_trigger)
        if retval == 0:
            return True
        else:
            print(f'dsoHTSetVTriggerLevel retval:  {retval}')
            return False

    def dsoHTSetTrigerMode(self):
        '''
            param function; scopeid [nTriggerMode, nTriggerSlop, nTriggerCouple]
        '''
        self.hthard_dll.dsoHTSetTrigerMode.argtypes = [c_ushort, c_ushort, c_short, c_int]
        self.hthard_dll.dsoHTSetTrigerMode.restype = c_uint16
        retval = self.hthard_dll.dsoHTSetTrigerMode(self.scopeid, self.m_nTriggerMode, self.m_nTriggerSlope, self.m_nTriggerCouple)
        if retval == 0:
            return True
        else:
            print(f'dsoHTSetTrigerMode retval:  {retval}')
            return False

    def dsoHTSetCHAndTriggerVB(self):
        """
        Sets channel configuration and trigger settings.

        Parameters:
        - Uses `self.scopeid` (device index).
        - Uses `self.m_relaycontrol.bCHEnable` (channel enable array).
        - Uses `self.m_relaycontrol.nCHVoltDIV` (voltage division array).
        - Uses `self.m_relaycontrol.nCHCoupling` (coupling mode array).
        - Uses `self.m_relaycontrol.bCHBWLimit` (bandwidth limit array).
        - Uses `self.m_stControl.nTriggerSource` (trigger source).
        - Uses `self.m_relaycontrol.bTrigFilt` (trigger filter).
        - Uses `self.m_relaycontrol.nALT` (ALT mode).
        - Uses `self.m_ntimediv` (time division index).

        Returns:
        - True if configuration succeeds.
        - False if configuration fails.
        """
        self.hthard_dll.dsoHTSetCHAndTriggerVB.argtypes = [
            c_ushort,              # nDeviceIndex
            POINTER(c_short),      # pCHEnable (pointer to array)
            POINTER(c_short),      # pCHVoltDIV (pointer to array)
            POINTER(c_short),      # pCHCoupling (pointer to array)
            POINTER(c_short),      # pCHBWLimit (pointer to array)
            c_ushort,              # nTriggerSource
            c_ushort,              # nTriggerFilt
            c_ushort,              # nALT
            c_ushort               # nTimeDIV
        ]
        self.hthard_dll.dsoHTSetCHAndTriggerVB.restype = c_ushort  
        
        bCHEnable_array = (c_short * len(self.m_relaycontrol.bCHEnable))(*self.m_relaycontrol.bCHEnable)
        nCHVoltDIV_array = (c_short * len(self.m_relaycontrol.nCHVoltDIV))(*self.m_relaycontrol.nCHVoltDIV)
        nCHCoupling_array = (c_short * len(self.m_relaycontrol.nCHCoupling))(*self.m_relaycontrol.nCHCoupling)
        bCHBWLimit_array = (c_short * len(self.m_relaycontrol.bCHBWLimit))(*self.m_relaycontrol.bCHBWLimit)
        

        retval = self.hthard_dll.dsoHTSetCHAndTriggerVB(
            c_ushort(self.scopeid),
            bCHEnable_array,
            nCHVoltDIV_array,
            nCHCoupling_array,
            bCHBWLimit_array,
            c_ushort(self.m_stControl.nTriggerSource),
            c_ushort(self.m_relaycontrol.bTrigFilt),
            c_ushort(self.m_relaycontrol.nALT),
            c_ushort(self.m_ntimediv)
        )
        
        if retval == 0:
            return True
        else:
            print(f'dsoHTSetCHAndTriggerVB retval:  {retval}')
            return False
    
    def dsoHTStartCollectData(self):
        '''
            param function; scopeid [ nStartControl]
        '''
        self.hthard_dll.dsoHTStartCollectData.argtypes = [c_ushort, c_short]
        self.hthard_dll.dsoHTStartCollectData.restype = c_uint
        retval = self.hthard_dll.dsoHTStartCollectData(self.scopeid, self.nStartControl_collect)
        if retval == 0:
            return True
        else:
            print(f'dsoHTSetCHAndTriggerVB retval:  {retval}')
            return False
    
    def dsoHTGetState(self):
        self.hthard_dll.dsoHTGetState.argtypes = [c_ushort]
        self.hthard_dll.dsoHTGetState.restype = c_ushort
        state = self.hthard_dll.dsoHTGetState(self.scopeid)
        
        is_triggered = bool(state & 0x01)
        is_data_finished = bool(state & 0x02)
        return is_triggered, is_data_finished

    def dsoHTGetData(self):
        '''
            param function; scopeid [ pCH1Data_buffer, pCH2Data_buffer, pCH3Data_buffer, pCH4Data_buffer, ControlData]
        '''
        pReadData = [(c_ushort * scope.m_stControl.nBufferLen)() for _ in range(scope.MAX_CH_NUM)]
        # for i in range(scope.MAX_CH_NUM):
        #     pReadData[i] = (c_ushort * scope.m_stControl.nBufferLen)()
        

        self.hthard_dll.dsoHTGetData.argtypes = [c_ushort, POINTER(c_ushort), POINTER(c_ushort), POINTER(c_ushort), POINTER(c_ushort), POINTER(ControlData)]
        self.hthard_dll.dsoHTGetData.restype = c_ushort
        retval = self.hthard_dll.dsoHTGetData(self.scopeid, pReadData[self.CH1], pReadData[self.CH2], pReadData[self.CH3], pReadData[self.CH4], byref(self.m_stControl))
        
        print(f'dsoHTSetCHAndTriggerVB retval:  {retval}')
        return True, pReadData



class ht_OPERATION():
    def __init__(self):
        self.volt_continuous_data =  [[],[],[],[]]
        self.position_continuous_collect = []
        self.JSON_DATA_PATH = os.path.join(base_filepath, 'data.json')
        self.NPZ_DATA_PATH = os.path.join(base_filepath, 'data.npz')
        self.SAVE_SIZE = 20000
        self.process_data_volts = 0.15
        
    def Init(self):
        scope.dsoHTDeviceConnect()
        scope.set_m_stControl()
        scope.set_m_relaycontrol()
        scope.dsoHTDeviceConnect()
        scope.dsoInitHard()
        scope.dsoHTADCCHModGain()
        scope.dsoHTSetAmpCalibrate()
        scope.dsoHTSetSampleRate()
        scope.dsoHTSetCHAndTrigger()
        scope.dsoHTSetRamAndTriggerControl()
        scope.dsoHTSetCHPos()
        scope.dsoHTSetVTriggerLevel()
        scope.dsoHTSetTrigerMode()
        
        scope.dsoHTSetCHAndTriggerVB()
        # scope.dsoHTSetRamAndTrigerControl()

    def retrieve_data(self, collection_times = 10):
        loop_cycles = 0
        while loop_cycles < collection_times:
            is_triggered, is_data_finished = scope.dsoHTGetState()
            while not is_data_finished:
                trig_d, is_data_finished = scope.dsoHTGetState()
                if is_data_finished:
                    sta, pReadData = scope.dsoHTGetData()
                    
                    
                    # discard 1st batch of data
                    if loop_cycles == 0: pass
                    else: self.extend_continuous_data(pReadData)
                    
                    
                    loop_cycles += 1
                    oscilloscope().dsoHTStartCollectData()
                print(loop_cycles)
        return pReadData

    def convert_read_data(self, input_data, scale, scale_points=32.0, offset=128):
        """
        Converts oscilloscope raw data into true analog voltage values.
        
        Parameters:
        - input_data (list/array): Raw oscilloscope data (ctypes or integer list).
        - scale (float): Voltage scale (Volt/Div).
        - scale_points (float): Number of divisions per step (default 32).
        - offset (int): ADC mid-range offset (default 128 for 8-bit ADC).

        Returns:
        - np.array: Converted analog voltage values.
        """
        if isinstance(input_data[0], _SimpleCData):
            input_data = np.array([j.value for j in input_data])
        else:
            input_data = np.array(input_data, dtype=np.float32)
        point_div = scale / scale_points
        return (input_data - offset) * point_div
    
    def save_json_extend(self, newdata: dict):
        '''pram newdata = {'ultrasonic': list, 'sig': list, 'fireposiiton' tuple:list}'''
        if os.path.exists(self.JSON_DATA_PATH):
            try:
                with open(self.JSON_DATA_PATH, 'r') as f:
                    old_data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                old_data = {}  # corrupted start fresh
        else: old_data = {}

        for key, new_values in newdata.items():
            if key in old_data and isinstance(old_data[key], list):
                old_data[key].extend(new_values)
            else: old_data[key] = new_values
        with open(self.JSON_DATA_PATH, 'w') as f:
            json.dump(old_data, f, indent=4)  
            
    def save_npz_extend(self, newdata: dict):
        """
        Extends and saves data in `.npz` format.
        
        Parameters:
        - newdata (dict): New data to extend existing `.npz` file.
                        Example: {'ultrasonic': list, 'sig': list, 'fireposition': list}
        """
        # Define `.npz` file path
        npz_path = self.NPZ_DATA_PATH
        if os.path.exists(npz_path):
            try:
                old_data = np.load(npz_path, allow_pickle=True)
                old_data_dict = {key: old_data[key].tolist() for key in old_data.files}
            except Exception as e:
                print(f"Error loading existing data: {e}")
                old_data_dict = {}  # Start fresh if file is corrupted
        else:
            old_data_dict = {}

        # Extend or initialize new data
        for key, new_values in newdata.items():
            if isinstance(new_values, np.ndarray):
                new_values = new_values.tolist()
            if key in old_data_dict:
                old_data_dict[key].extend(new_values)
            else: old_data_dict[key] = new_values
            
        np.savez(npz_path, **{k: np.array(v, dtype=np.float32) for k, v in old_data_dict.items()})
    
    def extend_continuous_data(self, pReadData):
        for num_channel in range(MAX_CH_NUM):
            volt_div_channel = scope.VOLT_DIV_INDEX[scope.nCHVoltDIV[num_channel]][1]
            volts_data = self.convert_read_data(pReadData[num_channel], volt_div_channel)
            self.volt_continuous_data[num_channel].extend(volts_data)
    
    def process_data(self, ultrasonic, sig = None):
        ultrasonic = np.array(ultrasonic)
        
        significant_indices = np.where(np.abs(ultrasonic) > self.process_data_volts)[0] # > 0.01V
        if len(significant_indices) > 0:
            start_idx = significant_indices[0]  # First occurrence above 0.07V
            end_idx = significant_indices[-1]   # Last occurrence above 0.07V

            significant_data = ultrasonic[start_idx:end_idx + 1]
        else: significant_data = np.array([])  # No significant data found
            
        if significant_data.shape[0] > self.SAVE_SIZE: trimmed_data = significant_data[:self.SAVE_SIZE] # trim
        elif significant_data.shape[0] < self.SAVE_SIZE: # smaller add padding
            trimmed_data = np.pad(significant_data, (0, self.SAVE_SIZE - significant_data.shape[0]), mode='constant')
        else:
            trimmed_data = significant_data
            
        return trimmed_data
    
    def save_continuousDat_to_npz(self) :    
        print("Saving Data to npz file") 
        cropped_data_peak = self.process_data(self.volt_continuous_data[scope.CH1])
        
             
        npz_df = {'ultrasonic': np.array(cropped_data_peak), #save data
                   'posfire': np.array(self.position_continuous_collect, dtype= np.int8)}
        self.save_npz_extend(npz_df)
        
        
        self.volt_continuous_data = [[], [], [], []] # reset var after saveded   
        self.position_continuous_collect = []

    def test_collect_plot(self, mat_plot = True):
        ReadData = self.retrieve_data(collection_times=20)
        channel = scope.CH1
        voltages = self.convert_read_data(ReadData[channel], scope.VOLT_DIV_INDEX[scope.nCHVoltDIV[channel]][1])
        fig, ax = plt.subplots(nrows= 2, ncols= 1)
        
        if mat_plot == True:
            ax[0].plot(ReadData[channel])
            ax[0].legend(['raw'])
            ax[1].plot(voltages)
            ax[1].legend(['processed'])
            ax[1].set_ylim(-scope.VOLT_DIV_INDEX[scope.nCHVoltDIV[channel]][1], scope.VOLT_DIV_INDEX[scope.nCHVoltDIV[channel]][1])
            plt.show()
            
            fig, ax = plt.subplots(nrows= 2, ncols= 1)
            ax[0].plot(operation.volt_continuous_data[channel])
            ax[0].set_ylim(-scope.VOLT_DIV_INDEX[scope.nCHVoltDIV[channel]][1], scope.VOLT_DIV_INDEX[scope.nCHVoltDIV[channel]][1])
            ax[1].plot(operation.volt_continuous_data[scope.CH2])
            ax[1].set_ylim(-scope.VOLT_DIV_INDEX[scope.nCHVoltDIV[scope.CH2]][1], scope.VOLT_DIV_INDEX[scope.nCHVoltDIV[scope.CH2]][1])
            plt.show()





class interface(object):
    def __init__(self):
        self.npz_filedata_path = os.path.join(base_filepath, 'data.npz')
        self.AVERAGE_DISTANCE_STEP = 0.7
                               
    def zigzag_coordinates(self, width, height ):
        """
        Generates zigzag coordinates in a 2D grid.
        
        - Moves **right** along x (0 → width-1).
        - Moves **left** along x (width-1 → 0) in the next row.
        
        :param width: Number of x points (horizontal steps)
        :param height: Number of y points (vertical levels)
        :return: List of (x, y) coordinates in zigzag order
        """
        width = width + 1
        height = height + 1
        coordinates = []
        for y in range(height):
            if y % 2 == 0: row = [(x, y) for x in range(width)]
            else: row = [(x, y) for x in range(width - 1, -1, -1)]
            coordinates.extend(row)
            
            
        # add position to home (0,0)
        xdis_home, ydis_home = coordinates[-1][0] - coordinates[0][0], coordinates[-1][1] - coordinates[0][1]
        x_step = [(x, coordinates[-1][1]) for x in range(xdis_home-1, 0-1, -1)]
        coordinates.extend(x_step)
        y_step = [(coordinates[-1][0], y) for y in range(ydis_home-1, 0-1, -1)] 
        coordinates.extend(y_step)
        return coordinates
    def backandforth_pattern(self, width, height, continue_from_previous):
        width+=1
        height+=1
        coordinates = []
        for y in range(height):
            x_steps = [(x, y, True, False) for x in range(width)]
            coordinates.extend(x_steps)
            x_steps_reverse = [(x, y, False, False) for x in range(width-1, 0, -1)]
            coordinates.extend(x_steps_reverse)

        # return to home
        xdis_home, ydis_home = coordinates[-1][0] - coordinates[0][0], coordinates[-1][1] - coordinates[0][1]
        x_step = [(x, coordinates[-1][1], False, True) for x in range(xdis_home-1, 0-1, -1)]
        coordinates.extend(x_step)
        y_step = [(coordinates[-1][0], y, False, True) for y in range(ydis_home-1, 0-1, -1)] 
        coordinates.extend(y_step)

        if continue_from_previous:
            self.trim_coordinates(coordinates)
        
        return coordinates
    
    def backandforth_pattern_each(self, width, height, continue_from_previous, steps_before_data_collection = 1):
        width+=1
        height+=1
        coordinates = []
        for y in range(height):
            x_steps = [(x, y, bool(x % steps_before_data_collection == 0 and y % steps_before_data_collection == 0), False) for x in range(width)]
            coordinates.extend(x_steps)
            x_steps_reverse = [(x, y, False, False) for x in range(width-1, 0, -1)]
            coordinates.extend(x_steps_reverse)

        # return to home
        xdis_home, ydis_home = coordinates[-1][0] - coordinates[0][0], coordinates[-1][1] - coordinates[0][1]
        x_step = [(x, coordinates[-1][1], False, True) for x in range(xdis_home-1, 0-1, -1)]
        coordinates.extend(x_step)
        y_step = [(coordinates[-1][0], y, False, True) for y in range(ydis_home-1, 0-1, -1)] 
        coordinates.extend(y_step)

        if continue_from_previous:
            self.trim_coordinates(coordinates)
        
        return coordinates

    def trim_coordinates(self, coordinates, continue_from_previous=True):
        """
        Trims the `coordinates` list by removing all values before the previously saved position.

        Parameters:
        - coordinates (list of tuples): List of (x, y) positions.
        - continue_from_previous (bool): Whether to continue from the last saved position.

        Returns:
        - list: Updated coordinates after trimming.
        """
        if continue_from_previous:
                # Load the last saved position
                saved_data = np.load(self.npz_filedata_path, allow_pickle=True)
                previously_saved_pos = saved_data['posfire'][-1]

                print(f"Previously saved position: {previously_saved_pos}")

                # Find the index of the last saved position in coordinates
                # print(previously_saved_pos, coordinates )
                if tuple(previously_saved_pos) in [(x, y) for x, y, fire, return_pos in coordinates]:
                    index = [(x, y) for x, y, fire, return_pos in coordinates].index(tuple(previously_saved_pos))
                    print(f"Found position at index: {index}, trimming before this index.")
                    coordinates = coordinates[index:]  # Keep values from that index onward
                else:
                    print("⚠️ Previously saved position not found in coordinates. No trimming applied.")
        return coordinates
     
    def move_position(self, width, height, fire_steps = False, steps = 1, mat_plot = True, continue_from_previous = False):
        positions = self.backandforth_pattern(width, height, continue_from_previous)
        positions = self.backandforth_pattern_each(width, height, continue_from_previous, steps_before_data_collection = 4)

        
        leonado.read_write_string(f'XHOME')
        time.sleep(6)
        leonado.read_write_string(f'MOVE 0 -10')
        time.sleep(5)
        leonado.read_write_string(f'HOME')
        
        for x, y, fire, ret in positions:
            leonado.read_write_string(f'MOVE {x} {y}')
            if fire == True and fire_steps == True: # fire laser
                leonado.read_write_string(f'FIREL000 1')
                scope.dsoHTStartCollectData()
                operation.test_collect_plot(mat_plot = mat_plot)
                
                operation.position_continuous_collect.append((x, y)) # log firing position
                # if x == width: operation.save_continuousDat_to_npz() # save data at last width
                operation.save_continuousDat_to_npz()
                
            time.sleep(0.5)   
            if x == 0 and ret == False: # return to x=0 each y step
                leonado.read_write_string(f'XHOME')
                time.sleep(3)

        # home        
        leonado.read_write_string(f'XHOME') 
        time.sleep(5)
        # fig, ax = plt.subplots(nrows= 2, ncols= 1)
        # ax[0].plot(operation.volt_continuous_data[scope.CH1])
        # ax[0].set_ylim(-scope.VOLT_DIV_INDEX[scope.nCHVoltDIV[scope.CH1]][1], scope.VOLT_DIV_INDEX[scope.nCHVoltDIV[scope.CH1]][1])
        # ax[1].plot(operation.volt_continuous_data[scope.CH2])
        # ax[1].set_ylim(-scope.VOLT_DIV_INDEX[scope.nCHVoltDIV[scope.CH2]][1], scope.VOLT_DIV_INDEX[scope.nCHVoltDIV[scope.CH2]][1])
        # plt.show()
    
    def move_and_collect_sensor_data(self, x, y, collection_times = 20):
        x+=1
        y+=1
        for pos_y in range(y):
            coordinates = [(pos_x, pos_y) for pos_x in range(x)] # go to position
        for x,y in coordinates:
            leonado.read_write_string(f"MOVE {x} {y}")
            time.sleep(0.5)

        # fire
        leonado.read_write_string(f"FIREL000 1")
        scope.dsoHTStartCollectData() # start collection
        ReadData = operation.retrieve_data(collection_times = collection_times)
        channel = scope.CH1
        voltages = operation.convert_read_data(ReadData[channel], scope.VOLT_DIV_INDEX[scope.nCHVoltDIV[channel]][1])

        # save voltages npz
        operation.save_npz_extend({"sensor_data_noisy": voltages})






scope = oscilloscope()
operation = ht_OPERATION()

if __name__ == "__main__":
    scope.dsoHTGetState()
    operation.Init()
    # interface().move_position(20, 20, 
    #                           fire_steps = True, 
    #                           mat_plot=False, 
    #                           continue_from_previous = False)
    interface().move_and_collect_sensor_data(20, 20, 20)


#TODO: higher frequency for laser
#TODO: update position of each firing
# resolution change steps_before_data_collection
