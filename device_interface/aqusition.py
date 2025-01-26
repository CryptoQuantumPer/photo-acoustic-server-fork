import ctypes
from ctypes import c_short, POINTER, c_uint, c_uint16, c_uint32, c_bool
import os, time
import platform
from device_interface.hantek_acqusition import search_device, connect_device, dsoInitHard, dsoHTADCCHModGain, dsoHTSetSampleRate, dsoHTSetCHAndTrigger, dsoHTSetRamAndTrigerControl, dsoHTSetCHPos, dsoHTSetVTriggerLevel, dsoHTSetTrigerMode, dsoHTStartCollectData, dsoHTGetState, dsoHTGetData
from device_interface.hantek_acqusition import relay_control, control_data


dll_x64_path = os.path.join(os.getcwd(), 'device_interface', 'HT6004BX_SDK', 'DLL', 'x64')
ht_hard_dll = ctypes.WinDLL(os.path.join(dll_x64_path, 'HTHardDll.dll'))

device_index = 0


# init hantek
search_device()
connect_device(device_index)
dsoInitHard(device_index)
dsoHTADCCHModGain(device_index, nCHMode= 4)
dsoHTSetSampleRate(device_index, nYTFormat=1, RELAYCONTROL=relay_control, CONTROL=control_data)
dsoHTSetCHAndTrigger(device_index, RELAYCONTROL= relay_control, nTimeDIV= control_data.nTimeDIV)
dsoHTSetRamAndTrigerControl(device_index, nTimeDiv=control_data.nTimeDIV, nCHset=control_data.nCHSet, nTrigerSource=control_data.nTriggerSource, nPeak=0)
for i in range(4):
    dsoHTSetCHPos(device_index, nVoltDIV=relay_control.nCHVoltDIV[i], nPos=128, nCH=i, nCHMode=relay_control.nCHCoupling[i])

# nPeak???, nCHMode ???

# ค่อยว่ากันนันนะคนไทย 
dsoHTSetVTriggerLevel(device_index, nPos=128, nSensitivity=1)
dsoHTSetTrigerMode(device_index, nTriggerMode=0, nTriggerSlop=0, nTriggerCouple=0)


continuous_data_CH1 : list = []
while True:
    dsoHTStartCollectData(device_index, nStartControl=0)
    if dsoHTGetState(device_index): 
        pCH1DATA, pCH2DATA, pCH3DATA, pCH4DATA = (c_uint16 * 4096)(), (c_uint16 * 4096)(), (c_uint16 * 4096)(), (c_uint16 * 4096)()
        dsoHTGetData(device_index, pCH1DATA, pCH2DATA, pCH3DATA, pCH4DATA, control_data)
        
        # record CH1 when CH2 is triggered
        if 1 in list(pCH2DATA):
            continuous_data_CH1.extend(list(pCH1DATA))
        else: pass
       