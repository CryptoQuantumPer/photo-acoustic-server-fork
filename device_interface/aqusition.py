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